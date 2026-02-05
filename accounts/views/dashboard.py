from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from projects.models import Project
from tasks.models import Task
from attendance.models import Attendance
from leaves.models import Leave
from leads_crm.models import Lead
from daily_updates.models import DailyUpdate
from payroll.models import Payroll


@login_required
def dashboard(request):
    """
    Role-based dashboard routing.
    Redirects to appropriate dashboard based on user role.
    """
    user = request.user

    if user.is_ceo:
        return redirect("accounts:ceo")
    elif user.is_hr:
        return redirect("accounts:hr")
    elif user.is_pm:
        return redirect("accounts:pm")
    elif user.is_dev:
        return redirect("accounts:developer")
    elif user.is_uiux:
        return redirect("accounts:uiux")
    elif user.is_bde:
        return redirect("accounts:bde")
    else:
        # Default dashboard for users without role
        return render(request, "dashboards/default_dashboard.html", {"user": user})


@login_required
def ceo_dashboard(request):
    """CEO Dashboard with company overview"""
    if not request.user.is_ceo:
        return redirect("accounts:dashboard")

    today = timezone.now().date()
    organization = request.user.organization

    # Projects
    total_projects = Project.objects.filter(organization=organization).count()
    active_projects = Project.objects.filter(
        organization=organization, status__in=["IN_PROGRESS", "NOT_STARTED"]
    ).count()
    recent_projects_list = (
        Project.objects.filter(organization=organization)
        .select_related("project_manager")
        .order_by("-created_at")[:5]
    )

    # Calculate days remaining for each project
    recent_projects = []
    today = timezone.now().date()
    for project in recent_projects_list:
        days_remaining = None
        is_overdue = False
        if project.deadline:
            delta = project.deadline - today
            days_remaining = delta.days
            if days_remaining < 0:
                is_overdue = True
                days_remaining = abs(days_remaining)
        project.days_remaining = days_remaining
        project.is_overdue = is_overdue
        recent_projects.append(project)

    # Project status chart data
    project_status = (
        Project.objects.filter(organization=organization)
        .values("status")
        .annotate(count=Count("id"))
    )
    project_status_labels = [p["status"] for p in project_status]
    project_status_data = [p["count"] for p in project_status]

    # Employees
    total_employees = User.objects.filter(
        organization=organization, is_active=True
    ).count()
    active_employees = (
        User.objects.filter(organization=organization, is_active=True)
        .exclude(role__name="CEO")
        .count()
    )

    # Attendance
    today_attendance = Attendance.objects.filter(organization=organization, date=today)
    today_attendance_present = today_attendance.filter(status="PRESENT").count()
    today_attendance_absent = today_attendance.filter(status="ABSENT").count()

    # Tasks
    overdue_tasks = Task.objects.filter(
        project__organization=organization,
        deadline__lt=timezone.now(),
        status__in=["TO_DO", "IN_PROGRESS"],
    ).order_by("-deadline")[:5]

    # Leads
    total_leads = Lead.objects.filter(organization=organization).count()
    won_leads = Lead.objects.filter(
        organization=organization, stage="CLOSED_WON"
    ).count()

    # Leads summary
    leads_summary = {}
    for stage in [
        "NEW",
        "CONTACTED",
        "PROPOSAL_SENT",
        "NEGOTIATION",
        "CLOSED_WON",
        "CLOSED_LOST",
    ]:
        leads = Lead.objects.filter(organization=organization, stage=stage)
        leads_summary[stage] = {
            "count": leads.count(),
            "revenue": leads.aggregate(Sum("expected_revenue"))["expected_revenue__sum"]
            or 0,
        }

    # Today's leaves
    today_leaves = Leave.objects.filter(
        organization=organization,
        date_from__lte=today,
        date_to__gte=today,
        status="APPROVED",
    )[:5]

    # Revenue data (mock data - replace with actual revenue calculation)
    revenue_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    revenue_data = [10000, 15000, 12000, 18000, 20000, 25000]

    context = {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "recent_projects": recent_projects,
        "project_status_labels": project_status_labels,
        "project_status_data": project_status_data,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "today_attendance": {
            "present": today_attendance_present,
            "absent": today_attendance_absent,
        },
        "overdue_tasks": overdue_tasks,
        "total_leads": total_leads,
        "won_leads": won_leads,
        "leads_summary": leads_summary,
        "today_leaves": today_leaves,
        "revenue_labels": revenue_labels,
        "revenue_data": revenue_data,
    }

    return render(request, "dashboards/ceo_dashboard.html", context)


