from django import forms
from django.db.models import Q
from projects.models import Project, Milestone, Payment
from organizations.models import Organization
from accounts.models import User
from django.utils import timezone


class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects"""
    
    class Meta:
        model = Project
        fields = [
            'organization', 'name', 'description', 'requirements',
            'status', 'priority', 'deadline', 'budget', 'payment_details',
            'client_name', 'client_email', 'client_phone', 'client_company',
            'project_manager'
        ]
        widgets = {
            'organization': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Enter project description'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Enter project requirements'
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'priority': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'payment_details': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Enter payment details'
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Client name'
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'client@example.com'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '+1234567890'
            }),
            'client_company': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Client company name'
            }),
            'project_manager': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter organizations based on user
        if user and user.organization:
            self.fields['organization'].queryset = Organization.objects.filter(
                id=user.organization.id
            )
            self.fields['organization'].initial = user.organization
        else:
            self.fields['organization'].queryset = Organization.objects.all()
        
        # Filter project managers - only PMs and CEO
        if user:
            pm_queryset = User.objects.filter(
                Q(role__name='PM') | Q(role__name='CEO')
            ).distinct()
            self.fields['project_manager'].queryset = pm_queryset
        else:
            self.fields['project_manager'].queryset = User.objects.filter(
                Q(role__name='PM') | Q(role__name='CEO')
            )
        
        # Make organization required
        self.fields['organization'].required = True
        self.fields['name'].required = True
    
    def clean_deadline(self):
        """Validate deadline is not in the past"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
    
    def clean_budget(self):
        """Validate budget is positive"""
        budget = self.cleaned_data.get('budget')
        if budget is not None and budget < 0:
            raise forms.ValidationError("Budget cannot be negative.")
        return budget


class MilestoneForm(forms.ModelForm):
    """Form for creating and updating milestones"""
    
    class Meta:
        model = Milestone
        fields = [
            'name', 'description', 'status', 'due_date',
            'completion_percentage', 'assigned_to'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter milestone name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Enter milestone description'
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'completion_percentage': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'min': 0,
                'max': 100,
                'step': 1
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter assigned_to based on project assignments
        if project:
            assigned_users = User.objects.filter(
                project_assignments__project=project
            ).distinct()
            self.fields['assigned_to'].queryset = assigned_users
        else:
            self.fields['assigned_to'].queryset = User.objects.all()
        
        self.fields['name'].required = True
    
    def clean_completion_percentage(self):
        """Validate completion percentage is between 0 and 100"""
        percentage = self.cleaned_data.get('completion_percentage')
        if percentage is not None and (percentage < 0 or percentage > 100):
            raise forms.ValidationError("Completion percentage must be between 0 and 100.")
        return percentage


class PaymentForm(forms.ModelForm):
    """Form for creating and updating payments"""
    
    class Meta:
        model = Payment
        fields = [
            'milestone', 'payment_type', 'amount', 'paid_amount',
            'due_date', 'paid_date', 'payment_method', 'transaction_id', 'notes'
        ]
        widgets = {
            'milestone': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'paid_amount': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'paid_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Bank Transfer, Check, Cash, etc.'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Transaction ID or reference number'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Payment notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Filter milestones based on project
        if project:
            self.fields['milestone'].queryset = Milestone.objects.filter(
                project=project
            )
        else:
            self.fields['milestone'].queryset = Milestone.objects.none()
        
        self.fields['amount'].required = True
        self.fields['due_date'].required = True
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
    
    def clean_paid_amount(self):
        """Validate paid amount is not greater than amount"""
        paid_amount = self.cleaned_data.get('paid_amount', 0)
        amount = self.cleaned_data.get('amount')
        if amount and paid_amount > amount:
            raise forms.ValidationError("Paid amount cannot be greater than total amount.")
        return paid_amount
