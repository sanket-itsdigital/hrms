from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from projects.models import (
    Project, ProjectAssignment, Milestone, Payment,
    APIDocumentationPage, APIEndpoint
)
from projects.forms import (
    ProjectForm, MilestoneForm, PaymentForm,
    APIDocumentationPageForm, APIEndpointForm
)
from tasks.models import Task


@login_required
def list_projects(request):
    """List all projects with filtering and pagination"""
    user = request.user
    organization = user.organization
    
    # Base queryset
    queryset = Project.objects.select_related(
        'organization', 'project_manager', 'created_by'
    ).prefetch_related('assignments__user').all()
    
    # Filter by organization
    if organization:
        queryset = queryset.filter(organization=organization)
    
    # Role-based filtering
    if user.is_ceo:
        # CEO sees all projects
        pass
    elif user.is_pm:
        # PM sees projects they manage or are assigned to
        queryset = queryset.filter(
            Q(project_manager=user) | Q(assignments__user=user)
        ).distinct()
    elif user.is_dev or user.is_uiux:
        # Developers/UIUX see projects they're assigned to
        queryset = queryset.filter(assignments__user=user).distinct()
    elif user.is_bde:
        # BDE can see all projects (read-only)
        pass
    else:
        # HR and others: no access to projects
        queryset = Project.objects.none()
    
    # Filtering
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('search')
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)
    
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(client_name__icontains=search_query) |
            Q(client_company__icontains=search_query)
        )
    
    # Statistics (before filtering)
    stats_queryset = queryset
    total_projects = stats_queryset.count()
    in_progress = stats_queryset.filter(status='IN_PROGRESS').count()
    completed = stats_queryset.filter(status='COMPLETED').count()
    on_hold = stats_queryset.filter(status='ON_HOLD').count()
    
    # Ordering
    ordering = request.GET.get('ordering', '-created_at')
    queryset = queryset.order_by(ordering)
    
    # Pagination
    paginator = Paginator(queryset, 12)  # 12 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'total_projects': total_projects,
        'in_progress': in_progress,
        'completed': completed,
        'on_hold': on_hold,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'ordering': ordering,
        'can_create': user.is_ceo,
        'can_edit': user.is_ceo or user.is_pm,
        'user': user,
    }
    
    return render(request, 'projects/list.html', context)


@login_required
def detail_project(request, id):
    """Project detail view"""
    user = request.user
    
    # Get project with related data
    project = get_object_or_404(
        Project.objects.select_related(
            'organization', 'project_manager', 'created_by'
        ),
        id=id
    )
    
    # Check permissions
    if not user.is_ceo:
        if user.is_hr:
            return redirect('accounts:dashboard')
        if user.is_pm and project.project_manager != user:
            if not ProjectAssignment.objects.filter(project=project, user=user).exists():
                return redirect('projects:list')
        elif user.is_dev or user.is_uiux:
            if not ProjectAssignment.objects.filter(project=project, user=user).exists():
                return redirect('projects:list')
        elif not user.is_bde:
            return redirect('projects:list')
    
    # Get related data
    assignments = ProjectAssignment.objects.filter(
        project=project
    ).select_related('user')
    
    tasks = Task.objects.filter(project=project).select_related(
        'assigned_to', 'created_by'
    ).order_by('-created_at')[:10]
    
    total_tasks = Task.objects.filter(project=project).count()
    completed_tasks = Task.objects.filter(
        project=project, status='COMPLETED'
    ).count()
    
    # Get milestones with calculated days
    milestones_list = Milestone.objects.filter(
        project=project
    ).select_related('assigned_to', 'created_by').order_by('due_date', '-created_at')
    
    # Calculate days for each milestone
    milestones = []
    today = timezone.now().date()
    for milestone in milestones_list:
        if milestone.due_date:
            days = (milestone.due_date - today).days
            milestone.days_remaining = days
        else:
            milestone.days_remaining = None
        milestones.append(milestone)
    
    # Get payments
    payments = Payment.objects.filter(
        project=project
    ).select_related('milestone', 'created_by').order_by('-due_date', '-created_at')
    
    # Calculate payment statistics
    total_payment_amount = sum(p.amount for p in payments) if payments else 0
    total_paid_amount = sum(p.paid_amount for p in payments) if payments else 0
    remaining_payment_amount = total_payment_amount - total_paid_amount
    pending_payments = payments.filter(status__in=['PENDING', 'PARTIAL', 'OVERDUE']).count() if payments else 0
    
    # Calculate days remaining
    days_remaining = None
    days_overdue = None
    if project.deadline:
        today = timezone.now().date()
        days_remaining = (project.deadline - today).days
        if days_remaining < 0:
            days_overdue = abs(days_remaining)
            days_remaining = None
    
    # Check if user can view API documentation
    can_view_api_docs = False
    if user.is_ceo:
        can_view_api_docs = True
    elif user.is_pm and project.project_manager == user:
        can_view_api_docs = True
    elif (user.is_dev or user.is_uiux) and ProjectAssignment.objects.filter(
        project=project, user=user, is_active=True
    ).exists():
        can_view_api_docs = True
    
    context = {
        'project': project,
        'assignments': assignments,
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'milestones': milestones,
        'payments': payments,
        'total_payment_amount': total_payment_amount,
        'total_paid_amount': total_paid_amount,
        'remaining_payment_amount': remaining_payment_amount,
        'pending_payments': pending_payments,
        'days_remaining': days_remaining,
        'days_overdue': days_overdue,
        'can_edit': user.is_ceo or (user.is_pm and project.project_manager == user),
        'can_delete': user.is_ceo,
        'can_view_api_docs': can_view_api_docs,
    }
    
    return render(request, 'projects/detail.html', context)


