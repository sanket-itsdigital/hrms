from django.db import models
from accounts.models import User


class MeetingLog(models.Model):
    """
    Meeting log model for tracking calls/meetings with leads.
    """
    MEETING_TYPE_CHOICES = [
        ('CALL', 'Phone Call'),
        ('MEETING', 'In-Person Meeting'),
        ('VIDEO', 'Video Call'),
        ('EMAIL', 'Email Communication'),
    ]

    lead = models.ForeignKey('leads_crm.Lead', on_delete=models.CASCADE, related_name='meeting_logs')
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='CALL')
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True, help_text="Duration in minutes")
    notes = models.TextField()
    logged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'meeting_logs'
        verbose_name = 'Meeting Log'
        verbose_name_plural = 'Meeting Logs'
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.meeting_type} with {self.lead.name} on {self.date}"
