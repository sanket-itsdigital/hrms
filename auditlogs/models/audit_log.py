from django.db import models
from accounts.models import User
from organizations.models import Organization


class AuditLog(models.Model):
    """
    Audit log model for tracking critical actions in the system.
    """
    ACTION_TYPE_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
    ]

    OBJECT_TYPE_CHOICES = [
        ('USER', 'User'),
        ('PROJECT', 'Project'),
        ('TASK', 'Task'),
        ('ATTENDANCE', 'Attendance'),
        ('LEAVE', 'Leave'),
        ('PAYROLL', 'Payroll'),
        ('LEAD', 'Lead'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='audit_logs')
    action_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPE_CHOICES)
    object_id = models.IntegerField()
    object_repr = models.CharField(max_length=255, blank=True, null=True)
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_by', 'created_at']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.action_type} {self.object_type} #{self.object_id} by {self.action_by}"
