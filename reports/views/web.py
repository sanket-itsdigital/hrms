from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
import csv

from accounts.models import User
from projects.models import Project
from tasks.models import Task
from attendance.models import Attendance
from leaves.models import Leave
from payroll.models import Payroll
from leads_crm.models import Lead
from daily_updates.models import DailyUpdate


@login_required
def reports_index(request):
    """Reports index page"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    context = {
        'can_generate_reports': user.is_ceo or user.is_hr,
    }
    
    return render(request, 'reports/index.html', context)


@login_required
def attendance_report(request):
    """Generate attendance report"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Get report parameters
    report_type = request.GET.get('type', 'monthly')
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    user_id = request.GET.get('user', '')
    
    try:
        year = int(year)
        month = int(month) if month else None
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month
    
    # Base queryset
    if user.is_ceo or user.is_hr:
        if user_id:
            attendances = Attendance.objects.filter(
                organization=organization,
                user_id=user_id
            )
        else:
            attendances = Attendance.objects.filter(organization=organization)
    else:
        attendances = Attendance.objects.filter(
            user=user,
            organization=organization
        )
    
    # Filter by date range
    if report_type == 'monthly' and month:
        attendances = attendances.filter(date__year=year, date__month=month)
        date_range = f"{calendar.month_name[month]} {year}"
    else:
        attendances = attendances.filter(date__year=year)
        date_range = f"{year}"
    
    # Calculate statistics
    total_days = attendances.count()
    present_days = attendances.filter(status='PRESENT').count()
    absent_days = attendances.filter(status='ABSENT').count()
    leave_days = attendances.filter(status='LEAVE').count()
    late_days = attendances.filter(status='LATE').count()
    half_days = attendances.filter(status='HALF_DAY').count()
    wfh_days = attendances.filter(status='WORK_FROM_HOME').count()
    
    # Group by user if viewing all
    user_stats = None
    if user.is_ceo or user.is_hr and not user_id:
        user_stats = attendances.values('user__id', 'user__first_name', 'user__last_name', 'user__email').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            leave=Count('id', filter=Q(status='LEAVE')),
            late=Count('id', filter=Q(status='LATE')),
            half_day=Count('id', filter=Q(status='HALF_DAY')),
            wfh=Count('id', filter=Q(status='WORK_FROM_HOME'))
        ).order_by('user__first_name', 'user__last_name')
    
    # Get users for filter
    users = None
    if user.is_ceo or user.is_hr:
        users = User.objects.filter(
            organization=organization,
            is_active=True
        ).order_by('first_name', 'last_name')
    
    context = {
        'report_type': report_type,
        'year': year,
        'month': month,
        'date_range': date_range,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'leave_days': leave_days,
        'late_days': late_days,
        'half_days': half_days,
        'wfh_days': wfh_days,
        'user_stats': user_stats,
        'users': users,
        'selected_user': user_id,
    }
    
    return render(request, 'reports/attendance.html', context)


@login_required
def payroll_report(request):
    """Generate payroll report"""
    user = request.user
    
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to view payroll reports.')
        return redirect('accounts:dashboard')
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Get report parameters
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', '')
    user_id = request.GET.get('user', '')
    
    try:
        year = int(year)
        month = int(month) if month else None
    except (ValueError, TypeError):
        year = timezone.now().year
        month = None
    
    # Base queryset
    payrolls = Payroll.objects.filter(organization=organization)
    
    if user_id:
        payrolls = payrolls.filter(user_id=user_id)
    
    if month:
        payrolls = payrolls.filter(year=year, month=month)
        date_range = f"{calendar.month_name[month]} {year}"
    else:
        payrolls = payrolls.filter(year=year)
        date_range = f"{year}"
    
    # Statistics
    total_payrolls = payrolls.count()
    total_net_salary = payrolls.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
    total_base_salary = payrolls.aggregate(Sum('base_salary'))['base_salary__sum'] or 0
    total_bonuses = payrolls.aggregate(Sum('bonuses'))['bonuses__sum'] or 0
    total_deductions = payrolls.aggregate(Sum('deductions'))['deductions__sum'] or 0
    
    # Group by user
    user_stats = payrolls.values('user__id', 'user__first_name', 'user__last_name', 'user__email').annotate(
        total_records=Count('id'),
        total_salary=Sum('net_salary'),
        avg_salary=Avg('net_salary')
    ).order_by('user__first_name', 'user__last_name')
    
    # Get users for filter
    users = User.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('first_name', 'last_name')
    
    context = {
        'year': year,
        'month': month,
        'date_range': date_range,
        'total_payrolls': total_payrolls,
        'total_net_salary': total_net_salary,
        'total_base_salary': total_base_salary,
        'total_bonuses': total_bonuses,
        'total_deductions': total_deductions,
        'user_stats': user_stats,
        'users': users,
        'selected_user': user_id,
    }
    
    return render(request, 'reports/payroll.html', context)