@login_required
def hr_dashboard(request):
    """HR Dashboard"""
    if not request.user.is_hr:
        return redirect("dashboard")

    today = timezone.now().date()
    organization = request.user.organization

    # Employees
    total_employees = (
        User.objects.filter(organization=organization, is_active=True)
        .exclude(role__name="CEO")
        .count()
    )

    # Attendance
    today_attendance = Attendance.objects.filter(organization=organization, date=today)
    today_attendance_present = today_attendance.filter(status="PRESENT").count()
    today_attendance_absent = today_attendance.filter(status="ABSENT").count()

    # Leaves
    pending_leaves = Leave.objects.filter(
        organization=organization, status="PENDING"
    ).count()
    pending_leave_requests = Leave.objects.filter(
        organization=organization, status="PENDING"
    ).order_by("-applied_at")[:5]

    # Payroll alerts (mock - implement actual logic)
    payroll_alerts = 0

    # Recent attendance
    recent_attendance = Attendance.objects.filter(organization=organization).order_by(
        "-date"
    )[:10]

    # Employee stats by role
    employees_by_role = (
        User.objects.filter(organization=organization, is_active=True)
        .exclude(role__isnull=True)
        .values("role__name")
        .annotate(count=Count("id"))
    )
    employees_by_role_dict = {
        item["role__name"]: item["count"] for item in employees_by_role
    }

    # Attendance chart data (last 7 days)
    attendance_labels = []
    attendance_present_data = []
    attendance_absent_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        attendance_labels.append(date.strftime("%b %d"))
        day_attendance = Attendance.objects.filter(organization=organization, date=date)
        attendance_present_data.append(day_attendance.filter(status="PRESENT").count())
        attendance_absent_data.append(day_attendance.filter(status="ABSENT").count())

    # Leave types chart
    leave_types = (
        Leave.objects.filter(organization=organization)
        .values("leave_type")
        .annotate(count=Count("id"))
    )
    leave_types_labels = [lt["leave_type"] for lt in leave_types]
    leave_types_data = [lt["count"] for lt in leave_types]

    context = {
        "total_employees": total_employees,
        "today_attendance": {
            "present": today_attendance_present,
            "absent": today_attendance_absent,
        },
        "pending_leaves": pending_leaves,
        "pending_leave_requests": pending_leave_requests,
        "payroll_alerts": payroll_alerts,
        "recent_attendance": recent_attendance,
        "employees_by_role": employees_by_role_dict,
        "attendance_labels": attendance_labels,
        "attendance_present_data": attendance_present_data,
        "attendance_absent_data": attendance_absent_data,
        "leave_types_labels": leave_types_labels,
        "leave_types_data": leave_types_data,
    }

    return render(request, "dashboards/hr_dashboard.html", context)


@login_required
def pm_dashboard(request):
    """Project Manager Dashboard"""
    if not request.user.is_pm:
        return redirect("dashboard")

    organization = request.user.organization

    # My projects
    my_projects = Project.objects.filter(
        organization=organization, project_manager=request.user
    )
    my_projects_count = my_projects.count()
    active_projects_count = my_projects.filter(status="IN_PROGRESS").count()

    # Tasks
    my_projects_ids = my_projects.values_list("id", flat=True)
    total_tasks = Task.objects.filter(project_id__in=my_projects_ids).count()
    completed_tasks = Task.objects.filter(
        project_id__in=my_projects_ids, status="COMPLETED"
    ).count()
    overdue_tasks_count = Task.objects.filter(
        project_id__in=my_projects_ids,
        deadline__lt=timezone.now(),
        status__in=["TO_DO", "IN_PROGRESS"],
    ).count()

    # Team members
    team_members = User.objects.filter(
        project_assignments__project_id__in=my_projects_ids
    ).distinct()
    team_members_count = team_members.count()

    # Tasks by status
    tasks_by_status = (
        Task.objects.filter(project_id__in=my_projects_ids)
        .values("status")
        .annotate(count=Count("id"))
    )
    tasks_by_status_dict = {item["status"]: item["count"] for item in tasks_by_status}

    # Recent tasks
    recent_tasks = Task.objects.filter(project_id__in=my_projects_ids).order_by(
        "-created_at"
    )[:5]

    # Team activity (daily updates)
    team_activity = DailyUpdate.objects.filter(project_id__in=my_projects_ids).order_by(
        "-created_at"
    )[:5]

    context = {
        "my_projects": my_projects[:6],
        "my_projects_count": my_projects_count,
        "active_projects_count": active_projects_count,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks_count": overdue_tasks_count,
        "team_members_count": team_members_count,
        "tasks_by_status": tasks_by_status_dict,
        "recent_tasks": recent_tasks,
        "team_activity": team_activity,
    }

    return render(request, "dashboards/pm_dashboard.html", context)


