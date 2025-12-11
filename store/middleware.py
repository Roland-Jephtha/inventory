from django.utils.deprecation import MiddlewareMixin
from .services import check_and_send_stock_alerts


class LowStockAlertMiddleware(MiddlewareMixin):
    """
    Middleware that checks and sends low stock alerts on every request.
    This ensures alerts are sent whenever a user accesses the application
    if stock has fallen below threshold and 24+ hours have passed.
    """
    
    def process_request(self, request):
        """
        Called on every incoming request.
        Checks for low stock products and sends emails if needed.
        """
        try:
            # Check and send low stock alerts
            check_and_send_stock_alerts()
        except Exception as e:
            # Don't let alert errors break the application
            print(f"Error checking stock alerts: {e}")
        
        return None
