from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from leaves.models import Leave, LeaveBalance
from accounts.models import User


@login_required
def list_leaves(request):
    """List all leave requests with filtering"""
    user = request.user
    
    # Get user's organization
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Base queryset
    if user.is_ceo or user.is_hr:
        # CEO/HR can see all leaves in organization
        leaves = Leave.objects.filter(
            organization=organization
        ).select_related('user', 'approved_by').order_by('-applied_at')
    else:
        # Others see only their own leaves
        leaves = Leave.objects.filter(
            user=user,
            organization=organization
        ).select_related('user', 'approved_by').order_by('-applied_at')
    
    # Filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    leave_type_filter = request.GET.get('leave_type', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search_query:
        leaves = leaves.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(reason__icontains=search_query)
        )
    
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    
    if leave_type_filter:
        leaves = leaves.filter(leave_type=leave_type_filter)
    
    if user_filter and (user.is_ceo or user.is_hr):
        leaves = leaves.filter(user_id=user_filter)
    
    if date_from:
        leaves = leaves.filter(date_from__gte=date_from)
    
    if date_to:
        leaves = leaves.filter(date_to__lte=date_to)
    
    # Pagination
    paginator = Paginator(leaves, 50)
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
    total_leaves = leaves.count()
    pending_count = leaves.filter(status='PENDING').count()
    approved_count = leaves.filter(status='APPROVED').count()
    rejected_count = leaves.filter(status='REJECTED').count()
    cancelled_count = leaves.filter(status='CANCELLED').count()
    
    context = {
        'page_obj': page_obj,
        'leaves': page_obj,
        'users': users,
        'total_leaves': total_leaves,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'cancelled_count': cancelled_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'leave_type_filter': leave_type_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'can_approve': user.is_ceo or user.is_hr,
    }
    
    return render(request, 'leaves/list.html', context)


@login_required
def my_leaves(request):
    """View own leave requests"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Get user's leaves
    leaves = Leave.objects.filter(
        user=user,
        organization=organization
    ).select_related('approved_by').order_by('-applied_at')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    leave_type_filter = request.GET.get('leave_type', '')
    
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    
    if leave_type_filter:
        leaves = leaves.filter(leave_type=leave_type_filter)
    
    # Get leave balances for current year
    current_year = timezone.now().year
    leave_balances = LeaveBalance.objects.filter(
        user=user,
        organization=organization,
        year=current_year
    )
    
    # Statistics
    total_leaves = leaves.count()
    pending_count = leaves.filter(status='PENDING').count()
    approved_count = leaves.filter(status='APPROVED').count()
    rejected_count = leaves.filter(status='REJECTED').count()
    
    context = {
        'leaves': leaves,
        'leave_balances': leave_balances,
        'current_year': current_year,
        'total_leaves': total_leaves,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'status_filter': status_filter,
        'leave_type_filter': leave_type_filter,
    }
    
    return render(request, 'leaves/my_leaves.html', context)


@login_required
def create_leave(request):
    """Create a new leave request"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from leaves.forms import LeaveForm
        form = LeaveForm(request.POST, request.FILES, user=user, organization=user.organization)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.organization = user.organization
            leave.user = user
            leave.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('leaves:my-leaves')
    else:
        from leaves.forms import LeaveForm
        form = LeaveForm(user=user, organization=user.organization)
    
    return render(request, 'leaves/form.html', {
        'form': form,
        'title': 'Apply for Leave'
    })


@login_required
def approve_leave(request, id):
    """Approve a leave request"""
    user = request.user
    
    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to approve leaves.')
        return redirect('leaves:list')
    
    leave = get_object_or_404(Leave, id=id)
    
    if leave.status != 'PENDING':
        messages.warning(request, f'This leave request is already {leave.get_status_display().lower()}.')
        return redirect('leaves:list')
    
    if request.method == 'POST':
        leave.status = 'APPROVED'
        leave.approved_by = user
        leave.approved_at = timezone.now()
        leave.save()
        
        # Update leave balance
        current_year = leave.date_from.year
        try:
            leave_balance = LeaveBalance.objects.get(
                user=leave.user,
                organization=leave.organization,
                leave_type=leave.leave_type,
                year=current_year
            )
        except LeaveBalance.DoesNotExist:
            leave_balance = LeaveBalance.objects.create(
                user=leave.user,
                organization=leave.organization,
                leave_type=leave.leave_type,
                year=current_year,
                total_days=0,
                used_days=0
            )
        
        # Update used days
        leave_balance.used_days += leave.days
        leave_balance.save()
        
        messages.success(request, f'Leave request for {leave.user.get_full_name()} has been approved.')
        return redirect('leaves:list')
    
    return render(request, 'leaves/approve_confirm.html', {
        'leave': leave
    })


@login_required
def reject_leave(request, id):
    """Reject a leave request"""
    user = request.user
    
    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(request, 'You do not have permission to reject leaves.')
        return redirect('leaves:list')
    
    leave = get_object_or_404(Leave, id=id)
    
    if leave.status != 'PENDING':
        messages.warning(request, f'This leave request is already {leave.get_status_display().lower()}.')
        return redirect('leaves:list')
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        leave.status = 'REJECTED'
        leave.approved_by = user
        leave.approved_at = timezone.now()
        leave.rejection_reason = rejection_reason
        leave.save()
        
        messages.success(request, f'Leave request for {leave.user.get_full_name()} has been rejected.')
        return redirect('leaves:list')
    
    return render(request, 'leaves/reject_confirm.html', {
        'leave': leave
    })
