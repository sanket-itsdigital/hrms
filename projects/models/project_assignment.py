from django.db import models
from accounts.models import User


class ProjectAssignment(models.Model):
    """
    Model for assigning team members to projects.
    """
    ROLE_CHOICES = [
        ('PM', 'Project Manager'),
        ('DEV', 'Developer'),
        ('UIUX', 'UI/UX Designer'),
        ('BDE', 'Business Development Executive'),
    ]

    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='project_assignments_made',
        null=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'project_assignments'
        verbose_name = 'Project Assignment'
        verbose_name_plural = 'Project Assignments'
        unique_together = ['project', 'user']
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.name} ({self.role})"
