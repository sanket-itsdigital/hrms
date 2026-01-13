from django.db import models
from accounts.models import User
from organizations.models import Organization


class DailyUpdate(models.Model):
    """
    Daily update model for developers and UI/UX team to submit daily work updates.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='daily_updates')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='daily_updates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_updates')
    description = models.TextField(help_text="Work done today")
    figma_link = models.URLField(blank=True, null=True, help_text="Figma link for UI/UX team")
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_updates'
        verbose_name = 'Daily Update'
        verbose_name_plural = 'Daily Updates'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'date']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['organization', 'date']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.name} - {self.date}"
