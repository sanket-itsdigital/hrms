from django.db import models
from django.utils import timezone
from accounts.models import User


class Milestone(models.Model):
    """
    Milestone model for tracking project milestones.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    completion_percentage = models.IntegerField(default=0, help_text="Completion percentage (0-100)")
    
    # Assigned to
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_milestones',
        null=True,
        blank=True
    )
    
    # Created by
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_milestones',
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'milestones'
        verbose_name = 'Milestone'
        verbose_name_plural = 'Milestones'
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def is_overdue(self):
        """Check if milestone is overdue"""
        if self.due_date and self.status != 'COMPLETED':
            return timezone.now().date() > self.due_date
        return False
    
    def days_remaining(self):
        """Calculate days remaining until due date"""
        if self.due_date:
            today = timezone.now().date()
            return (self.due_date - today).days
        return None
