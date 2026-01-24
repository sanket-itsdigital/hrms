from django import forms
from .models import Lead, Proposal, MeetingLog
from accounts.models import User
from organizations.models import Organization


class LeadForm(forms.ModelForm):
    """Form for creating and updating leads"""
    
    class Meta:
        model = Lead
        fields = ['name', 'company_name', 'email', 'phone', 'stage', 'expected_revenue', 'probability', 'notes', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'stage': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'expected_revenue': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0'
            }),
            'probability': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'number',
                'min': '0',
                'max': '100',
                'step': '1'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Additional notes about the lead...'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Filter users based on organization and role
        if user and organization:
            if user.is_ceo:
                # CEO can assign to anyone
                self.fields['assigned_to'].queryset = User.objects.filter(
                    organization=organization,
                    is_active=True
                ).order_by('first_name', 'last_name')
            elif user.is_bde:
                # BDE can assign to other BDEs or themselves
                self.fields['assigned_to'].queryset = User.objects.filter(
                    organization=organization,
                    is_active=True,
                    role__name__in=['BDE', 'CEO']
                ).order_by('first_name', 'last_name')
            else:
                self.fields['assigned_to'].queryset = User.objects.filter(id=user.id)
        
        # Set default probability
        if not self.instance.pk:
            self.fields['probability'].initial = 0
