from django.db import models
from accounts.models import User
from organizations.models import Organization


class Payroll(models.Model):
    """
    Payroll model for managing monthly payroll.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='payrolls')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payrolls')
    month = models.IntegerField()
    year = models.IntegerField()
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    attendance_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    payslip_generated = models.BooleanField(default=False)
    payslip_file = models.FileField(upload_to='payroll/payslips/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='processed_payrolls',
        null=True
    )
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payrolls'
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payrolls'
        unique_together = ['user', 'month', 'year']
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['user', 'year', 'month']),
            models.Index(fields=['organization', 'year', 'month']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.month}/{self.year} - {self.net_salary}"

    def calculate_net_salary(self):
        """Calculate net salary"""
        self.gross_salary = self.base_salary + self.bonuses
        self.net_salary = self.gross_salary - self.deductions - self.attendance_deduction
        return self.net_salary

    def get_month_display(self):
        """Get month name"""
        import calendar
        return calendar.month_name[self.month]
    
    def save(self, *args, **kwargs):
        self.calculate_net_salary()
        super().save(*args, **kwargs)