@login_required
def projects_report(request):
    """Generate projects report"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Base queryset
    if user.is_ceo:
        projects = Project.objects.filter(organization=organization)
    elif user.is_pm:
        projects = Project.objects.filter(
            organization=organization,
            project_manager=user
        )
    else:
        projects = Project.objects.filter(
            organization=organization,
            team_members=user
        ).distinct()
    
    # Statistics
    total_projects = projects.count()
    not_started = projects.filter(status='NOT_STARTED').count()
    in_progress = projects.filter(status='IN_PROGRESS').count()
    on_hold = projects.filter(status='ON_HOLD').count()
    completed = projects.filter(status='COMPLETED').count()
    cancelled = projects.filter(status='CANCELLED').count()
    
    # Budget statistics
    total_budget = projects.aggregate(Sum('budget'))['budget__sum'] or 0
    
    # Group by status
    status_stats = projects.values('status').annotate(count=Count('id'))
    
    # Group by project manager
    pm_stats = projects.values('project_manager__first_name', 'project_manager__last_name', 'project_manager__email').annotate(
        count=Count('id')
    ).order_by('project_manager__first_name')
    
    context = {
        'total_projects': total_projects,
        'not_started': not_started,
        'in_progress': in_progress,
        'on_hold': on_hold,
        'completed': completed,
        'cancelled': cancelled,
        'total_budget': total_budget,
        'status_stats': status_stats,
        'pm_stats': pm_stats,
        'projects': projects[:20],  # Recent projects
    }
    
    return render(request, 'reports/projects.html', context)


@login_required
def leads_report(request):
    """Generate leads report"""
    user = request.user
    
    if not (user.is_ceo or user.is_bde):
        messages.error(request, 'You do not have permission to view leads reports.')
        return redirect('accounts:dashboard')
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Get all leads
    leads = Lead.objects.filter(organization=organization)
    
    # Statistics
    total_leads = leads.count()
    new_count = leads.filter(stage='NEW').count()
    contacted_count = leads.filter(stage='CONTACTED').count()
    proposal_sent_count = leads.filter(stage='PROPOSAL_SENT').count()
    negotiation_count = leads.filter(stage='NEGOTIATION').count()
    won_count = leads.filter(stage='CLOSED_WON').count()
    lost_count = leads.filter(stage='CLOSED_LOST').count()
    
    # Revenue statistics
    total_revenue = leads.filter(stage='CLOSED_WON').aggregate(Sum('expected_revenue'))['expected_revenue__sum'] or 0
    pipeline_revenue = leads.filter(stage__in=['NEW', 'CONTACTED', 'PROPOSAL_SENT', 'NEGOTIATION']).aggregate(Sum('expected_revenue'))['expected_revenue__sum'] or 0
    
    # Conversion rate
    conversion_rate = (won_count / total_leads * 100) if total_leads > 0 else 0
    
    # Group by stage
    stage_stats = leads.values('stage').annotate(
        count=Count('id'),
        total_revenue=Sum('expected_revenue')
    ).order_by('stage')
    
    # Group by assigned user
    user_stats = leads.values('assigned_to__first_name', 'assigned_to__last_name', 'assigned_to__email').annotate(
        count=Count('id'),
        won=Count('id', filter=Q(stage='CLOSED_WON')),
        revenue=Sum('expected_revenue', filter=Q(stage='CLOSED_WON'))
    ).order_by('assigned_to__first_name')
    
    context = {
        'total_leads': total_leads,
        'new_count': new_count,
        'contacted_count': contacted_count,
        'proposal_sent_count': proposal_sent_count,
        'negotiation_count': negotiation_count,
        'won_count': won_count,
        'lost_count': lost_count,
        'total_revenue': total_revenue,
        'pipeline_revenue': pipeline_revenue,
        'conversion_rate': conversion_rate,
        'stage_stats': stage_stats,
        'user_stats': user_stats,
    }
    
    return render(request, 'reports/leads.html', context)
