from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime
import calendar

from decimal import Decimal, ROUND_HALF_UP
from payroll.models import Payroll, SalaryStructure
from accounts.models import User
from attendance.models import Attendance
from company.models import Holiday


def get_payroll_attendance_breakdown(payroll):
    """
    Compute attendance breakdown for a payroll month: working days, present, absent, etc.
    Non-working days = Sundays + company holidays (national, Saturday off, etc.) — no salary cut.
    Returns a dict suitable for JSON (Decimals as strings where needed).
    """
    month, year = payroll.month, payroll.year
    total_days = calendar.monthrange(year, month)[1]
    non_working = Holiday.get_non_working_dates_for_month(payroll.organization, year, month)
    working_days_in_month = total_days - len(non_working)
    total_sundays = sum(
        1 for day in range(1, total_days + 1)
        if datetime(year, month, day).date().weekday() == 6
    )

    attendances = list(
        Attendance.objects.filter(
            user=payroll.user,
            organization=payroll.organization,
            date__year=year,
            date__month=month,
        ).values_list('date', 'status')
    )

    # Count by status (only on working days; Sunday + holidays not counted as present/absent)
    present_count = 0
    late_count = 0
    wfh_count = 0
    half_day_count = 0
    absent_status_count = 0
    leave_count = 0
    effective_days = Decimal('0')
    working_day_records = 0

    for dat, status in attendances:
        if dat in non_working:
            continue
        working_day_records += 1
        if status in ('PRESENT',):
            present_count += 1
            effective_days += 1
        elif status == 'LATE':
            late_count += 1
            effective_days += 1
        elif status == 'WORK_FROM_HOME':
            wfh_count += 1
            effective_days += 1
        elif status == 'HALF_DAY':
            half_day_count += 1
            effective_days += Decimal('0.5')
        elif status == 'ABSENT':
            absent_status_count += 1
        elif status == 'LEAVE':
            leave_count += 1

    # No record = absent (working days with no attendance record)
    no_record_absent = working_days_in_month - working_day_records
    total_absent = no_record_absent + absent_status_count

    # Effective days = Present + Late + WFH + 0.5×Half day + Sundays + Holidays (all non-working days are paid)
    effective_days += Decimal(len(non_working))

    # Per day salary = Base / number of days in month (total calendar days)
    if total_days:
        per_day_salary = (payroll.base_salary / total_days).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    else:
        per_day_salary = Decimal('0')
    calculated_salary = (per_day_salary * effective_days).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    attendance_deduction_calc = (payroll.base_salary - calculated_salary).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    if attendance_deduction_calc < 0:
        attendance_deduction_calc = Decimal('0')

    company_holidays_count = len(non_working) - total_sundays  # Saturday off, national, etc.
    return {
        'period': {
            'month': month,
            'year': year,
            'month_name': calendar.month_name[month],
        },
        'days': {
            'total_days_in_month': total_days,
            'working_days_in_month': working_days_in_month,
            'sundays_holiday': total_sundays,
            'company_holidays': company_holidays_count,
        },
        'attendance_breakdown': {
            'present': present_count,
            'late': late_count,
            'work_from_home': wfh_count,
            'half_day': half_day_count,
            'absent': total_absent,
            'absent_no_record': no_record_absent,
            'absent_marked': absent_status_count,
            'leave': leave_count,
        },
        'effective_days': str(effective_days),
        'per_day_salary': str(per_day_salary),
        'calculated_salary_from_attendance': str(calculated_salary),
        'attendance_deduction': str(attendance_deduction_calc),
    }


