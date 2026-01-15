from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, TaskComment, TaskActivity
from tasks.forms import TaskForm
from tasks.utils import create_task_notification, check_deadline_notifications
from projects.models import Project, ProjectAssignment
from accounts.models import User


@login_required
def list_tasks(request):
    """List all tasks with filtering and search"""
    user = request.user

    # Get base queryset based on role - following same pattern as projects list
    organization = user.organization

    # Base queryset
    tasks = Task.objects.select_related("project", "assigned_to", "created_by").all()

    # Filter by organization first
    if organization:
        tasks = tasks.filter(project__organization=organization)

    # Role-based filtering
    if user.is_ceo:
        # CEO sees all tasks in their organization
        pass
    elif user.is_pm:
        # PM sees tasks from projects they manage or are assigned to
        tasks = tasks.filter(
            Q(project__project_manager=user) | Q(project__assignments__user=user)
        ).distinct()
    elif user.is_hr or user.is_bde:
        # HR and BDE can see all tasks (read-only)
        pass
    elif user.is_dev or user.is_uiux:
        # Developers/UIUX see tasks assigned to them or from their projects
        tasks = tasks.filter(
            Q(assigned_to=user) | Q(project__assignments__user=user)
        ).distinct()
    else:
        tasks = Task.objects.none()

    # Apply filters
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    project_filter = request.GET.get("project")
    assigned_to_filter = request.GET.get("assigned_to")
    search_query = request.GET.get("search")

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        try:
            project_id = int(project_filter)
            tasks = tasks.filter(project_id=project_id)
        except (ValueError, TypeError):
            pass  # Invalid project filter, ignore it
    if assigned_to_filter:
        tasks = tasks.filter(assigned_to_id=assigned_to_filter)
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(project__name__icontains=search_query)
        )

    # Get available projects for filter - following same pattern as projects list view
    # Base queryset
    projects_queryset = (
        Project.objects.select_related("organization", "project_manager", "created_by")
        .prefetch_related("assignments__user")
        .all()
    )

    # Filter by organization first (if user has one)
    if organization:
        projects_queryset = projects_queryset.filter(organization=organization)

    # Role-based filtering
    if user.is_ceo:
        # CEO sees all projects (in their org if they have one, otherwise all)
        pass
    elif user.is_pm:
        # PM sees projects they manage or are assigned to
        projects_queryset = projects_queryset.filter(
            Q(project_manager=user)
            | Q(assignments__user=user, assignments__is_active=True)
        ).distinct()
    elif user.is_hr or user.is_bde:
        # HR and BDE can see all projects in their organization (read-only)
        if not organization:
            projects_queryset = Project.objects.none()
    elif user.is_dev or user.is_uiux:
        # Developers/UIUX see projects they're assigned to
        projects_queryset = projects_queryset.filter(
            assignments__user=user, assignments__is_active=True
        ).distinct()
    else:
        projects_queryset = Project.objects.none()

    # Order by name
    projects = projects_queryset.order_by("name")

    # Get available users for filter
    if user.organization:
        users = User.objects.filter(
            organization=user.organization, role__name__in=["Dev", "UIUX", "BDE"]
        )
    else:
        users = User.objects.filter(role__name__in=["Dev", "UIUX", "BDE"])

    # Statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status="COMPLETED").count()
    in_progress_tasks = tasks.filter(status="IN_PROGRESS").count()
    overdue_tasks = tasks.filter(is_overdue=True).count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Order by
    order_by = request.GET.get("order_by", "-created_at")
    tasks = tasks.select_related("project", "assigned_to", "created_by").order_by(
        order_by
    )

    context = {
        "tasks": tasks,
        "projects": projects,
        "users": users,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "project_filter": project_filter,
        "assigned_to_filter": assigned_to_filter,
        "search_query": search_query,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": completion_rate,
        "user": user,
        "can_create": user.is_ceo or user.is_pm,  # Add can_create flag
    }

    return render(request, "tasks/list.html", context)


