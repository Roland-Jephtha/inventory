from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps

def owner_required(view_func):
    """
    Decorator to restrict access to owner users only.
    Staff users will be redirected to dashboard.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'OWNER':
            return view_func(request, *args, **kwargs)
        else:
            # Redirect staff to dashboard
            return redirect('dashboard')
    return wrapper


def staff_or_owner_required(view_func):
    """
    Decorator to allow both staff and owner access.
    Just ensures user is authenticated.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
