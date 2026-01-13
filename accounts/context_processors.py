def notifications_context(request):
    """Context processor to add unread notifications count to all templates"""
    if request.user.is_authenticated:
        try:
            unread_count = request.user.notifications.filter(is_read=False).count()
        except:
            unread_count = 0
    else:
        unread_count = 0
    
    return {
        'unread_notifications_count': unread_count
    }