@login_required
def my_tasks(request):
    """View tasks assigned to the current user"""
    user = request.user

    tasks = Task.objects.filter(assigned_to=user).select_related(
        "project", "created_by"
    )

    # Apply filters
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    project_filter = request.GET.get("project")
    search_query = request.GET.get("search")

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(project__name__icontains=search_query)
        )

    # Get user's projects
    projects = Project.objects.filter(
        assignments__user=user, assignments__is_active=True
    ).distinct()

    # Statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status="COMPLETED").count()
    in_progress_tasks = tasks.filter(status="IN_PROGRESS").count()
    overdue_tasks = tasks.filter(is_overdue=True).count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Order by
    order_by = request.GET.get("order_by", "-created_at")
    tasks = tasks.order_by(order_by)

    context = {
        "tasks": tasks,
        "projects": projects,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "project_filter": project_filter,
        "search_query": search_query,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": completion_rate,
        "user": user,
    }

    return render(request, "tasks/my_tasks.html", context)


@login_required
def detail_task(request, id):
    """Task detail view"""
    user = request.user
    task = get_object_or_404(
        Task.objects.select_related("project", "assigned_to", "created_by"), id=id
    )

    # Check permissions
    if not user.is_ceo:
        if user.is_pm and task.project.project_manager != user:
            if not ProjectAssignment.objects.filter(
                project=task.project, user=user
            ).exists():
                if task.assigned_to != user:
                    return redirect("tasks:list")
        elif user.is_dev or user.is_uiux or user.is_bde:
            if (
                task.assigned_to != user
                and not ProjectAssignment.objects.filter(
                    project=task.project, user=user
                ).exists()
            ):
                return redirect("tasks:list")
        elif not (user.is_hr or user.is_bde):
            return redirect("tasks:list")

    # Get comments
    comments = (
        TaskComment.objects.filter(task=task)
        .select_related("user")
        .order_by("-created_at")
    )

    # Get activities
    activities = (
        TaskActivity.objects.filter(task=task)
        .select_related("user")
        .order_by("-created_at")[:20]
    )

    # Calculate days remaining
    days_remaining = None
    days_overdue = None
    if task.deadline:
        now = timezone.now()
        delta = task.deadline - now
        days_remaining = delta.days
        if days_remaining < 0:
            days_overdue = abs(days_remaining)
            days_remaining = None

    # Check if user can edit
    can_edit = (
        user.is_ceo
        or (user.is_pm and task.project.project_manager == user)
        or task.assigned_to == user
    )

    context = {
        "task": task,
        "comments": comments,
        "activities": activities,
        "days_remaining": days_remaining,
        "days_overdue": days_overdue,
        "can_edit": can_edit,
        "user": user,
    }

    return render(request, "tasks/detail.html", context)


@login_required
def create_task(request):
    """Create a new task"""
    user = request.user

    # Check permissions - only CEO and PM can create tasks
    if not (user.is_ceo or user.is_pm):
        messages.error(request, "You do not have permission to create tasks.")
        return redirect("tasks:list")

    project_id = request.GET.get("project")

    if request.method == "POST":
        form = TaskForm(request.POST, user=user, project_id=project_id)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = user
            task.save()

            # Create activity log
            TaskActivity.objects.create(
                task=task,
                user=user,
                action="CREATED",
                description=f'Task "{task.title}" created',
            )

            # Create notification if assigned
            if task.assigned_to:
                create_task_notification(task, "assigned", user)

            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect("tasks:detail", id=task.id)
    else:
        form = TaskForm(user=user, project_id=project_id)

    context = {"form": form, "title": "Create New Task", "action": "Create"}

    return render(request, "tasks/form.html", context)


