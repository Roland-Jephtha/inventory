from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth import get_user_model
from .decorators import owner_required

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        if not full_name or not email or not phone or not password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'users/signup.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'users/signup.html')
        username = email
        first_name = full_name.split(' ')[0]
        last_name = ' '.join(full_name.split(' ')[1:]) if len(full_name.split(' ')) > 1 else ''
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.save()
        login(request, user)
        return redirect('business_setup')
    return render(request, 'users/signup.html')


# Staff Management Views

@owner_required
def staff_list(request):
    """List all staff members (owner only)"""
    staff_members = User.objects.filter(role='STAFF').order_by('-date_joined')
    context = {
        'staff_members': staff_members,
    }
    return render(request, 'users/staff_list.html', context)


@owner_required
def staff_create(request):
    """Create a new staff member (owner only)"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        
        # Validation
        if not full_name or not email or not password or not username:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/staff_form.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'A user with this username already exists.')
            return render(request, 'users/staff_form.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'users/staff_form.html')
        
        # Create staff user
        # Create staff user
        # username is already set from POST
        first_name = full_name.split(' ')[0]
        last_name = ' '.join(full_name.split(' ')[1:]) if len(full_name.split(' ')) > 1 else ''
        
        staff = User.objects.create_user(username=username, email=email, password=password)
        staff.first_name = first_name
        staff.last_name = last_name
        staff.phone = phone
        staff.role = 'STAFF'  # Explicitly set role to STAFF
        staff.save()
        
        messages.success(request, f'Staff member {full_name} has been created successfully.')
        return redirect('staff_list')
    
    return render(request, 'users/staff_form.html')


@owner_required
def staff_edit(request, staff_id):
    """Edit an existing staff member (owner only)"""
    staff = get_object_or_404(User, id=staff_id, role='STAFF')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Validation
        if not full_name or not email or not username:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/staff_form.html', {'staff': staff})
        
        # Check if username is taken by another user
        if User.objects.filter(username=username).exclude(id=staff_id).exists():
            messages.error(request, 'A user with this username already exists.')
            return render(request, 'users/staff_form.html', {'staff': staff})

        # Check if email is taken by another user
        if User.objects.filter(email=email).exclude(id=staff_id).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'users/staff_form.html', {'staff': staff})
        
        # Update staff user
        first_name = full_name.split(' ')[0]
        last_name = ' '.join(full_name.split(' ')[1:]) if len(full_name.split(' ')) > 1 else ''
        
        staff.username = username
        staff.email = email
        staff.first_name = first_name
        staff.last_name = last_name
        staff.phone = phone
        
        # Update password only if provided
        if password:
            staff.set_password(password)
        
        staff.save()
        
        messages.success(request, f'Staff member {full_name} has been updated successfully.')
        return redirect('staff_list')
    
    context = {
        'staff': staff,
    }
    return render(request, 'users/staff_form.html', context)


@owner_required
def staff_delete(request, staff_id):
    """Delete a staff member (owner only)"""
    staff = get_object_or_404(User, id=staff_id, role='STAFF')
    
    if request.method == 'POST':
        staff_name = f"{staff.first_name} {staff.last_name}"
        staff.delete()
        messages.success(request, f'Staff member {staff_name} has been deleted successfully.')
        return redirect('staff_list')
    
    context = {
        'staff': staff,
    }
    return render(request, 'users/staff_confirm_delete.html', context)
