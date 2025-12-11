from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from .models import Product, StoreSettings, LowStockAlert
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

def check_and_send_stock_alerts():
    """
    Checks for products with low stock and sends daily reminders.
    
    Logic:
    1. Find products that are currently low stock (stock <= threshold)
    2. Create/update LowStockAlert records
    3. Send email reminders if:
       - First alert: send immediately
       - Subsequent reminders: send every 24 hours
    """
    
    # Get all products that are low stock
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=models.F('low_stock_threshold')
    )
    
    if not low_stock_products.exists():
        return 0
    
    store_name = "Inventory System"
    try:
        store_settings = StoreSettings.objects.first()
        if store_settings:
            store_name = store_settings.store_name
    except:
        pass
    
    sent_count = 0
    current_time = timezone.now()
    
    # Get recipient email(s) - admin or superusers
    recipients = get_alert_recipients()
    if not recipients:
        print("No recipients configured for stock alerts.")
        return 0
    
    for product in low_stock_products:
        # Get or create alert record
        alert, created = LowStockAlert.objects.get_or_create(product=product)
        
        # Check if we should send an email (first alert or 24+ hours since last)
        should_send_email = created or (
            current_time - alert.last_alert_sent >= timedelta(days=1)
        )
        
        if should_send_email and alert.is_active:
            # Send email
            subject = f"⚠️ LOW STOCK ALERT: {product.name} - {store_name}"
            message = f"""
Hello,

We're writing to inform you that the following product is running low on stock:

Product: {product.name}
Current Stock: {product.stock_quantity} units
Low Stock Threshold: {product.low_stock_threshold} units
Stock Alert #{alert.reminder_count + 1}

Please arrange to restock this item as soon as possible to avoid stockouts.

Store: {store_name}
Alert Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}

---
This is an automated low stock reminder. If stock has been replenished, this alert will automatically stop.
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipients,
                    fail_silently=False,
                )
                
                # Update alert record
                alert.reminder_count += 1
                alert.last_alert_sent = current_time
                alert.save()
                
                sent_count += 1
                print(f"✓ Sent low stock alert for {product.name}")
                
            except Exception as e:
                print(f"✗ Failed to send alert for {product.name}: {e}")
        
        # If stock is no longer low, deactivate the alert
        if product.stock_quantity > product.low_stock_threshold:
            alert.is_active = False
            alert.save()
            print(f"✓ Deactivated alert for {product.name} - stock replenished")
    
    if sent_count > 0:
        print(f"\n📧 Sent {sent_count} low stock alert(s)")
    
    return sent_count


def get_alert_recipients():
    """Get list of email addresses to send low stock alerts to."""
    recipients = []
    
    # Try to get from settings first
    if hasattr(settings, 'STOCK_ALERT_EMAIL'):
        recipients = settings.STOCK_ALERT_EMAIL
        if isinstance(recipients, str):
            recipients = [recipients]
    
    # Fallback to superusers
    if not recipients:
        superusers = User.objects.filter(is_superuser=True, email__isnull=False).exclude(email='')
        recipients = list(superusers.values_list('email', flat=True))
    
    # Final fallback
    if not recipients and hasattr(settings, 'DEFAULT_ADMIN_EMAIL'):
        recipients = [settings.DEFAULT_ADMIN_EMAIL]
    
    return recipients

