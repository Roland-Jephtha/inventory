from django.shortcuts import render, redirect

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
