from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from accounts.models import User, Role
from organizations.models import Organization

User = get_user_model()


class UserForm(forms.ModelForm):
    """Form for creating and updating users"""
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Leave blank to keep existing password'
        }),
        help_text="Leave blank to keep existing password, or enter new password"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'profile_picture', 
                  'role', 'employee_id', 'designation', 'department', 'date_of_joining', 
                  'is_active', 'is_staff', 'is_verified']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full'
            }),
            'role': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'department': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'date_of_joining': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'is_verified': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Filter roles
        if organization:
            self.fields['role'].queryset = Role.objects.filter(is_active=True).order_by('name')
        
        # Make password required only for new users
        if self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = "Enter password for new user"
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing = User.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            existing = User.objects.filter(employee_id=employee_id)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A user with this employee ID already exists.')
        return employee_id


class ProfileForm(forms.ModelForm):
    """Form for users to edit their own profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing = User.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A user with this email already exists.')
        return email


class PasswordChangeForm(DjangoPasswordChangeForm):
    """Custom password change form with styled widgets"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Enter your current password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Enter your new password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirm your new password'
        })
