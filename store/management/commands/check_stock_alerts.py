from django.core.management.base import BaseCommand
from store.services import check_and_send_stock_alerts

class Command(BaseCommand):
    help = 'Checks for low stock products and sends email alerts'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking for low stock products...")
        
        count = check_and_send_stock_alerts()
        
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f"Successfully sent alert for {count} products."))
        else:
            self.stdout.write("No new low stock alerts to send.")
