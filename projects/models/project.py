from django.db import models
from django.utils import timezone
from organizations.models import Organization
from accounts.models import User


class Project(models.Model):
    """
    Project model for managing IT company projects.
    """
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    deadline = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payment_details = models.TextField(blank=True, null=True)
    
    # Client Information
    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_company = models.CharField(max_length=255, blank=True, null=True)
    
    # Project Manager
    project_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='managed_projects',
        null=True,
        blank=True
    )
    
    # Created by
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_projects',
        null=True
    )
    
    completion_percentage = models.IntegerField(default=0, help_text="Auto-calculated from tasks")
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def calculate_completion(self):
        """Calculate completion percentage based on tasks"""
        from tasks.models import Task
        tasks = Task.objects.filter(project_id=self.id)
        if not tasks.exists():
            return 0
        completed = tasks.filter(status='COMPLETED').count()
        total = tasks.count()
        return int((completed / total) * 100) if total > 0 else 0

    def save(self, *args, **kwargs):
        if self.pk:
            self.completion_percentage = self.calculate_completion()
        super().save(*args, **kwargs)
