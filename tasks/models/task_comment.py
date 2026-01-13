from django.db import models
from accounts.models import User


class TaskComment(models.Model):
    """
    Model for task comments/notes.
    """
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_comments'
        verbose_name = 'Task Comment'
        verbose_name_plural = 'Task Comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.get_full_name()} on {self.task.title}"
