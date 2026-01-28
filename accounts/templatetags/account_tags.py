from django import template

register = template.Library()


@register.simple_tag
def get_unread_notifications_count(user):
    """Get count of unread notifications for a user"""
    if not user or not hasattr(user, 'notifications'):
        return 0
    return user.notifications.filter(is_read=False).count()


@register.filter
def unread_count(user):
    """Filter to get unread notifications count"""
    if not user or not hasattr(user, 'notifications'):
        return 0
    return user.notifications.filter(is_read=False).count()


@register.filter
def display_name(user):
    """
    Return a proper display name for a user. Handles cases like
    first_name=last_name (e.g. 'developer' + 'developer' -> 'Developer').
    """
    if not user:
        return ""
    full = (user.get_full_name() or "").strip()
    if not full:
        return user.email or getattr(user, "username", "") or ""
    parts = full.split()
    if len(parts) == 2 and parts[0].lower() == parts[1].lower():
        return parts[0].capitalize()
    return full.strip()