@login_required
def create_project(request):
    """Create a new project"""
    user = request.user
    
    # Only CEO can create projects
    if not user.is_ceo:
        messages.error(request, 'You do not have permission to create projects.')
        return redirect('projects:list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=user)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = user
            project.save()
            
            # Save team member assignments (only for CEO)
            if user.is_ceo:
                # Get selected team members
                developers = form.cleaned_data.get('developers', [])
                uiux_designers = form.cleaned_data.get('uiux_designers', [])
                bde_users = form.cleaned_data.get('bde_users', [])
                
                # Create assignments for developers
                for dev in developers:
                    ProjectAssignment.objects.update_or_create(
                        project=project,
                        user=dev,
                        defaults={
                            'role': 'DEV',
                            'assigned_by': user,
                            'is_active': True
                        }
                    )
                
                # Create assignments for UIUX designers
                for uiux in uiux_designers:
                    ProjectAssignment.objects.update_or_create(
                        project=project,
                        user=uiux,
                        defaults={
                            'role': 'UIUX',
                            'assigned_by': user,
                            'is_active': True
                        }
                    )
                
                # Create assignments for BDE users
                for bde in bde_users:
                    ProjectAssignment.objects.update_or_create(
                        project=project,
                        user=bde,
                        defaults={
                            'role': 'BDE',
                            'assigned_by': user,
                            'is_active': True
                        }
                    )
            
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('projects:detail', id=project.id)
    else:
        form = ProjectForm(user=user)
    
    context = {
        'form': form,
        'title': 'Create New Project',
        'action': 'Create',
        'user': user
    }
    
    return render(request, 'projects/form.html', context)


@login_required
def update_project(request, id):
    """Update an existing project"""
    user = request.user
    project = get_object_or_404(Project, id=id)
    
    # Check permissions - CEO or PM managing this project
    if not user.is_ceo and not (user.is_pm and project.project_manager == user):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:detail', id=project.id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, user=user)
        if form.is_valid():
            # Handle status changes
            old_status = project.status
            project = form.save()
            new_status = project.status
            
            # Auto-set started_at when status changes to IN_PROGRESS
            if new_status == 'IN_PROGRESS' and not project.started_at:
                project.started_at = timezone.now()
                project.save()
            
            # Auto-set completed_at when status changes to COMPLETED
            if new_status == 'COMPLETED' and not project.completed_at:
                project.completed_at = timezone.now()
                project.completion_percentage = 100
                project.save()
            
            # Save team member assignments (only for CEO)
            if user.is_ceo:
                # Get selected team members
                developers = form.cleaned_data.get('developers', [])
                uiux_designers = form.cleaned_data.get('uiux_designers', [])
                bde_users = form.cleaned_data.get('bde_users', [])
                
                # Get all currently assigned users for this project
                current_assignments = ProjectAssignment.objects.filter(
                    project=project,
                    role__in=['DEV', 'UIUX', 'BDE']
                )
                
                # Deactivate assignments that are no longer selected
                selected_user_ids = set()
                selected_user_ids.update([u.id for u in developers])
                selected_user_ids.update([u.id for u in uiux_designers])
                selected_user_ids.update([u.id for u in bde_users])
                
                for assignment in current_assignments:
                    if assignment.user_id not in selected_user_ids:
                        assignment.is_active = False
                        assignment.save()
                
                # Create/update assignments for developers
                for dev in developers:
                    ProjectAssignment.objects.update_or_create(
                        project=project,
                        user=dev,
                        defaults={
                            'role': 'DEV',
                            'assigned_by': user,
                            'is_active': True
                        }
                    )
                
                # Create/update assignments for UIUX designers
                for uiux in uiux_designers:
                    ProjectAssignment.objects.update_or_create(
                        project=project,
                        user=uiux,
                        defaults={
                            'role': 'UIUX',
                            'assigned_by': user,
                            'is_active': True
                        }
                    )
                
                # Create/update assignments for BDE users
                for bde in bde_users:
                    ProjectAssignment.objects.update_or_create(
                        project=project,
                        user=bde,
                        defaults={
                            'role': 'BDE',
                            'assigned_by': user,
                            'is_active': True
                        }
                    )
            
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('projects:detail', id=project.id)
    else:
        form = ProjectForm(instance=project, user=user)
    
    context = {
        'form': form,
        'project': project,
        'title': f'Edit Project: {project.name}',
        'action': 'Update',
        'user': user
    }
    
    return render(request, 'projects/form.html', context)


@login_required
def delete_project(request, id):
    """Delete a project"""
    user = request.user
    project = get_object_or_404(Project, id=id)
    
    # Only CEO can delete projects
    if not user.is_ceo:
        messages.error(request, 'You do not have permission to delete projects.')
        return redirect('projects:detail', id=project.id)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('projects:list')
    
    context = {
        'project': project
    }
    
    return render(request, 'projects/delete_confirm.html', context)


# Milestone Management Views
@login_required
def create_milestone(request, project_id):
    """Create a new milestone for a project"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    if not user.is_ceo and not (user.is_pm and project.project_manager == user):
        messages.error(request, 'You do not have permission to create milestones.')
        return redirect('projects:detail', id=project_id)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, project=project, user=user)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.created_by = user
            milestone.save()
            messages.success(request, f'Milestone "{milestone.name}" created successfully!')
            return redirect('projects:detail', id=project_id)
    else:
        form = MilestoneForm(project=project, user=user)
    
    context = {
        'form': form,
        'project': project,
        'title': 'Create New Milestone',
        'action': 'Create'
    }
    
    return render(request, 'projects/milestone_form.html', context)


@login_required
def update_milestone(request, project_id, milestone_id):
    """Update an existing milestone"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    milestone = get_object_or_404(Milestone, id=milestone_id, project=project)
    
    # Check permissions
    if not user.is_ceo and not (user.is_pm and project.project_manager == user):
        messages.error(request, 'You do not have permission to edit milestones.')
        return redirect('projects:detail', id=project_id)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone, project=project, user=user)
        if form.is_valid():
            milestone = form.save()
            # Auto-set completed_date when status changes to COMPLETED
            if milestone.status == 'COMPLETED' and not milestone.completed_date:
                milestone.completed_date = timezone.now().date()
                milestone.completion_percentage = 100
                milestone.save()
            messages.success(request, f'Milestone "{milestone.name}" updated successfully!')
            return redirect('projects:detail', id=project_id)
    else:
        form = MilestoneForm(instance=milestone, project=project, user=user)
    
    context = {
        'form': form,
        'project': project,
        'milestone': milestone,
        'title': f'Edit Milestone: {milestone.name}',
        'action': 'Update'
    }
    
    return render(request, 'projects/milestone_form.html', context)


