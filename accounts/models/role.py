from django.db import models


class Role(models.Model):
    """
    Role model for defining user roles in the system.
    """
    ROLE_CHOICES = [
        ('CEO', 'CEO'),
        ('HR', 'HR'),
        ('PM', 'Project Manager'),
        ('DEV', 'Developer'),
        ('UIUX', 'UI/UX Designer'),
        ('BDE', 'Business Development Executive'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(default=dict, help_text="JSON object storing role permissions")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.display_name
