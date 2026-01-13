from django.db import models
from accounts.models import User
from organizations.models import Organization


class LeaveBalance(models.Model):
    """
    Model for tracking leave balances for employees.
    """
    LEAVE_TYPE_CHOICES = [
        ('SICK', 'Sick Leave'),
        ('VACATION', 'Vacation/Annual Leave'),
        ('CASUAL', 'Casual Leave'),
        ('EMERGENCY', 'Emergency Leave'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='leave_balances')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    year = models.IntegerField()
    total_days = models.IntegerField(default=0)
    used_days = models.IntegerField(default=0)
    remaining_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_balances'
        verbose_name = 'Leave Balance'
        verbose_name_plural = 'Leave Balances'
        unique_together = ['user', 'leave_type', 'year']
        ordering = ['-year', 'leave_type']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.leave_type} ({self.year}): {self.remaining_days} days"

    def save(self, *args, **kwargs):
        self.remaining_days = self.total_days - self.used_days
        super().save(*args, **kwargs)
