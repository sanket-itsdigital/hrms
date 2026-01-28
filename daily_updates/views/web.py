from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from daily_updates.models import DailyUpdate
from daily_updates.forms import DailyUpdateForm
from projects.models import Project
from accounts.models import User


@login_required
def list_daily_updates(request):
    """List daily updates with filtering"""
    user = request.user

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    organization = user.organization

    # Get base queryset based on role
    if user.is_ceo:
        # CEO can view all users' daily tasks (view only, cannot add)
        updates = DailyUpdate.objects.filter(organization=organization)
    elif user.is_pm:
        # PM can view own updates and updates for projects they manage (view + add)
        updates = (
            DailyUpdate.objects.filter(organization=organization)
            .filter(Q(user=user) | Q(project__project_manager=user))
            .distinct()
        )
    else:
        # DEV, UIUX, BDE, HR: can add daily task and see their own
        updates = DailyUpdate.objects.filter(organization=organization, user=user)

    # Apply filters
    search_query = request.GET.get("search", "")
    project_filter = request.GET.get("project", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    user_filter = request.GET.get("user", "")

    if search_query:
        updates = updates.filter(
            Q(description__icontains=search_query)
            | Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(project__name__icontains=search_query)
        )

    if project_filter:
        try:
            updates = updates.filter(project_id=int(project_filter))
        except (ValueError, TypeError):
            pass

    if date_from:
        try:
            updates = updates.filter(
                date__gte=datetime.strptime(date_from, "%Y-%m-%d").date()
            )
        except ValueError:
            pass

    if date_to:
        try:
            updates = updates.filter(
                date__lte=datetime.strptime(date_to, "%Y-%m-%d").date()
            )
        except ValueError:
            pass

    if user_filter and user.is_ceo:
        try:
            updates = updates.filter(user_id=int(user_filter))
        except (ValueError, TypeError):
            pass

    # Order by date (newest first)
    updates = updates.select_related("user", "project", "organization").order_by(
        "-date", "-created_at"
    )

    # Pagination
    paginator = Paginator(updates, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get available projects for filter
    if user.is_ceo:
        projects = Project.objects.filter(organization=organization).order_by("name")
    elif user.is_pm:
        projects = Project.objects.filter(
            organization=organization, project_manager=user
        ).order_by("name")
    elif user.is_dev or user.is_uiux:
        projects = (
            Project.objects.filter(
                organization=organization,
                assignments__user=user,
                assignments__is_active=True,
            )
            .distinct()
            .order_by("name")
        )
    elif user.is_hr or user.is_bde:
        projects = Project.objects.filter(organization=organization).order_by("name")
    else:
        projects = Project.objects.none()

    # Statistics
    total_updates = updates.count()
    this_month = updates.filter(
        date__year=timezone.now().year, date__month=timezone.now().month
    ).count()
    this_week = updates.filter(
        date__gte=timezone.now().date() - timedelta(days=7)
    ).count()

    # CEO: view only. PM + all others (DEV, UIUX, BDE, HR): can add. PM/DEV/UIUX/BDE/HR can edit own; PM can edit project updates too.
    can_create = not user.is_ceo
    can_edit_any = (
        user.is_pm
    )  # PM can edit own + project's; others edit own only (checked per-update)

    # Users list for CEO filter (users in org who have submitted at least one update, or all org users)
    users = []
    if user.is_ceo:
        users = (
            User.objects.filter(organization=organization, is_active=True)
            .exclude(role__name="CEO")
            .order_by("first_name", "last_name", "email")
        )

    context = {
        "page_obj": page_obj,
        "updates": page_obj,
        "projects": projects,
        "users": users,
        "total_updates": total_updates,
        "this_month": this_month,
        "this_week": this_week,
        "search_query": search_query,
        "project_filter": project_filter,
        "date_from": date_from,
        "date_to": date_to,
        "user_filter": user_filter,
        "can_create": can_create,
        "can_edit_any": can_edit_any,
    }

    return render(request, "daily_updates/list.html", context)


@login_required
def create_daily_update(request):
    """Create a new daily update. All roles except CEO can add."""
    user = request.user

    # CEO is view-only; all others (PM, DEV, UIUX, BDE, HR) can add
    if user.is_ceo:
        messages.error(request, "You do not have permission to create daily updates.")
        return redirect("daily_updates:list")

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = DailyUpdateForm(request.POST, user=user)
        if form.is_valid():
            daily_update = form.save(commit=False)
            daily_update.user = user
            daily_update.organization = user.organization
            daily_update.save()
            messages.success(request, "Daily update created successfully!")
            return redirect("daily_updates:list")
    else:
        form = DailyUpdateForm(user=user)

    return render(
        request,
        "daily_updates/form.html",
        {"form": form, "title": "Submit Daily Update"},
    )


@login_required
def update_daily_update(request, id):
    """Update an existing daily update"""
    user = request.user

    daily_update = get_object_or_404(DailyUpdate, id=id)

    # CEO is view-only; cannot edit
    if user.is_ceo:
        messages.error(request, "You do not have permission to edit daily updates.")
        return redirect("daily_updates:list")
    if user.is_pm:
        # PM can edit own updates and updates for projects they manage
        if daily_update.user != user and daily_update.project.project_manager != user:
            messages.error(
                request, "You do not have permission to edit this daily update."
            )
            return redirect("daily_updates:list")
    else:
        # DEV, UIUX, BDE, HR can only edit their own updates
        if daily_update.user != user:
            messages.error(request, "You can only edit your own daily updates.")
            return redirect("daily_updates:list")

    if request.method == "POST":
        form = DailyUpdateForm(request.POST, instance=daily_update, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Daily update updated successfully!")
            return redirect("daily_updates:list")
    else:
        form = DailyUpdateForm(instance=daily_update, user=user)

    return render(
        request,
        "daily_updates/form.html",
        {"form": form, "daily_update": daily_update, "title": "Update Daily Update"},
    )


@login_required
def delete_daily_update(request, id):
    """Delete a daily update"""
    user = request.user

    daily_update = get_object_or_404(DailyUpdate, id=id)

    # CEO is view-only; cannot delete
    if user.is_ceo:
        messages.error(request, "You do not have permission to delete daily updates.")
        return redirect("daily_updates:list")
    if user.is_pm:
        # PM can delete own updates and updates for projects they manage
        if daily_update.user != user and daily_update.project.project_manager != user:
            messages.error(
                request, "You do not have permission to delete this daily update."
            )
            return redirect("daily_updates:list")
    else:
        # DEV, UIUX, BDE, HR can only delete their own updates
        if daily_update.user != user:
            messages.error(request, "You can only delete your own daily updates.")
            return redirect("daily_updates:list")

    if request.method == "POST":
        daily_update.delete()
        messages.success(request, "Daily update deleted successfully!")
        return redirect("daily_updates:list")

    return render(
        request, "daily_updates/delete_confirm.html", {"daily_update": daily_update}
    )
