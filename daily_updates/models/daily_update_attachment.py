from django.db import models


class DailyUpdateAttachment(models.Model):
    """
    Model for storing attachments (screenshots, docs) for daily updates.
    """
    daily_update = models.ForeignKey('daily_updates.DailyUpdate', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='daily_updates/attachments/')
    file_type = models.CharField(max_length=50, blank=True, help_text="image, document, etc.")
    thumbnail = models.ImageField(upload_to='daily_updates/thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'daily_update_attachments'
        verbose_name = 'Daily Update Attachment'
        verbose_name_plural = 'Daily Update Attachments'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Attachment for {self.daily_update}"
