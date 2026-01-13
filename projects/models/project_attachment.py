from django.db import models


class ProjectAttachment(models.Model):
    """
    Model for storing project-related attachments (requirements docs, etc.)
    """
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='projects/attachments/')
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        db_table = 'project_attachments'
        verbose_name = 'Project Attachment'
        verbose_name_plural = 'Project Attachments'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name or self.file.name} - {self.project.name}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        super().save(*args, **kwargs)
