from django.db import models
from django.utils import timezone
from accounts.models import User


class APIDocumentationPage(models.Model):
    """
    Model for organizing API documentation by pages (like Figma pages).
    For example: Dashboard page, Profile page, etc.
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='api_documentation_pages'
    )
    page_name = models.CharField(
        max_length=255,
        help_text="Page name (e.g., Dashboard, Profile, Settings)"
    )
    figma_link = models.URLField(
        blank=True,
        null=True,
        help_text="Link to Figma page (optional)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the page and its functionality"
    )
    order = models.IntegerField(
        default=0,
        help_text="Order for displaying pages"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_api_pages',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_documentation_pages'
        verbose_name = 'API Documentation Page'
        verbose_name_plural = 'API Documentation Pages'
        ordering = ['order', 'page_name']
        unique_together = ['project', 'page_name']

    def __str__(self):
        return f"{self.page_name} - {self.project.name}"


class APIEndpoint(models.Model):
    """
    Model for storing API endpoint documentation.
    Each endpoint belongs to a page and a project.
    """
    HTTP_METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]

    page = models.ForeignKey(
        APIDocumentationPage,
        on_delete=models.CASCADE,
        related_name='api_endpoints'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='api_endpoints'
    )
    name = models.CharField(
        max_length=255,
        help_text="API endpoint name/description"
    )
    endpoint_url = models.CharField(
        max_length=500,
        help_text="Full API endpoint URL (e.g., /api/users/list/)"
    )
    http_method = models.CharField(
        max_length=10,
        choices=HTTP_METHOD_CHOICES,
        default='GET'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of what this API does"
    )
    request_body = models.TextField(
        blank=True,
        null=True,
        help_text="Request body example (JSON format)"
    )
    response_body = models.TextField(
        blank=True,
        null=True,
        help_text="Response body example (JSON format)"
    )
    request_headers = models.TextField(
        blank=True,
        null=True,
        help_text="Required request headers (JSON format)"
    )
    response_status_codes = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Possible response status codes (e.g., 200, 400, 401, 404)"
    )
    authentication_required = models.BooleanField(
        default=True,
        help_text="Whether authentication is required for this endpoint"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes, tips, or important information about this API endpoint"
    )
    order = models.IntegerField(
        default=0,
        help_text="Order for displaying endpoints within the page"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_api_endpoints',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_endpoints'
        verbose_name = 'API Endpoint'
        verbose_name_plural = 'API Endpoints'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.http_method} {self.endpoint_url} - {self.name}"
