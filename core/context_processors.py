from django.utils import timezone
from users.models import User

def subscription_context(request):
    """
    Context processor to make subscription status available in all templates.
    Also handles the daily reminder logic.
    """
    if not request.user.is_authenticated:
        return {}

    user = request.user
    context = {
        'subscription_status': user.subscription_status,
        'is_trial': user.subscription_status == User.SubscriptionStatus.TRIAL,
        'is_active': user.subscription_status == User.SubscriptionStatus.ACTIVE,
        'is_expired': user.subscription_status == User.SubscriptionStatus.EXPIRED,
        'days_left': getattr(request, 'days_left', 0),
        'subscription_reminder': None,
        'subscription_reminder_color': 'green', # green, yellow, red
    }

    # Daily Reminder Logic (Soft Psychology)
    if context['is_trial']:
        days_left = context['days_left']
        
        if days_left == 4: # Day 3 used (4 days left)
            context['subscription_reminder'] = "💚 You're doing great! Keep managing your business with ease."
            context['subscription_reminder_color'] = 'green'
            
        elif days_left == 2: # Day 5 used (2 days left)
            context['subscription_reminder'] = "⏳ Your free access ends in 2 days. Don't lose your records!"
            context['subscription_reminder_color'] = 'yellow'
            
        elif days_left == 1: # Day 6 used (1 day left)
            context['subscription_reminder'] = "Keep your inventory live after tomorrow → Secure your business data with a plan."
            context['subscription_reminder_color'] = 'yellow'
            
        elif days_left == 0: # Day 7 (Last day)
            context['subscription_reminder'] = "Final reminder — your access expires today (don't worry, you won't lose data)."
            context['subscription_reminder_color'] = 'red'

    elif context['is_expired']:
        context['subscription_reminder'] = "Your access is paused. Activate a plan to continue adding records."
        context['subscription_reminder_color'] = 'red'

    return context
