from django.shortcuts import render, redirect
from django.utils import timezone
from users.models import User

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def business_setup(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        theme_color = request.POST.get('theme_color')
        request.session['theme_color'] = theme_color or '#4318ff'
        return redirect('dashboard')
    return render(request, 'onboarding_setup.html')

def access_paused(request):
    """View for the 'Access Paused' page (soft paywall)"""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'subscription/access_paused.html')

def verify_payment(request):
    """Verify Paystack payment and activate subscription"""
    reference = request.GET.get('reference')
    if not reference:
        return redirect('access_paused')
    
    # In a real app, verify with Paystack API here
    # For now, we assume success if reference exists
    
    user = request.user
    user.subscription_status = User.SubscriptionStatus.ACTIVE
    user.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
    user.save()
    
    # Clear any expired flags in session/request if needed
    
    return redirect('dashboard')
