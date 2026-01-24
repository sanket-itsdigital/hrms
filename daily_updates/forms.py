from django import forms
from daily_updates.models import DailyUpdate
from projects.models import Project
from accounts.models import User


class DailyUpdateForm(forms.ModelForm):
    """Form for creating and updating daily updates"""
    
    class Meta:
        model = DailyUpdate
        fields = ['project', 'description', 'figma_link', 'hours_worked', 'date']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 5,
                'placeholder': 'Describe the work you did today...'
            }),
            'figma_link': forms.URLInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'https://figma.com/...'
            }),
            'hours_worked': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.5',
                'min': '0',
                'max': '24',
                'placeholder': '8.0'
            }),
            'date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter projects based on user role
        if user:
            if user.is_ceo:
                # CEO can see all projects in their organization
                projects = Project.objects.filter(organization=user.organization)
            elif user.is_pm:
                # PM can see projects they manage
                projects = Project.objects.filter(
                    organization=user.organization,
                    project_manager=user
                )
            elif user.is_dev or user.is_uiux:
                # Developers/UIUX can see projects they're assigned to
                projects = Project.objects.filter(
                    organization=user.organization,
                    assignments__user=user,
                    assignments__is_active=True
                ).distinct()
            else:
                projects = Project.objects.none()
            
            self.fields['project'].queryset = projects.order_by('name')
            
            # Set default date to today if creating new
            if not self.instance.pk:
                from django.utils import timezone
                self.fields['date'].initial = timezone.now().date()
    
    def clean_date(self):
        """Validate that date is not in the future"""
        date = self.cleaned_data.get('date')
        if date:
            from django.utils import timezone
            if date > timezone.now().date():
                raise forms.ValidationError('Date cannot be in the future.')
        return date
    
    def clean_hours_worked(self):
        """Validate hours worked"""
        hours = self.cleaned_data.get('hours_worked')
        if hours is not None:
            if hours < 0:
                raise forms.ValidationError('Hours worked cannot be negative.')
            if hours > 24:
                raise forms.ValidationError('Hours worked cannot exceed 24 hours.')
        return hours
