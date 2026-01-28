from django import forms
from company.models import Announcement, Policy, Holiday, RecurringHolidayRule, Event, BirthdayAnniversary
from accounts.models import User
from django.utils import timezone


class AnnouncementForm(forms.ModelForm):
    """Form for creating and updating announcements"""
    
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'priority', 'is_pinned',
            'target_roles', 'attachment', 'expires_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter announcement title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 6,
                'placeholder': 'Enter announcement content'
            }),
            'priority': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Target roles field - multi-select
        from accounts.models import Role
        role_choices = [(role.name, role.display_name) for role in Role.objects.filter(is_active=True)]
        
        # Get initial value from instance if editing
        initial_target_roles = []
        if self.instance and self.instance.pk:
            initial_target_roles = self.instance.target_roles or []
        
        self.fields['target_roles'] = forms.MultipleChoiceField(
            choices=role_choices,
            required=False,
            initial=initial_target_roles,
            widget=forms.SelectMultiple(attrs={
                'class': 'select select-bordered w-full',
                'size': '5'
            }),
            help_text="Select roles this announcement is for. Leave empty for all roles."
        )
        
        self.fields['title'].required = True
        self.fields['content'].required = True
    
    def clean_target_roles(self):
        """Ensure target_roles is always a list"""
        target_roles = self.cleaned_data.get('target_roles', [])
        if target_roles is None:
            return []
        return list(target_roles) if target_roles else []


class PolicyForm(forms.ModelForm):
    """Form for creating and updating policies"""
    
    class Meta:
        model = Policy
        fields = [
            'title', 'category', 'description', 'document',
            'version', 'is_active', 'effective_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter policy title'
            }),
            'category': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Enter policy description'
            }),
            'document': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': '.pdf,.doc,.docx'
            }),
            'version': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., 1.0, 2.1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'effective_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['document'].required = True
        self.fields['effective_date'].required = True


class HolidayForm(forms.ModelForm):
    """Form for creating and updating holidays"""
    
    class Meta:
        model = Holiday
        fields = [
            'name', 'date', 'holiday_type', 'description', 'is_recurring'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., Independence Day, Diwali'
            }),
            'date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'holiday_type': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['date'].required = True


class RecurringHolidayRuleForm(forms.ModelForm):
    """Form for adding recurring rules e.g. 2nd Saturday, 4th Saturday."""

    class Meta:
        model = RecurringHolidayRule
        fields = ['name', 'weekday', 'week_of_month']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. 2nd Saturday Off',
            }),
            'weekday': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'week_of_month': forms.Select(attrs={'class': 'select select-bordered w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['week_of_month'].choices = [(i, f'{i}{"st" if i == 1 else "nd" if i == 2 else "rd" if i == 3 else "th"} of month') for i in range(1, 6)]


class EventForm(forms.ModelForm):
    """Form for creating and updating events"""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'start_date',
            'end_date', 'location', 'venue_link', 'is_virtual', 'attendees'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Enter event description'
            }),
            'event_type': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Physical location or venue'
            }),
            'venue_link': forms.URLInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'https://meet.google.com/...'
            }),
            'is_virtual': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'attendees': forms.SelectMultiple(attrs={
                'class': 'select select-bordered w-full',
                'size': '8'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter attendees by organization
        if user and user.organization:
            self.fields['attendees'].queryset = User.objects.filter(
                organization=user.organization,
                is_active=True
            ).order_by('first_name', 'last_name', 'username')
        else:
            self.fields['attendees'].queryset = User.objects.filter(is_active=True)
        
        self.fields['title'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data


class BirthdayAnniversaryForm(forms.ModelForm):
    """Form for updating birthday and anniversary information"""
    
    class Meta:
        model = BirthdayAnniversary
        fields = ['birth_date', 'joining_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'joining_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
        }
    
    def clean_birth_date(self):
        """Validate birth date is not in the future"""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > timezone.now().date():
            raise forms.ValidationError("Birth date cannot be in the future.")
        return birth_date
    
    def clean_joining_date(self):
        """Validate joining date is not in the future"""
        joining_date = self.cleaned_data.get('joining_date')
        if joining_date and joining_date > timezone.now().date():
            raise forms.ValidationError("Joining date cannot be in the future.")
        return joining_date