@login_required
def update_task(request, id):
    """Update an existing task"""
    user = request.user
    task = get_object_or_404(Task, id=id)

    # Check permissions
    can_edit = (
        user.is_ceo
        or (user.is_pm and task.project.project_manager == user)
        or task.assigned_to == user
    )
    if not can_edit:
        messages.error(request, "You do not have permission to edit this task.")
        return redirect("tasks:detail", id=id)

    old_assigned_to = task.assigned_to
    old_status = task.status

    if request.method == "POST":
        form = TaskForm(
            request.POST, instance=task, user=user, project_id=task.project.id
        )
        if form.is_valid():
            task = form.save()

            # Create activity log
            changes = []
            if old_status != task.status:
                changes.append(
                    f"Status changed from {task.get_status_display()} to {task.get_status_display()}"
                )
                TaskActivity.objects.create(
                    task=task,
                    user=user,
                    action="STATUS_CHANGED",
                    description=f"Status changed from {old_status} to {task.status}",
                    old_value=old_status,
                    new_value=task.status,
                )

            if old_assigned_to != task.assigned_to:
                changes.append(f"Assignment changed")
                TaskActivity.objects.create(
                    task=task,
                    user=user,
                    action="ASSIGNED",
                    description=f"Task reassigned",
                    old_value=str(old_assigned_to) if old_assigned_to else "Unassigned",
                    new_value=(
                        str(task.assigned_to) if task.assigned_to else "Unassigned"
                    ),
                )

                # Create notification for new assignee
                if task.assigned_to:
                    create_task_notification(task, "assigned", user)

            if changes:
                TaskActivity.objects.create(
                    task=task,
                    user=user,
                    action="UPDATED",
                    description=f'Task updated: {", ".join(changes)}',
                )
            else:
                TaskActivity.objects.create(
                    task=task,
                    user=user,
                    action="UPDATED",
                    description="Task details updated",
                )

            # Notify assignee of update
            if task.assigned_to and old_assigned_to == task.assigned_to:
                create_task_notification(task, "updated", user)

            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect("tasks:detail", id=task.id)
    else:
        form = TaskForm(instance=task, user=user, project_id=task.project.id)

    context = {
        "form": form,
        "task": task,
        "title": f"Edit Task: {task.title}",
        "action": "Update",
    }

    return render(request, "tasks/form.html", context)


@login_required
def delete_task(request, id):
    """Delete a task"""
    user = request.user
    task = get_object_or_404(Task, id=id)

    # Check permissions - only CEO and PM can delete
    if not (user.is_ceo or (user.is_pm and task.project.project_manager == user)):
        messages.error(request, "You do not have permission to delete tasks.")
        return redirect("tasks:detail", id=id)

    if request.method == "POST":
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect("tasks:list")

    context = {"task": task}

    return render(request, "tasks/delete_confirm.html", context)


@login_required
def kanban_board(request, project_id=None):
    """Kanban board view for tasks"""
    user = request.user

    # Get project if specified
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Check permissions
        if not user.is_ceo:
            if user.is_pm and project.project_manager != user:
                if not ProjectAssignment.objects.filter(
                    project=project, user=user
                ).exists():
                    return redirect("tasks:list")
            elif user.is_dev or user.is_uiux or user.is_bde:
                if not ProjectAssignment.objects.filter(
                    project=project, user=user
                ).exists():
                    return redirect("tasks:list")

    # Get tasks based on project and user role
    if project:
        if user.is_ceo or (user.is_pm and project.project_manager == user):
            tasks = Task.objects.filter(project=project)
        else:
            tasks = Task.objects.filter(project=project, assigned_to=user)
    else:
        # Get all tasks user can see
        if user.is_ceo:
            tasks = Task.objects.filter(project__organization=user.organization)
        elif user.is_pm:
            tasks = Task.objects.filter(
                Q(project__project_manager=user) | Q(project__assignments__user=user)
            ).distinct()
        else:
            tasks = Task.objects.filter(assigned_to=user)

    # Group tasks by status
    status_groups = {
        "TO_DO": tasks.filter(status="TO_DO").select_related(
            "project", "assigned_to", "created_by"
        ),
        "IN_PROGRESS": tasks.filter(status="IN_PROGRESS").select_related(
            "project", "assigned_to", "created_by"
        ),
        "COMPLETED": tasks.filter(status="COMPLETED").select_related(
            "project", "assigned_to", "created_by"
        ),
        "BLOCKED": tasks.filter(status="BLOCKED").select_related(
            "project", "assigned_to", "created_by"
        ),
    }

    # Get available projects for filter
    # Get available projects for filter - following same pattern as projects list view
    organization = user.organization

    # Base queryset
    projects_queryset = (
        Project.objects.select_related("organization", "project_manager", "created_by")
        .prefetch_related("assignments__user")
        .all()
    )

    # Filter by organization first
    if organization:
        projects_queryset = projects_queryset.filter(organization=organization)

    # Role-based filtering
    if user.is_ceo:
        # CEO sees all projects
        pass
    elif user.is_pm:
        # PM sees projects they manage or are assigned to
        projects_queryset = projects_queryset.filter(
            Q(project_manager=user) | Q(assignments__user=user)
        ).distinct()
    elif user.is_hr or user.is_bde:
        # HR and BDE can see all projects (read-only)
        pass
    elif user.is_dev or user.is_uiux:
        # Developers/UIUX see projects they're assigned to
        projects_queryset = projects_queryset.filter(assignments__user=user).distinct()
    else:
        projects_queryset = Project.objects.none()

    # Order by name
    projects = projects_queryset.order_by("name")

    context = {
        "project": project,
        "projects": projects,
        "status_groups": status_groups,
        "user": user,
    }

    return render(request, "tasks/kanban.html", context)


