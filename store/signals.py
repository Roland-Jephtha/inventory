from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Product, LowStockAlert
from .services import get_alert_recipients
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Product)
def check_stock_level_on_save(sender, instance, created, **kwargs):
    """
    Checks if product stock has fallen below threshold and sends alert if needed.
    Also deactivates alerts if stock has been replenished.
    """
    if instance.is_low_stock:
        # Stock is low - create alert if needed and send email
        alert, created = LowStockAlert.objects.get_or_create(product=instance)
        
        # Send email if first alert or 24+ hours since last alert
        should_send = created or (timezone.now() - alert.last_alert_sent >= timedelta(days=1))
        
        if should_send and alert.is_active:
            recipients = get_alert_recipients()
            if recipients:
                try:
                    subject = f"⚠️ LOW STOCK ALERT: {instance.name}"
                    message = f"""
Your product '{instance.name}' is running low on stock.

Current Stock: {instance.stock_quantity} units
Low Stock Threshold: {instance.low_stock_threshold} units

Please restock this item.
                    """
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)
                    alert.reminder_count += 1
                    alert.last_alert_sent = timezone.now()
                    alert.save()
                except Exception as e:
                    print(f"Error sending stock alert: {e}")
    else:
        # Stock is normal - deactivate alert if it exists
        try:
            alert = LowStockAlert.objects.get(product=instance)
            if alert.is_active:
                alert.is_active = False
                alert.save()
        except LowStockAlert.DoesNotExist:
            pass

