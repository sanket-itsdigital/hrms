from django.db import models
from accounts.models import User
from organizations.models import Organization


class Leave(models.Model):
    """
    Leave model for managing employee leave requests.
    """
    LEAVE_TYPE_CHOICES = [
        ('SICK', 'Sick Leave'),
        ('VACATION', 'Vacation/Annual Leave'),
        ('CASUAL', 'Casual Leave'),
        ('EMERGENCY', 'Emergency Leave'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='leaves')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='CASUAL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_from = models.DateField()
    date_to = models.DateField()
    days = models.IntegerField(help_text="Number of leave days")
    reason = models.TextField()
    attachment = models.FileField(upload_to='leaves/attachments/', blank=True, null=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='approved_leaves',
        null=True,
        blank=True
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leaves'
        verbose_name = 'Leave'
        verbose_name_plural = 'Leaves'
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['organization', 'date_from']),
            models.Index(fields=['status', 'date_from']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.leave_type} ({self.date_from} to {self.date_to})"

    def save(self, *args, **kwargs):
        if self.date_from and self.date_to:
            delta = self.date_to - self.date_from
            self.days = delta.days + 1
        super().save(*args, **kwargs)
