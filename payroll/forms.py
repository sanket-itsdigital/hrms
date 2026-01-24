from django import forms
from .models import Payroll, SalaryStructure
from accounts.models import User
from organizations.models import Organization
from django.utils import timezone
import calendar


class PayrollForm(forms.ModelForm):
    """Form for creating and updating payroll records"""
    
    # Override month field to use ChoiceField with proper choices
    month = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    class Meta:
        model = Payroll
        fields = ['user', 'month', 'year', 'base_salary', 'bonuses', 'deductions', 'attendance_deduction', 'notes']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'min': 2020,
                'max': 2030
            }),
            'base_salary': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0'
            }),
            'bonuses': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0'
            }),
            'deductions': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0'
            }),
            'attendance_deduction': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Optional notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Filter users based on organization
        if user and organization:
            self.fields['user'].queryset = User.objects.filter(
                organization=organization,
                is_active=True
            ).order_by('first_name', 'last_name')
        
        # Set month choices - using calendar.month_name which has empty string at index 0
        month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
        self.fields['month'].choices = month_choices
        
        # Set default month and year
        if not self.instance.pk:
            now = timezone.now()
            self.fields['month'].initial = str(now.month)  # Convert to string for ChoiceField
            self.fields['year'].initial = now.year
        else:
            # For existing records, convert month to string
            if self.instance.month:
                self.fields['month'].initial = str(self.instance.month)
            if self.instance.year:
                self.fields['year'].initial = self.instance.year
    
    def clean_month(self):
        """Convert month choice to integer"""
        month = self.cleaned_data.get('month')
        if month:
            return int(month)
        return month
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')
        
        # Check for duplicate payroll
        if user and month and year:
            existing = Payroll.objects.filter(user=user, month=month, year=year)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    f'Payroll for {user.get_full_name()} for {calendar.month_name[month]} {year} already exists.'
                )
        
        return cleaned_data
