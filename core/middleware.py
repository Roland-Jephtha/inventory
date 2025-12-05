from django.shortcuts import redirect, render
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from users.models import User

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check trial status
            self.check_subscription_status(request)
            
            # Feature Locking Logic
            if request.subscription_expired and request.method == 'POST':
                # List of locked views (names or paths)
                locked_paths = [
                    reverse('pos'),
                    reverse('product_create'),
                    reverse('product_update', args=[0]).replace('0', ''), # Partial match
                    reverse('product_delete', args=[0]).replace('0', ''),
                    reverse('checkout'),
                    # Add other locked paths here
                ]
                
                # Check if current path is locked
                is_locked = any(request.path.startswith(path) for path in locked_paths)
                
                # Special case for product update/delete which have dynamic IDs
                if 'product' in request.path and ('update' in request.path or 'delete' in request.path):
                    is_locked = True
                    
                if is_locked:
                    if request.headers.get('HX-Request'):
                        # For HTMX requests, return a special status or partial
                        return render(request, 'subscription/access_paused_partial.html')
                    return redirect('access_paused')

        response = self.get_response(request)
        return response

    def check_subscription_status(self, request):
        user = request.user
        request.subscription_expired = False
        request.days_left = 0
        
        if user.subscription_status == User.SubscriptionStatus.ACTIVE:
            return

        # Calculate trial days left
        if user.subscription_status == User.SubscriptionStatus.TRIAL:
            elapsed = timezone.now() - user.trial_start_date
            days_elapsed = elapsed.days
            days_left = 7 - days_elapsed
            
            request.days_left = max(0, days_left)
            
            if days_elapsed >= 7:
                user.subscription_status = User.SubscriptionStatus.EXPIRED
                user.save()
                request.subscription_expired = True
        
        elif user.subscription_status == User.SubscriptionStatus.EXPIRED:
            request.subscription_expired = True
            request.days_left = 0
