"""
Utility functions and decorators for accounts app.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from .permissions_config import has_permission as check_permission, get_module_permissions


def role_required(*allowed_roles):
    """
    Decorator to check if user has required role.
    Usage: @role_required('CEO', 'HR')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('accounts:login')
            
            if not request.user.role:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'User role not assigned'}, status=403)
                messages.error(request, 'Your account does not have a role assigned.')
                return redirect('accounts:login')
            
            user_role = request.user.role.name
            if user_role not in allowed_roles and not request.user.is_ceo:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'Insufficient permissions'}, status=403)
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def org_required(view_func):
    """
    Decorator to ensure user belongs to an organization.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': 'Authentication required'}, status=401)
            return redirect('accounts:login')
        
        if not request.user.organization:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': 'User not assigned to an organization'}, status=403)
            messages.error(request, 'Your account is not assigned to an organization.')
            return redirect('accounts:login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required(module, action):
    """
    Decorator to check if user has specific permission.
    Usage: @permission_required('projects', 'create')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('accounts:login')
            
            if not request.user.role:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'User role not assigned'}, status=403)
                messages.error(request, 'Your account does not have a role assigned.')
                return redirect('accounts:login')
            
            user_role = request.user.role.name
            if not check_permission(user_role, module, action):
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'Insufficient permissions'}, status=403)
                messages.error(request, f'You do not have permission to {action} {module}.')
                return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def has_permission(user, module, action):
    """
    Check if user has a specific permission.
    
    Args:
        user: User instance
        module: Module name (users, projects, tasks, etc.)
        action: Action name (create, read, update, delete, etc.)
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    if user.is_ceo:
        return True
    
    if not user.role:
        return False
    
    return check_permission(user.role.name, module, action)


def get_user_permissions(user):
    """
    Get all permissions for a user based on their role.
    
    Returns:
        dict: Dictionary of all permissions for the user's role
    """
    if not user.role:
        return {}
    
    from .permissions_config import get_role_permissions
    return get_role_permissions(user.role.name)