@login_required
def update_task_status(request, id):
    """Update task status via AJAX (for drag-and-drop)"""
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import json

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    user = request.user
    task = get_object_or_404(Task, id=id)

    # Check permissions
    can_edit = (
        user.is_ceo
        or (user.is_pm and task.project.project_manager == user)
        or task.assigned_to == user
    )
    if not can_edit:
        return JsonResponse(
            {"error": "You do not have permission to update this task."}, status=403
        )

    # Get new status from request
    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({"error": f"Invalid JSON: {str(e)}"}, status=400)

    new_status = data.get("status")

    if not new_status:
        return JsonResponse({"error": "Status is required"}, status=400)

    # Validate status
    valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse(
            {"error": f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
            status=400,
        )

    # Update task status
    old_status = task.status
    if old_status == new_status:
        return JsonResponse(
            {
                "success": True,
                "message": "Status unchanged",
                "task_id": task.id,
                "new_status": new_status,
            }
        )

    task.status = new_status
    task.save()

    # Create activity log
    TaskActivity.objects.create(
        task=task,
        user=user,
        action="STATUS_CHANGED",
        description=f"Status changed from {old_status} to {new_status} via Kanban board",
        old_value=old_status,
        new_value=new_status,
    )

    # Notify assignee if status changed
    if task.assigned_to and old_status != new_status:
        create_task_notification(task, "updated", user)

    return JsonResponse(
        {
            "success": True,
            "message": f"Task status updated to {task.get_status_display()}",
            "task_id": task.id,
            "new_status": new_status,
        }
    )


@login_required
def task_reporting(request):
    """Task reporting and statistics"""
    user = request.user

    # Get base queryset
    if user.is_ceo:
        tasks = Task.objects.filter(project__organization=user.organization)
    elif user.is_pm:
        tasks = Task.objects.filter(
            Q(project__project_manager=user) | Q(project__assignments__user=user)
        ).distinct()
    else:
        tasks = Task.objects.filter(assigned_to=user)

    # Overall statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status="COMPLETED").count()
    in_progress_tasks = tasks.filter(status="IN_PROGRESS").count()
    blocked_tasks = tasks.filter(status="BLOCKED").count()
    overdue_tasks = tasks.filter(is_overdue=True).count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Tasks by priority
    priority_stats = (
        tasks.values("priority").annotate(count=Count("id")).order_by("priority")
    )

    # Tasks by status
    status_stats = tasks.values("status").annotate(count=Count("id")).order_by("status")

    # Tasks by project
    project_stats = (
        tasks.values("project__name")
        .annotate(
            total=Count("id"),
            completed=Count("id", filter=Q(status="COMPLETED")),
            in_progress=Count("id", filter=Q(status="IN_PROGRESS")),
            overdue=Count("id", filter=Q(is_overdue=True)),
        )
        .order_by("-total")[:10]
    )

    # User performance (if CEO or PM)
    user_performance = None
    if user.is_ceo or user.is_pm:
        user_performance = (
            tasks.values(
                "assigned_to__username",
                "assigned_to__first_name",
                "assigned_to__last_name",
            )
            .annotate(
                total=Count("id"),
                completed=Count("id", filter=Q(status="COMPLETED")),
                in_progress=Count("id", filter=Q(status="IN_PROGRESS")),
                overdue=Count("id", filter=Q(is_overdue=True)),
            )
            .annotate(completion_rate=Avg("status", filter=Q(status="COMPLETED")))
            .order_by("-total")[:10]
        )

    # Recent completed tasks
    recent_completed = (
        tasks.filter(status="COMPLETED")
        .select_related("project", "assigned_to")
        .order_by("-completed_at")[:10]
    )

    context = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "blocked_tasks": blocked_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": completion_rate,
        "priority_stats": priority_stats,
        "status_stats": status_stats,
        "project_stats": project_stats,
        "user_performance": user_performance,
        "recent_completed": recent_completed,
        "user": user,
    }

    return render(request, "tasks/reporting.html", context)