@login_required
def delete_milestone(request, project_id, milestone_id):
    """Delete a milestone"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    milestone = get_object_or_404(Milestone, id=milestone_id, project=project)
    
    # Check permissions
    if not user.is_ceo and not (user.is_pm and project.project_manager == user):
        messages.error(request, 'You do not have permission to delete milestones.')
        return redirect('projects:detail', id=project_id)
    
    if request.method == 'POST':
        milestone_name = milestone.name
        milestone.delete()
        messages.success(request, f'Milestone "{milestone_name}" deleted successfully!')
        return redirect('projects:detail', id=project_id)
    
    context = {
        'project': project,
        'milestone': milestone
    }
    
    return render(request, 'projects/milestone_delete_confirm.html', context)


# Payment Management Views
@login_required
def create_payment(request, project_id):
    """Create a new payment for a project"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions - CEO and PM can create payments
    if not user.is_ceo and not (user.is_pm and project.project_manager == user):
        messages.error(request, 'You do not have permission to create payments.')
        return redirect('projects:detail', id=project_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, project=project)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.project = project
            payment.created_by = user
            payment.save()
            messages.success(request, f'Payment of ₹{payment.amount} created successfully!')
            return redirect('projects:detail', id=project_id)
    else:
        form = PaymentForm(project=project)
    
    context = {
        'form': form,
        'project': project,
        'title': 'Create New Payment',
        'action': 'Create'
    }
    
    return render(request, 'projects/payment_form.html', context)


