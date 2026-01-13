from django.db import models
from accounts.models import User


class TaskActivity(models.Model):
    """
    Model for tracking task activity/logs.
    """
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('UPDATED', 'Updated'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('ASSIGNED', 'Assigned'),
        ('COMMENTED', 'Commented'),
        ('COMPLETED', 'Completed'),
    ]

    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    old_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_activities'
        verbose_name = 'Task Activity'
        verbose_name_plural = 'Task Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.task.title} by {self.user.get_full_name() if self.user else 'System'}"
