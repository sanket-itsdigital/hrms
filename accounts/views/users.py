from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from accounts.models import User, Role
from organizations.models import Organization

User = get_user_model()


@login_required
def list_users(request):
    """List all users with filtering"""
    user = request.user
    
    # Check permissions - only CEO can manage users
    if not user.is_ceo:
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('accounts:dashboard')
    
    # Get user's organization
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Get all users in organization
    users = User.objects.filter(
        organization=organization
    ).select_related('role', 'organization').order_by('-created_at')
    
    # Filtering
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(role__name=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all roles for filter
    roles = Role.objects.filter(is_active=True).order_by('name')
    
    # Statistics
    total_users = users.count()
    active_count = users.filter(is_active=True).count()
    inactive_count = users.filter(is_active=False).count()
    users_by_role = users.values('role__name').annotate(count=Count('id'))
    role_counts = {item['role__name']: item['count'] for item in users_by_role if item['role__name']}
    
    context = {
        'page_obj': page_obj,
        'users': page_obj,
        'roles': roles,
        'total_users': total_users,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'role_counts': role_counts,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'accounts/users/list.html', context)


@login_required
def create_user(request):
    """Create a new user"""
    user = request.user
    
    # Check permissions
    if not user.is_ceo:
        messages.error(request, 'You do not have permission to create users.')
        return redirect('accounts:users')
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from accounts.forms import UserForm
        form = UserForm(request.POST, request.FILES, user=user, organization=user.organization)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.organization = user.organization
            password = form.cleaned_data.get('password')
            if password:
                new_user.set_password(password)
            new_user.save()
            messages.success(request, f'User {new_user.get_full_name()} created successfully!')
            return redirect('accounts:users')
    else:
        from accounts.forms import UserForm
        form = UserForm(user=user, organization=user.organization)
    
    return render(request, 'accounts/users/form.html', {
        'form': form,
        'title': 'Create New User'
    })


@login_required
def update_user(request, id):
    """Update an existing user"""
    user = request.user
    
    # Check permissions
    if not user.is_ceo:
        messages.error(request, 'You do not have permission to update users.')
        return redirect('accounts:users')
    
    target_user = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        from accounts.forms import UserForm
        form = UserForm(request.POST, request.FILES, instance=target_user, user=user, organization=user.organization)
        if form.is_valid():
            updated_user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                updated_user.set_password(password)
            updated_user.save()
            messages.success(request, f'User {updated_user.get_full_name()} updated successfully!')
            return redirect('accounts:users')
    else:
        from accounts.forms import UserForm
        form = UserForm(instance=target_user, user=user, organization=user.organization)
    
    return render(request, 'accounts/users/form.html', {
        'form': form,
        'target_user': target_user,
        'title': 'Update User'
    })


@login_required
def delete_user(request, id):
    """Delete a user"""
    user = request.user
    
    # Check permissions
    if not user.is_ceo:
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('accounts:users')
    
    target_user = get_object_or_404(User, id=id)
    
    # Prevent self-deletion
    if target_user.id == user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:users')
    
    if request.method == 'POST':
        user_name = target_user.get_full_name()
        target_user.delete()
        messages.success(request, f'User {user_name} deleted successfully!')
        return redirect('accounts:users')
    
    return render(request, 'accounts/users/delete_confirm.html', {
        'target_user': target_user
    })


@login_required
def profile_view(request):
    """User profile view - allows users to view and edit their own profile"""
    user = request.user
    
    if request.method == 'POST':
        from accounts.forms import ProfileForm
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        from accounts.forms import ProfileForm
        form = ProfileForm(instance=user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': user
    })


@login_required
def settings_view(request):
    """User settings view - allows users to change password and manage account settings"""
    user = request.user
    
    # Handle password change
    password_form = None
    password_changed = False
    
    if request.method == 'POST':
        if 'change_password' in request.POST:
            from accounts.forms import PasswordChangeForm
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Your password has been changed successfully!')
                password_changed = True
                # Reset form after successful change
                password_form = PasswordChangeForm(user=user)
        else:
            from accounts.forms import PasswordChangeForm
            password_form = PasswordChangeForm(user=user)
    else:
        from accounts.forms import PasswordChangeForm
        password_form = PasswordChangeForm(user=user)
    
    return render(request, 'accounts/settings.html', {
        'user': user,
        'password_form': password_form,
        'password_changed': password_changed
    })