@login_required
def update_payment(request, project_id, payment_id):
    """Update an existing payment"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    payment = get_object_or_404(Payment, id=payment_id, project=project)
    
    # Check permissions
    if not user.is_ceo and not (user.is_pm and project.project_manager == user):
        messages.error(request, 'You do not have permission to edit payments.')
        return redirect('projects:detail', id=project_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment, project=project)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment updated successfully!')
            return redirect('projects:detail', id=project_id)
    else:
        form = PaymentForm(instance=payment, project=project)
    
    context = {
        'form': form,
        'project': project,
        'payment': payment,
        'title': f'Edit Payment',
        'action': 'Update'
    }
    
    return render(request, 'projects/payment_form.html', context)


@login_required
def delete_payment(request, project_id, payment_id):
    """Delete a payment"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    payment = get_object_or_404(Payment, id=payment_id, project=project)
    
    # Check permissions
    if not user.is_ceo and not (user.is_pm and project.project_manager == user):
        messages.error(request, 'You do not have permission to delete payments.')
        return redirect('projects:detail', id=project_id)
    
    if request.method == 'POST':
        payment_amount = payment.amount
        payment.delete()
        messages.success(request, f'Payment of ₹{payment_amount} deleted successfully!')
        return redirect('projects:detail', id=project_id)
    
    context = {
        'project': project,
        'payment': payment
    }
    
    return render(request, 'projects/payment_delete_confirm.html', context)


# API Documentation Views
def can_manage_api_docs(user, project):
    """Check if user can manage API documentation for a project"""
    if user.is_ceo:
        return True
    elif user.is_pm and project.project_manager == user:
        return True
    elif (user.is_dev or user.is_uiux) and ProjectAssignment.objects.filter(
        project=project, user=user, is_active=True
    ).exists():
        return True
    return False


@login_required
def api_documentation_index(request):
    """List all projects with API documentation access"""
    user = request.user
    
    # Get projects user can access
    if user.is_ceo:
        projects = Project.objects.filter(
            organization=user.organization
        ).prefetch_related('api_documentation_pages').order_by('-created_at')
    elif user.is_pm:
        projects = Project.objects.filter(
            organization=user.organization,
            project_manager=user
        ).prefetch_related('api_documentation_pages').order_by('-created_at')
    elif user.is_dev or user.is_uiux:
        projects = Project.objects.filter(
            organization=user.organization,
            assignments__user=user,
            assignments__is_active=True
        ).distinct().prefetch_related('api_documentation_pages').order_by('-created_at')
    else:
        projects = Project.objects.none()
    
    # Count API pages for each project
    for project in projects:
        project.api_pages_count = project.api_documentation_pages.count()
    
    context = {
        'projects': projects,
        'user': user
    }
    
    return render(request, 'projects/api_documentation_index.html', context)


@login_required
def api_documentation(request, project_id):
    """View API documentation for a project"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions - CEO, PM, or assigned developers/UIUX can view
    can_view = False
    if user.is_ceo:
        can_view = True
    elif user.is_pm and project.project_manager == user:
        can_view = True
    elif (user.is_dev or user.is_uiux) and ProjectAssignment.objects.filter(
        project=project, user=user, is_active=True
    ).exists():
        can_view = True
    
    if not can_view:
        messages.error(request, 'You do not have permission to view API documentation for this project.')
        return redirect('projects:detail', id=project_id)
    
    # Get all pages with their endpoints
    pages = APIDocumentationPage.objects.filter(
        project=project
    ).prefetch_related('api_endpoints').order_by('order', 'page_name')
    
    # Check if user can manage (CEO, PM, or assigned developers/UIUX)
    can_manage = can_manage_api_docs(user, project)
    
    context = {
        'project': project,
        'pages': pages,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'projects/api_documentation.html', context)


@login_required
def create_api_page(request, project_id):
    """Create a new API documentation page"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user can manage API documentation
    if not can_manage_api_docs(user, project):
        messages.error(request, 'You do not have permission to create API documentation pages.')
        return redirect('projects:api_documentation', project_id=project_id)
    
    if request.method == 'POST':
        form = APIDocumentationPageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.project = project
            page.created_by = user
            page.save()
            messages.success(request, f'API documentation page "{page.page_name}" created successfully!')
            return redirect('projects:api_documentation', project_id=project_id)
    else:
        form = APIDocumentationPageForm()
    
    context = {
        'form': form,
        'project': project,
        'title': 'Create API Documentation Page',
        'action': 'Create'
    }
    
    return render(request, 'projects/api_page_form.html', context)


