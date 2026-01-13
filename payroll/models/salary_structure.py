from django.db import models
from accounts.models import User
from organizations.models import Organization


class SalaryStructure(models.Model):
    """
    Model for storing employee salary structure.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='salary_structures')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salary_structure')
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.JSONField(default=dict, help_text="JSON object for various allowances")
    deductions = models.JSONField(default=dict, help_text="JSON object for various deductions")
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salary_structures'
        verbose_name = 'Salary Structure'
        verbose_name_plural = 'Salary Structures'
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.base_salary}"
