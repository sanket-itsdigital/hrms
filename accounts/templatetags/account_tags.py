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
