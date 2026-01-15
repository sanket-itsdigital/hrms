from django.utils import timezone
from django.db.models import Q
from notifications.models import Notification
from tasks.models import Task


def create_task_notification(task, notification_type, user=None):
    """Create a notification for task-related events"""
    if not task.assigned_to or not task.assigned_to.organization:
        return None
    
    notification_type_map = {
        'assigned': 'TASK_ASSIGNED',
        'updated': 'TASK_UPDATED',
        'deadline': 'DEADLINE_APPROACHING',
    }
    
    notification_type_code = notification_type_map.get(notification_type, 'TASK_UPDATED')
    
    if notification_type == 'assigned':
        title = f"New Task Assigned: {task.title}"
        message = f"You have been assigned a new task '{task.title}' in project '{task.project.name}'."
    elif notification_type == 'updated':
        title = f"Task Updated: {task.title}"
        message = f"The task '{task.title}' in project '{task.project.name}' has been updated."
    elif notification_type == 'deadline':
        title = f"Task Deadline Approaching: {task.title}"
        message = f"The task '{task.title}' deadline is approaching in project '{task.project.name}'."
    else:
        title = f"Task Notification: {task.title}"
        message = f"There's an update on task '{task.title}' in project '{task.project.name}'."
    
    notification = Notification.objects.create(
        organization=task.assigned_to.organization,
        user=task.assigned_to,
        notification_type=notification_type_code,
        title=title,
        message=message,
        link=f"/api/tasks/{task.id}/",
        related_object_type='Task',
        related_object_id=task.id
    )
    
    return notification


def check_deadline_notifications():
    """Check for tasks with approaching deadlines and create notifications"""
    from datetime import timedelta
    
    # Check tasks with deadlines in the next 24 hours
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_tasks = Task.objects.filter(
        deadline__lte=tomorrow,
        deadline__gt=timezone.now(),
        status__in=['TO_DO', 'IN_PROGRESS', 'BLOCKED'],
        assigned_to__isnull=False
    )
    
    notifications_created = 0
    for task in upcoming_tasks:
        # Check if notification was already sent today
        existing_notification = Notification.objects.filter(
            user=task.assigned_to,
            notification_type='DEADLINE_APPROACHING',
            related_object_id=task.id,
            created_at__date=timezone.now().date()
        ).exists()
        
        if not existing_notification:
            create_task_notification(task, 'deadline')
            notifications_created += 1
    
    return notifications_created