@login_required
def list_payroll(request):
    """List all payroll records with filtering. Only CEO and HR can view and update.
    GET with Accept: application/json or ?format=json returns JSON list (own payrolls for non-CEO/HR)."""
    user = request.user

    wants_json = (
        'application/json' in request.META.get('HTTP_ACCEPT', '')
        or request.GET.get('format') == 'json'
    )

    if not user.organization:
        if wants_json:
            return JsonResponse({'error': 'You are not associated with an organization.'}, status=400)
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')

    organization = user.organization

    if wants_json:
        # API list: CEO/HR see all (with optional filters), others see only own
        if user.is_ceo or user.is_hr:
            payrolls = Payroll.objects.filter(
                organization=organization
            ).select_related('user', 'processed_by').order_by('-year', '-month', 'user__first_name')
            if request.GET.get('status'):
                payrolls = payrolls.filter(status=request.GET.get('status'))
            if request.GET.get('user_id'):
                payrolls = payrolls.filter(user_id=request.GET.get('user_id'))
            try:
                if request.GET.get('month'):
                    payrolls = payrolls.filter(month=int(request.GET.get('month')))
                if request.GET.get('year'):
                    payrolls = payrolls.filter(year=int(request.GET.get('year')))
            except (TypeError, ValueError):
                pass
        else:
            payrolls = Payroll.objects.filter(
                organization=organization, user=user
            ).select_related('user', 'processed_by').order_by('-year', '-month')
        page = request.GET.get('page', 1)
        paginator = Paginator(payrolls, 50)
        page_obj = paginator.get_page(page)
        results = [
            {
                'id': p.id,
                'user': {'id': p.user_id, 'name': p.user.get_full_name() or p.user.email},
                'period': {'month': p.month, 'year': p.year, 'month_name': p.get_month_display()},
                'base_salary': str(p.base_salary),
                'bonuses': str(p.bonuses),
                'deductions': str(p.deductions),
                'attendance_deduction': str(p.attendance_deduction),
                'net_salary': str(p.net_salary),
                'status': p.status,
                'status_display': p.get_status_display(),
            }
            for p in page_obj
        ]
        return JsonResponse({
            'count': paginator.count,
            'results': results,
            'page': page_obj.number,
            'num_pages': paginator.num_pages,
        })

    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to view payroll.')
        return redirect('accounts:dashboard')

    payrolls = Payroll.objects.filter(
        organization=organization
    ).select_related('user', 'processed_by').order_by('-year', '-month', 'user__first_name')
    
    # Filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    user_filter = request.GET.get('user', '')
    month_filter = request.GET.get('month', '')
    year_filter = request.GET.get('year', '')
    
    if search_query:
        payrolls = payrolls.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    if status_filter:
        payrolls = payrolls.filter(status=status_filter)
    
    if user_filter:
        payrolls = payrolls.filter(user_id=user_filter)
    
    if month_filter:
        payrolls = payrolls.filter(month=month_filter)
    
    if year_filter:
        payrolls = payrolls.filter(year=year_filter)
    
    # Pagination
    paginator = Paginator(payrolls, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get users for filter dropdown (only for CEO/HR)
    users = None
    if user.is_ceo or user.is_hr:
        users = User.objects.filter(
            organization=organization,
            is_active=True
        ).order_by('first_name', 'last_name')
    
    # Statistics
    total_payrolls = payrolls.count()
    draft_count = payrolls.filter(status='DRAFT').count()
    processed_count = payrolls.filter(status='PROCESSED').count()
    paid_count = payrolls.filter(status='PAID').count()
    total_net_salary = payrolls.filter(status__in=['PROCESSED', 'PAID']).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
    
    context = {
        'page_obj': page_obj,
        'payrolls': page_obj,
        'users': users,
        'total_payrolls': total_payrolls,
        'draft_count': draft_count,
        'processed_count': processed_count,
        'paid_count': paid_count,
        'total_net_salary': total_net_salary,
        'search_query': search_query,
        'status_filter': status_filter,
        'user_filter': user_filter,
        'month_filter': month_filter,
        'year_filter': year_filter,
        'can_edit': user.is_ceo or user.is_hr,
    }
    
    return render(request, 'payroll/list.html', context)


@login_required
def create_payroll(request):
    """Create a new payroll record"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to create payroll records.')
        return redirect('payroll:list')
    
    if request.method == 'POST':
        from payroll.forms import PayrollForm
        form = PayrollForm(request.POST, user=user, organization=user.organization)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.organization = user.organization
            payroll.save()
            messages.success(request, f'Payroll record created successfully for {payroll.user.get_full_name()}!')
            return redirect('payroll:list')
    else:
        from payroll.forms import PayrollForm
        form = PayrollForm(user=user, organization=user.organization)
    
    return render(request, 'payroll/form.html', {
        'form': form,
        'title': 'Create Payroll Record'
    })


@login_required
def update_payroll(request, id):
    """Update an existing payroll record"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to edit payroll records.')
        return redirect('payroll:list')
    
    payroll = get_object_or_404(Payroll, id=id)
    
    # Only allow editing DRAFT payrolls
    if payroll.status != 'DRAFT':
        messages.warning(request, 'Only draft payroll records can be edited.')
        return redirect('payroll:list')
    
    if request.method == 'POST':
        from payroll.forms import PayrollForm
        form = PayrollForm(request.POST, instance=payroll, user=user, organization=user.organization)
        if form.is_valid():
            updated_payroll = form.save(commit=False)
            updated_payroll.organization = user.organization
            updated_payroll.save()
            messages.success(request, f'Payroll record updated successfully for {updated_payroll.user.get_full_name()}!')
            return redirect('payroll:list')
    else:
        from payroll.forms import PayrollForm
        form = PayrollForm(instance=payroll, user=user, organization=user.organization)
    
    return render(request, 'payroll/form.html', {
        'form': form,
        'payroll': payroll,
        'title': 'Update Payroll Record'
    })


@login_required
def process_payroll(request, id):
    """Process a payroll record"""
    user = request.user
    
    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to process payroll.')
        return redirect('payroll:list')
    
    payroll = get_object_or_404(Payroll, id=id)
    
    if payroll.status != 'DRAFT':
        messages.warning(request, f'This payroll is already {payroll.get_status_display().lower()}.')
        return redirect('payroll:list')
    
    if request.method == 'POST':
        payroll.status = 'PROCESSED'
        payroll.processed_by = user
        payroll.processed_at = timezone.now()
        payroll.save()
        
        messages.success(request, f'Payroll for {payroll.user.get_full_name()} has been processed.')
        return redirect('payroll:list')
    
    return render(request, 'payroll/process_confirm.html', {
        'payroll': payroll
    })


@login_required
def change_status(request, id):
    """Change payroll status"""
    user = request.user
    
    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to change payroll status.')
        return redirect('payroll:list')
    
    payroll = get_object_or_404(Payroll, id=id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if not new_status:
            messages.error(request, 'Status is required.')
            return redirect('payroll:list')
        
        # Validate status
        valid_statuses = [choice[0] for choice in Payroll.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Invalid status.')
            return redirect('payroll:list')
        
        old_status = payroll.status
        payroll.status = new_status
        
        # Set processed_by and processed_at if changing to PROCESSED
        if new_status == 'PROCESSED' and old_status != 'PROCESSED':
            payroll.processed_by = user
            payroll.processed_at = timezone.now()
        elif new_status != 'PROCESSED':
            # Clear processed_by if changing away from PROCESSED
            if old_status == 'PROCESSED':
                payroll.processed_by = None
                payroll.processed_at = None
        
        payroll.save()
        
        # Get status display names
        status_dict = dict(Payroll.STATUS_CHOICES)
        old_status_display = status_dict.get(old_status, old_status)
        new_status_display = status_dict.get(new_status, new_status)
        
        messages.success(request, f'Payroll status changed from {old_status_display} to {new_status_display} for {payroll.user.get_full_name()}.')
        return redirect('payroll:list')
    
    return redirect('payroll:list')


@login_required
def mark_paid(request, id):
    """Mark payroll as paid"""
    user = request.user
    
    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to mark payroll as paid.')
        return redirect('payroll:list')
    
    payroll = get_object_or_404(Payroll, id=id)
    
    if payroll.status != 'PROCESSED':
        messages.warning(request, f'Payroll must be processed before marking as paid.')
        return redirect('payroll:list')
    
    if request.method == 'POST':
        payroll.status = 'PAID'
        payroll.save()
        
        messages.success(request, f'Payroll for {payroll.user.get_full_name()} has been marked as paid.')
        return redirect('payroll:list')
    
    return render(request, 'payroll/mark_paid_confirm.html', {
        'payroll': payroll
    })


@login_required
def generate_payroll(request):
    """Generate payroll records automatically from user salaries for a given month/year. CEO/HR only."""
    user = request.user

    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to generate payroll.')
        return redirect('accounts:dashboard')

    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')

    organization = user.organization

    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12 or year < 2020 or year > 2030:
                raise ValueError('Invalid month or year')
        except (TypeError, ValueError):
            messages.error(request, 'Please select a valid month and year.')
            return redirect('payroll:generate')

        # Users with salary set (exclude CEO role for payroll if desired; here we include all with salary)
        users_with_salary = User.objects.filter(
            organization=organization,
            is_active=True,
            salary__isnull=False
        ).exclude(salary=Decimal('0'))

        # Per-day salary = Base / number of days in month (total calendar days)
        total_days_in_month = calendar.monthrange(year, month)[1]
        if total_days_in_month == 0:
            total_days_in_month = 1

        non_working = Holiday.get_non_working_dates_for_month(organization, year, month)

        existing_payrolls = {
            p.user_id: p
            for p in Payroll.objects.filter(
                organization=organization,
                month=month,
                year=year,
            ).select_related("user")
        }

        created_count = 0
        updated_count = 0

        for u in users_with_salary:
            monthly_salary = u.salary or Decimal('0')
            per_day_salary = (monthly_salary / total_days_in_month).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            # Effective days: only on working days (exclude Sunday + company holidays like Saturday off, national).
            attendances = Attendance.objects.filter(
                user=u,
                organization=organization,
                date__year=year,
                date__month=month,
            )
            effective_days = Decimal('0')
            for att in attendances:
                if att.date in non_working:
                    continue
                if att.status in ('PRESENT', 'LATE', 'WORK_FROM_HOME'):
                    effective_days += 1
                elif att.status == 'HALF_DAY':
                    effective_days += Decimal('0.5')
            # Effective days = attendance days + Sundays + Holidays (non-working days are paid)
            effective_days += Decimal(len(non_working))

            calculated_salary = (per_day_salary * effective_days).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            attendance_deduction = (monthly_salary - calculated_salary).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            if attendance_deduction < 0:
                attendance_deduction = Decimal('0')

            payroll = existing_payrolls.get(u.id)
            if payroll is None:
                payroll = Payroll(
                    organization=organization,
                    user=u,
                    month=month,
                    year=year,
                    base_salary=monthly_salary,
                    bonuses=Decimal('0'),
                    deductions=Decimal('0'),
                    attendance_deduction=attendance_deduction,
                    status='DRAFT',
                )
                payroll.save()
                created_count += 1
            elif payroll.status == 'DRAFT':
                payroll.base_salary = monthly_salary
                payroll.attendance_deduction = attendance_deduction
                payroll.deductions = payroll.deductions or Decimal('0')
                payroll.bonuses = payroll.bonuses or Decimal('0')
                payroll.save()
                updated_count += 1

        skipped = len([uid for uid in existing_payrolls if existing_payrolls[uid].status != 'DRAFT'])
        if created_count or updated_count:
            parts = []
            if created_count:
                parts.append(f'{created_count} created')
            if updated_count:
                parts.append(f'{updated_count} updated (attendance-based pay)')
            messages.success(
                request,
                f"{calendar.month_name[month]} {year}: {', '.join(parts)}."
                + (f' {skipped} non-draft payroll(s) left unchanged.' if skipped else '')
            )
        else:
            if users_with_salary.exists():
                messages.info(
                    request,
                    f'All {users_with_salary.count()} user(s) with salary already have payroll for {calendar.month_name[month]} {year}.'
                )
            else:
                messages.warning(
                    request,
                    'No users with salary found. Set salary on users (Users Management) first.'
                )
        return redirect('payroll:list')

    # GET: show form
    now = timezone.now()
    context = {
        'default_month': now.month,
        'default_year': now.year,
        'month_names': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'users_with_salary_count': User.objects.filter(
            organization=organization,
            is_active=True,
            salary__isnull=False
        ).exclude(salary=Decimal('0')).count(),
    }
    return render(request, 'payroll/generate.html', context)


@login_required
def my_payroll(request):
    """List current user's payroll records. Any logged-in user can view their own."""
    user = request.user
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')

    payrolls = Payroll.objects.filter(
        organization=user.organization,
        user=user,
    ).select_related('user', 'processed_by').order_by('-year', '-month')

    paginator = Paginator(payrolls, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'payrolls': page_obj,
    }
    return render(request, 'payroll/my_list.html', context)


def _payroll_to_json(payroll):
    """Build JSON-serializable dict for a payroll (for API)."""
    data = {
        'id': payroll.id,
        'user': {
            'id': payroll.user_id,
            'email': payroll.user.email,
            'first_name': payroll.user.first_name,
            'last_name': payroll.user.get_full_name() or payroll.user.email,
        },
        'period': {
            'month': payroll.month,
            'year': payroll.year,
            'month_name': payroll.get_month_display(),
        },
        'base_salary': str(payroll.base_salary),
        'bonuses': str(payroll.bonuses),
        'deductions': str(payroll.deductions),
        'attendance_deduction': str(payroll.attendance_deduction),
        'gross_salary': str(payroll.gross_salary),
        'net_salary': str(payroll.net_salary),
        'status': payroll.status,
        'status_display': payroll.get_status_display(),
        'notes': payroll.notes or '',
        'processed_by': None,
        'processed_at': None,
    }
    if payroll.processed_by_id:
        data['processed_by'] = {
            'id': payroll.processed_by_id,
            'name': payroll.processed_by.get_full_name() or payroll.processed_by.email,
        }
        data['processed_at'] = payroll.processed_at.isoformat() if payroll.processed_at else None
    data['calculation'] = get_payroll_attendance_breakdown(payroll)
    return data


@login_required
def payroll_detail(request, id):
    """View a single payroll (payslip). User can view own; CEO/HR can view any.
    Returns JSON with full calculation (days present, absent, etc.) when Accept: application/json."""
    user = request.user
    payroll = get_object_or_404(Payroll, id=id)

    if payroll.user_id != user.id and not (user.is_ceo or user.is_hr):
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return JsonResponse({'error': 'You do not have permission to view this payroll.'}, status=403)
        messages.error(request, 'You do not have permission to view this payroll.')
        return redirect('accounts:dashboard')

    if payroll.organization_id != user.organization_id:
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return JsonResponse({'error': 'You do not have permission to view this payroll.'}, status=403)
        messages.error(request, 'You do not have permission to view this payroll.')
        return redirect('accounts:dashboard')

    wants_json = (
        'application/json' in request.META.get('HTTP_ACCEPT', '')
        or request.GET.get('format') == 'json'
    )
    if wants_json:
        return JsonResponse(_payroll_to_json(payroll))

    calculation = get_payroll_attendance_breakdown(payroll)
    context = {'payroll': payroll, 'calculation': calculation}
    return render(request, 'payroll/detail.html', context)
