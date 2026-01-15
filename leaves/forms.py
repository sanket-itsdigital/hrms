from django import forms
from .models import Leave
from accounts.models import User
from organizations.models import Organization
from django.utils import timezone


class LeaveForm(forms.ModelForm):
    """Form for creating leave requests"""
    
    class Meta:
        model = Leave
        fields = ['leave_type', 'date_from', 'date_to', 'reason', 'attachment']
        widgets = {
            'leave_type': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'date_from': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'date_to': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Please provide a reason for your leave request...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Set default dates
        if not self.instance.pk:
            self.fields['date_from'].initial = timezone.now().date()
            self.fields['date_to'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_to < date_from:
                raise forms.ValidationError(
                    'End date must be after or equal to start date.'
                )
            
            # Check if dates are in the past
            today = timezone.now().date()
            if date_from < today:
                raise forms.ValidationError(
                    'Leave start date cannot be in the past.'
                )
        
        return cleaned_data
