from django.db import models
from accounts.models import User
from organizations.models import Organization


class Lead(models.Model):
    """
    Lead model for Business Development CRM.
    """

    STAGE_CHOICES = [
        ("NEW", "New"),
        ("CONTACTED", "Contacted"),
        ("PROPOSAL_SENT", "Proposal Sent"),
        ("NEGOTIATION", "Negotiation"),
        ("CLOSED_WON", "Closed Won"),
        ("CLOSED_LOST", "Closed Lost"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="leads"
    )
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default="NEW")
    expected_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    probability = models.IntegerField(
        default=0, help_text="Win probability percentage (0-100)"
    )
    notes = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_leads",
        null=True,
        blank=True,
    )
    assigned_users = models.ManyToManyField(
        User,
        related_name="lead_assignments",
        blank=True,
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="created_leads", null=True
    )
    converted_to_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_lead",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leads"
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["stage"]),
            models.Index(fields=["assigned_to", "stage"]),
            models.Index(fields=["organization", "stage"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.company_name} ({self.stage})"
