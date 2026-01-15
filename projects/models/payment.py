from django.db import models
from django.utils import timezone
from accounts.models import User


class Payment(models.Model):
    """
    Payment model for tracking project payments.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('ADVANCE', 'Advance Payment'),
        ('MILESTONE', 'Milestone Payment'),
        ('FINAL', 'Final Payment'),
        ('OTHER', 'Other'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    milestone = models.ForeignKey(
        'projects.Milestone',
        on_delete=models.SET_NULL,
        related_name='payments',
        null=True,
        blank=True,
        help_text="Associated milestone (if applicable)"
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='MILESTONE')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Bank transfer, Check, Cash, etc."
    )
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Created by
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_payments',
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"{self.project.name} - ${self.amount} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-update status based on paid amount"""
        if self.paid_amount >= self.amount:
            self.status = 'COMPLETED'
            if not self.paid_date:
                self.paid_date = timezone.now().date()
        elif self.paid_amount > 0:
            self.status = 'PARTIAL'
        elif self.due_date and timezone.now().date() > self.due_date:
            self.status = 'OVERDUE'
        else:
            self.status = 'PENDING'
        
        super().save(*args, **kwargs)
    
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.amount - self.paid_amount
    
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.due_date and self.status not in ['COMPLETED', 'CANCELLED']:
            return timezone.now().date() > self.due_date
        return False
    
    def payment_percentage(self):
        """Calculate payment completion percentage"""
        if self.amount > 0:
            return int((self.paid_amount / self.amount) * 100)
        return 0
