from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime
import calendar

from payroll.models import Payroll, SalaryStructure
from accounts.models import User
from attendance.models import Attendance


@login_required
def list_payroll(request):
    """List all payroll records with filtering"""
    user = request.user
    
    # Get user's organization
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Base queryset
    if user.is_ceo or user.is_hr:
        # CEO/HR can see all payroll in organization
        payrolls = Payroll.objects.filter(
            organization=organization
        ).select_related('user', 'processed_by').order_by('-year', '-month', 'user__first_name')
    else:
        # Others see only their own payroll
        payrolls = Payroll.objects.filter(
            user=user,
            organization=organization
        ).select_related('user', 'processed_by').order_by('-year', '-month')
    
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
    
    if user_filter and (user.is_ceo or user.is_hr):
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
