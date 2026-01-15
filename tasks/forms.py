from django import forms
from django.db.models import Q
from tasks.models import Task
from projects.models import Project, ProjectAssignment
from accounts.models import User
from django.utils import timezone


class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks"""
    
    class Meta:
        model = Task
        fields = [
            'project', 'title', 'description', 'status', 'priority',
            'deadline', 'assigned_to'
        ]
        widgets = {
            'project': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Enter task description'
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'priority': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'datetime-local'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)
        
        # Set default empty queryset first
        self.fields['project'].queryset = Project.objects.none()
        self.fields['assigned_to'].queryset = User.objects.none()
        
        # Filter projects based on user role - following same pattern as projects list view
        if user:
            organization = user.organization
            
            # Base queryset
            projects_queryset = Project.objects.select_related(
                'organization', 'project_manager', 'created_by'
            ).prefetch_related('assignments__user').all()
            
            # Filter by organization first
            if organization:
                projects_queryset = projects_queryset.filter(organization=organization)
            
            # Role-based filtering
            if user.is_ceo:
                # CEO sees all projects (in their org if they have one, otherwise all)
                if not organization:
                    # If CEO has no organization, show all projects
                    projects_queryset = Project.objects.all()
            elif user.is_pm:
                # PM sees projects they manage or are assigned to
                if organization:
                    # Filter within organization first
                    projects_queryset = projects_queryset.filter(
                        Q(project_manager=user) | Q(assignments__user=user, assignments__is_active=True)
                    ).distinct()
                else:
                    # If no organization, just filter by PM role
                    projects_queryset = projects_queryset.filter(
                        Q(project_manager=user) | Q(assignments__user=user, assignments__is_active=True)
                    ).distinct()
            elif user.is_hr or user.is_bde:
                # HR and BDE can see all projects in their organization (read-only)
                if not organization:
                    projects_queryset = Project.objects.none()
            elif user.is_dev or user.is_uiux:
                # Developers/UIUX see projects they're assigned to
                projects_queryset = projects_queryset.filter(
                    assignments__user=user,
                    assignments__is_active=True
                ).distinct()
            else:
                projects_queryset = Project.objects.none()
            
            # Order by name
            self.fields['project'].queryset = projects_queryset.order_by('name')
            
            # If project_id is provided, set it
            if project_id:
                self.fields['project'].initial = project_id
        
        # Filter assigned_to based on project assignments
        if project_id:
            project = Project.objects.filter(id=project_id).first()
            if project:
                # Get users assigned to this project (Dev, UIUX, BDE)
                assigned_users = User.objects.filter(
                    project_assignments__project=project,
                    project_assignments__is_active=True,
                    role__name__in=['Dev', 'UIUX', 'BDE']
                ).distinct()
                self.fields['assigned_to'].queryset = assigned_users
            else:
                # If project not found, show empty queryset
                self.fields['assigned_to'].queryset = User.objects.none()
        else:
            # If no project selected, show all Dev/UIUX/BDE users in organization
            if user and user.organization:
                self.fields['assigned_to'].queryset = User.objects.filter(
                    organization=user.organization,
                    role__name__in=['Dev', 'UIUX', 'BDE']
                ).order_by('first_name', 'last_name', 'username')
            else:
                self.fields['assigned_to'].queryset = User.objects.filter(
                    role__name__in=['Dev', 'UIUX', 'BDE']
                ).order_by('first_name', 'last_name', 'username')
        
        self.fields['title'].required = True
        self.fields['project'].required = True
    
    def clean_deadline(self):
        """Validate deadline is not in the past"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
