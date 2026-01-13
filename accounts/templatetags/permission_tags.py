from django import template
from accounts.utils import has_permission

register = template.Library()


@register.filter
def can_access(user, permission_string):
    """
    Template filter to check if user has permission.
    Usage: {% if user|can_access:"projects:create" %}
    Format: "module:action"
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_ceo:
        return True
    
    if not user.role:
        return False
    
    try:
        module, action = permission_string.split(':')
        return has_permission(user, module, action)
    except ValueError:
        return False


@register.simple_tag
def user_can(user, module, action):
    """
    Template tag to check if user has permission.
    Usage: {% user_can user "projects" "create" as can_create %}
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_ceo:
        return True
    
    if not user.role:
        return False
    
    return has_permission(user, module, action)