@login_required
def developer_dashboard(request):
    """Developer Dashboard"""
    if not request.user.is_dev:
        return redirect("dashboard")

    organization = request.user.organization

    # My tasks
    my_tasks = Task.objects.filter(assigned_to=request.user)
    my_tasks_count = my_tasks.count()
    completed_tasks_count = my_tasks.filter(status="COMPLETED").count()
    overdue_tasks_count = my_tasks.filter(
        deadline__lt=timezone.now(), status__in=["TO_DO", "IN_PROGRESS"]
    ).count()

    # Tasks by status
    tasks_by_status = my_tasks.values("status").annotate(count=Count("id"))
    tasks_by_status_dict = {item["status"]: item["count"] for item in tasks_by_status}

    # Assigned projects
    assigned_projects = Project.objects.filter(
        organization=organization, assignments__user=request.user
    ).distinct()
    assigned_projects_count = assigned_projects.count()

    # Monthly attendance
    today = timezone.now().date()
    month_start = today.replace(day=1)
    monthly_attendance = Attendance.objects.filter(
        organization=organization,
        user=request.user,
        date__gte=month_start,
        date__lte=today,
    )
    monthly_present = monthly_attendance.filter(status="PRESENT").count()
    monthly_total = (today - month_start).days + 1

    # Monthly leaves
    monthly_leaves = Leave.objects.filter(
        organization=organization,
        user=request.user,
        date_from__gte=month_start,
        date_from__lte=today,
        status="APPROVED",
    ).count()

    context = {
        "my_tasks": my_tasks,
        "my_tasks_count": my_tasks_count,
        "completed_tasks_count": completed_tasks_count,
        "overdue_tasks_count": overdue_tasks_count,
        "tasks_by_status": tasks_by_status_dict,
        "assigned_projects": assigned_projects[:5],
        "assigned_projects_count": assigned_projects_count,
        "monthly_attendance": {"present": monthly_present, "total": monthly_total},
        "monthly_leaves": monthly_leaves,
    }

    return render(request, "dashboards/developer_dashboard.html", context)


@login_required
def uiux_dashboard(request):
    """UI/UX Designer Dashboard"""
    if not request.user.is_uiux:
        return redirect("dashboard")

    organization = request.user.organization

    # Design tasks (tasks assigned to UI/UX)
    design_tasks = Task.objects.filter(assigned_to=request.user)
    design_tasks_count = design_tasks.count()
    completed_design_tasks = design_tasks.filter(status="COMPLETED").count()

    # Tasks by status
    tasks_by_status = design_tasks.values("status").annotate(count=Count("id"))
    tasks_by_status_dict = {item["status"]: item["count"] for item in tasks_by_status}

    # Assigned projects
    assigned_projects = Project.objects.filter(
        organization=organization, assignments__user=request.user
    ).distinct()
    assigned_projects_count = assigned_projects.count()

    # Pending reviews (mock)
    pending_reviews_count = 0

    # Assets count (from daily updates)
    assets_count = 0  # Implement actual count from attachments

    # Recent updates
    recent_updates = DailyUpdate.objects.filter(user=request.user).order_by("-date")[:5]

    # Recent assets (mock)
    recent_assets = []

    context = {
        "design_tasks": design_tasks,
        "design_tasks_count": design_tasks_count,
        "completed_design_tasks": completed_design_tasks,
        "tasks_by_status": tasks_by_status_dict,
        "assigned_projects": assigned_projects[:5],
        "assigned_projects_count": assigned_projects_count,
        "pending_reviews_count": pending_reviews_count,
        "assets_count": assets_count,
        "recent_updates": recent_updates,
        "recent_assets": recent_assets,
    }

    return render(request, "dashboards/uiux_dashboard.html", context)


@login_required
def bde_dashboard(request):
    """Business Development Executive Dashboard"""
    if not request.user.is_bde:
        return redirect("dashboard")

    organization = request.user.organization

    # Leads
    leads = Lead.objects.filter(organization=organization)
    total_leads = leads.count()
    active_leads = leads.exclude(stage__in=["CLOSED_WON", "CLOSED_LOST"]).count()
    won_leads = leads.filter(stage="CLOSED_WON").count()
    conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0

    # Expected revenue
    expected_revenue = (
        leads.aggregate(Sum("expected_revenue"))["expected_revenue__sum"] or 0
    )

    # Follow-ups today
    today = timezone.now().date()
    followups_today = 0  # Implement from MeetingLog

    # Leads by stage
    leads_by_stage = leads.values("stage").annotate(count=Count("id"))
    leads_by_stage_dict = {item["stage"]: item["count"] for item in leads_by_stage}

    # Recent follow-ups (mock)
    recent_followups = []

    # Conversion chart data
    conversion_labels = ["New", "Contacted", "Proposal", "Negotiation", "Won", "Lost"]
    conversion_data = [
        leads_by_stage_dict.get("NEW", 0),
        leads_by_stage_dict.get("CONTACTED", 0),
        leads_by_stage_dict.get("PROPOSAL_SENT", 0),
        leads_by_stage_dict.get("NEGOTIATION", 0),
        leads_by_stage_dict.get("CLOSED_WON", 0),
        leads_by_stage_dict.get("CLOSED_LOST", 0),
    ]

    # Revenue projection (mock)
    revenue_projection_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    revenue_projection_data = [5000, 8000, 12000, 15000, 18000, 20000]

    context = {
        "leads": leads[:20],
        "total_leads": total_leads,
        "active_leads": active_leads,
        "won_leads": won_leads,
        "conversion_rate": round(conversion_rate, 1),
        "expected_revenue": expected_revenue,
        "followups_today": followups_today,
        "leads_by_stage": leads_by_stage_dict,
        "recent_followups": recent_followups,
        "conversion_labels": conversion_labels,
        "conversion_data": conversion_data,
        "revenue_projection_labels": revenue_projection_labels,
        "revenue_projection_data": revenue_projection_data,
    }

    return render(request, "dashboards/bde_dashboard.html", context)