@login_required
def update_api_page(request, project_id, page_id):
    """Update an API documentation page"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    page = get_object_or_404(APIDocumentationPage, id=page_id, project=project)
    
    # Check if user can manage API documentation
    if not can_manage_api_docs(user, project):
        messages.error(request, 'You do not have permission to edit API documentation pages.')
        return redirect('projects:api_documentation', project_id=project_id)
    
    if request.method == 'POST':
        form = APIDocumentationPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, f'API documentation page "{page.page_name}" updated successfully!')
            return redirect('projects:api_documentation', project_id=project_id)
    else:
        form = APIDocumentationPageForm(instance=page)
    
    context = {
        'form': form,
        'project': project,
        'page': page,
        'title': f'Edit API Documentation Page: {page.page_name}',
        'action': 'Update'
    }
    
    return render(request, 'projects/api_page_form.html', context)


@login_required
def delete_api_page(request, project_id, page_id):
    """Delete an API documentation page"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    page = get_object_or_404(APIDocumentationPage, id=page_id, project=project)
    
    # Check if user can manage API documentation
    if not can_manage_api_docs(user, project):
        messages.error(request, 'You do not have permission to delete API documentation pages.')
        return redirect('projects:api_documentation', project_id=project_id)
    
    if request.method == 'POST':
        page_name = page.page_name
        page.delete()
        messages.success(request, f'API documentation page "{page_name}" deleted successfully!')
        return redirect('projects:api_documentation', project_id=project_id)
    
    context = {
        'project': project,
        'page': page
    }
    
    return render(request, 'projects/api_page_delete_confirm.html', context)


@login_required
def create_api_endpoint(request, project_id, page_id):
    """Create a new API endpoint"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    page = get_object_or_404(APIDocumentationPage, id=page_id, project=project)
    
    # Check if user can manage API documentation
    if not can_manage_api_docs(user, project):
        messages.error(request, 'You do not have permission to create API endpoints.')
        return redirect('projects:api_documentation', project_id=project_id)
    
    if request.method == 'POST':
        form = APIEndpointForm(request.POST, project=project)
        if form.is_valid():
            endpoint = form.save(commit=False)
            endpoint.project = project
            endpoint.created_by = user
            endpoint.save()
            messages.success(request, f'API endpoint "{endpoint.name}" created successfully!')
            return redirect('projects:api_documentation', project_id=project_id)
    else:
        form = APIEndpointForm(project=project)
        form.fields['page'].initial = page
    
    context = {
        'form': form,
        'project': project,
        'page': page,
        'title': f'Create API Endpoint for {page.page_name}',
        'action': 'Create'
    }
    
    return render(request, 'projects/api_endpoint_form.html', context)


@login_required
def update_api_endpoint(request, project_id, endpoint_id):
    """Update an API endpoint"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    endpoint = get_object_or_404(APIEndpoint, id=endpoint_id, project=project)
    
    # Check if user can manage API documentation
    if not can_manage_api_docs(user, project):
        messages.error(request, 'You do not have permission to edit API endpoints.')
        return redirect('projects:api_documentation', project_id=project_id)
    
    if request.method == 'POST':
        form = APIEndpointForm(request.POST, instance=endpoint, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'API endpoint "{endpoint.name}" updated successfully!')
            return redirect('projects:api_documentation', project_id=project_id)
    else:
        form = APIEndpointForm(instance=endpoint, project=project)
    
    context = {
        'form': form,
        'project': project,
        'endpoint': endpoint,
        'title': f'Edit API Endpoint: {endpoint.name}',
        'action': 'Update'
    }
    
    return render(request, 'projects/api_endpoint_form.html', context)


@login_required
def delete_api_endpoint(request, project_id, endpoint_id):
    """Delete an API endpoint"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)
    endpoint = get_object_or_404(APIEndpoint, id=endpoint_id, project=project)
    
    # Check if user can manage API documentation
    if not can_manage_api_docs(user, project):
        messages.error(request, 'You do not have permission to delete API endpoints.')
        return redirect('projects:api_documentation', project_id=project_id)
    
    if request.method == 'POST':
        endpoint_name = endpoint.name
        endpoint.delete()
        messages.success(request, f'API endpoint "{endpoint_name}" deleted successfully!')
        return redirect('projects:api_documentation', project_id=project_id)
    
    context = {
        'project': project,
        'endpoint': endpoint
    }
    
    return render(request, 'projects/api_endpoint_delete_confirm.html', context)
