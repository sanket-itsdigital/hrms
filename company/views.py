from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from company.models import Announcement, Policy, Holiday, Event, BirthdayAnniversary
from company.forms import (
    AnnouncementForm, PolicyForm, HolidayForm,
    EventForm, BirthdayAnniversaryForm
)
from accounts.models import User


# ==================== ANNOUNCEMENTS ====================

@login_required
def announcements_list(request):
    """List all announcements for the user's organization"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    # Get announcements for user's organization
    announcements = Announcement.objects.filter(
        organization=user.organization
    ).select_related('created_by').order_by('-is_pinned', '-created_at')
    
    # Check if user can manage (CEO or HR) - they see all announcements
    can_manage = user.is_ceo or user.is_hr
    
    # Filter by active announcements (not expired)
    today = timezone.now()
    active_announcements = [a for a in announcements if a.is_active()]
    
    # Filter by target roles if specified (but CEO/HR see all)
    if can_manage:
        # CEO/HR can see all announcements for management
        filtered_announcements = active_announcements
    else:
        # Regular users see announcements based on target roles
        filtered_announcements = []
        user_role_name = user.role.name if user.role else None
        
        for announcement in active_announcements:
            target_roles = announcement.target_roles or []
            # If no target roles specified, show to all
            # If target roles specified, check if user's role is included
            if not target_roles or (user_role_name and user_role_name in target_roles):
                filtered_announcements.append(announcement)
    
    # Pagination
    paginator = Paginator(filtered_announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'announcements': page_obj,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/announcements/list.html', context)


@login_required
def announcement_detail(request, id):
    """View announcement details"""
    user = request.user
    announcement = get_object_or_404(Announcement, id=id)
    
    # Check if user has access
    if announcement.organization != user.organization:
        messages.error(request, 'You do not have access to this announcement.')
        return redirect('company:announcements_list')
    
    # Check target roles
    if announcement.target_roles:
        if not user.role or user.role.name not in announcement.target_roles:
            messages.error(request, 'You do not have access to this announcement.')
            return redirect('company:announcements_list')
    
    can_manage = user.is_ceo or user.is_hr
    
    context = {
        'announcement': announcement,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/announcements/detail.html', context)


@login_required
def announcement_create(request):
    """Create a new announcement"""
    user = request.user
    
    # Only CEO or HR can create announcements
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to create announcements.')
        return redirect('company:announcements_list')
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.organization = user.organization
            announcement.created_by = user
            # Ensure target_roles is a list (not None)
            if not announcement.target_roles:
                announcement.target_roles = []
            announcement.save()
            messages.success(request, f'Announcement "{announcement.title}" created successfully!')
            return redirect('company:announcements_list')
    else:
        form = AnnouncementForm(user=user)
    
    context = {
        'form': form,
        'title': 'Create Announcement',
        'action': 'Create'
    }
    
    return render(request, 'company/announcements/form.html', context)


@login_required
def announcement_update(request, id):
    """Update an announcement"""
    user = request.user
    announcement = get_object_or_404(Announcement, id=id)
    
    # Only CEO or HR can update announcements
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to edit announcements.')
        return redirect('company:announcements_list')
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement, user=user)
        if form.is_valid():
            updated_announcement = form.save(commit=False)
            # Ensure target_roles is a list (not None)
            if not updated_announcement.target_roles:
                updated_announcement.target_roles = []
            updated_announcement.save()
            messages.success(request, f'Announcement "{announcement.title}" updated successfully!')
            return redirect('company:announcements_list')
    else:
        form = AnnouncementForm(instance=announcement, user=user)
    
    context = {
        'form': form,
        'announcement': announcement,
        'title': f'Edit Announcement: {announcement.title}',
        'action': 'Update'
    }
    
    return render(request, 'company/announcements/form.html', context)


@login_required
def announcement_delete(request, id):
    """Delete an announcement"""
    user = request.user
    announcement = get_object_or_404(Announcement, id=id)
    
    # Only CEO or HR can delete announcements
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to delete announcements.')
        return redirect('company:announcements_list')
    
    if request.method == 'POST':
        title = announcement.title
        announcement.delete()
        messages.success(request, f'Announcement "{title}" deleted successfully!')
        return redirect('company:announcements_list')
    
    context = {
        'announcement': announcement
    }
    
    return render(request, 'company/announcements/delete_confirm.html', context)


# ==================== POLICIES ====================

@login_required
def policies_list(request):
    """List all policies"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    policies = Policy.objects.filter(
        organization=user.organization,
        is_active=True
    ).select_related('created_by').order_by('-effective_date', '-created_at')
    
    # Group by category
    policies_by_category = {}
    for policy in policies:
        category = policy.get_category_display()
        if category not in policies_by_category:
            policies_by_category[category] = []
        policies_by_category[category].append(policy)
    
    can_manage = user.is_ceo or user.is_hr
    
    context = {
        'policies': policies,
        'policies_by_category': policies_by_category,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/policies/list.html', context)


@login_required
def policy_create(request):
    """Create a new policy"""
    user = request.user
    
    # Only CEO or HR can create policies
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to create policies.')
        return redirect('company:policies_list')
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = PolicyForm(request.POST, request.FILES)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.organization = user.organization
            policy.created_by = user
            policy.save()
            messages.success(request, f'Policy "{policy.title}" created successfully!')
            return redirect('company:policies_list')
    else:
        form = PolicyForm()
    
    context = {
        'form': form,
        'title': 'Create Policy',
        'action': 'Create'
    }
    
    return render(request, 'company/policies/form.html', context)


@login_required
def policy_update(request, id):
    """Update a policy"""
    user = request.user
    policy = get_object_or_404(Policy, id=id)
    
    # Only CEO or HR can update policies
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to edit policies.')
        return redirect('company:policies_list')
    
    if request.method == 'POST':
        form = PolicyForm(request.POST, request.FILES, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, f'Policy "{policy.title}" updated successfully!')
            return redirect('company:policies_list')
    else:
        form = PolicyForm(instance=policy)
    
    context = {
        'form': form,
        'policy': policy,
        'title': f'Edit Policy: {policy.title}',
        'action': 'Update'
    }
    
    return render(request, 'company/policies/form.html', context)


@login_required
def policy_delete(request, id):
    """Delete a policy"""
    user = request.user
    policy = get_object_or_404(Policy, id=id)
    
    # Only CEO or HR can delete policies
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to delete policies.')
        return redirect('company:policies_list')
    
    if request.method == 'POST':
        title = policy.title
        policy.delete()
        messages.success(request, f'Policy "{title}" deleted successfully!')
        return redirect('company:policies_list')
    
    context = {
        'policy': policy
    }
    
    return render(request, 'company/policies/delete_confirm.html', context)


# ==================== HOLIDAYS ====================

@login_required
def holidays_list(request):
    """List all holidays"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    # Get current year holidays
    current_year = timezone.now().year
    holidays = Holiday.objects.filter(
        organization=user.organization,
        date__year=current_year
    ).order_by('date')
    
    # Get upcoming holidays
    today = timezone.now().date()
    upcoming_holidays = holidays.filter(date__gte=today)[:10]
    past_holidays = holidays.filter(date__lt=today)
    
    # Group by month
    holidays_by_month = {}
    for holiday in holidays:
        month = holiday.date.strftime('%B %Y')
        if month not in holidays_by_month:
            holidays_by_month[month] = []
        holidays_by_month[month].append(holiday)
    
    can_manage = user.is_ceo or user.is_hr
    
    context = {
        'holidays': holidays,
        'upcoming_holidays': upcoming_holidays,
        'holidays_by_month': holidays_by_month,
        'current_year': current_year,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/holidays/list.html', context)


@login_required
def holiday_create(request):
    """Create a new holiday"""
    user = request.user
    
    # Only CEO or HR can create holidays
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to create holidays.')
        return redirect('company:holidays_list')
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save(commit=False)
            holiday.organization = user.organization
            holiday.created_by = user
            holiday.save()
            messages.success(request, f'Holiday "{holiday.name}" created successfully!')
            return redirect('company:holidays_list')
    else:
        form = HolidayForm()
    
    context = {
        'form': form,
        'title': 'Create Holiday',
        'action': 'Create'
    }
    
    return render(request, 'company/holidays/form.html', context)


@login_required
def holiday_update(request, id):
    """Update a holiday"""
    user = request.user
    holiday = get_object_or_404(Holiday, id=id)
    
    # Only CEO or HR can update holidays
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to edit holidays.')
        return redirect('company:holidays_list')
    
    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, f'Holiday "{holiday.name}" updated successfully!')
            return redirect('company:holidays_list')
    else:
        form = HolidayForm(instance=holiday)
    
    context = {
        'form': form,
        'holiday': holiday,
        'title': f'Edit Holiday: {holiday.name}',
        'action': 'Update'
    }
    
    return render(request, 'company/holidays/form.html', context)


@login_required
def holiday_delete(request, id):
    """Delete a holiday"""
    user = request.user
    holiday = get_object_or_404(Holiday, id=id)
    
    # Only CEO or HR can delete holidays
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to delete holidays.')
        return redirect('company:holidays_list')
    
    if request.method == 'POST':
        name = holiday.name
        holiday.delete()
        messages.success(request, f'Holiday "{name}" deleted successfully!')
        return redirect('company:holidays_list')
    
    context = {
        'holiday': holiday
    }
    
    return render(request, 'company/holidays/delete_confirm.html', context)


# ==================== EVENTS ====================

@login_required
def events_list(request):
    """List all events"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    # Get all events for organization
    events = Event.objects.filter(
        organization=user.organization
    ).prefetch_related('attendees', 'created_by').order_by('start_date')
    
    # Separate upcoming and past events
    today = timezone.now()
    upcoming_events = events.filter(start_date__gte=today)
    past_events = events.filter(start_date__lt=today)
    
    # Get events user is attending
    my_events = events.filter(attendees=user)
    
    can_manage = user.is_ceo or user.is_hr
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'my_events': my_events,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/events/list.html', context)


@login_required
def event_detail(request, id):
    """View event details"""
    user = request.user
    event = get_object_or_404(Event, id=id)
    
    # Check if user has access
    if event.organization != user.organization:
        messages.error(request, 'You do not have access to this event.')
        return redirect('company:events_list')
    
    is_attending = event.attendees.filter(id=user.id).exists()
    can_manage = user.is_ceo or user.is_hr
    
    context = {
        'event': event,
        'is_attending': is_attending,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/events/detail.html', context)


@login_required
def event_create(request):
    """Create a new event"""
    user = request.user
    
    # Only CEO or HR can create events
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to create events.')
        return redirect('company:events_list')
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = EventForm(request.POST, user=user)
        if form.is_valid():
            event = form.save(commit=False)
            event.organization = user.organization
            event.created_by = user
            event.save()
            form.save_m2m()  # Save many-to-many relationships (attendees)
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('company:events_list')
    else:
        form = EventForm(user=user)
    
    context = {
        'form': form,
        'title': 'Create Event',
        'action': 'Create'
    }
    
    return render(request, 'company/events/form.html', context)


@login_required
def event_update(request, id):
    """Update an event"""
    user = request.user
    event = get_object_or_404(Event, id=id)
    
    # Only CEO or HR can update events
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to edit events.')
        return redirect('company:events_list')
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('company:events_list')
    else:
        form = EventForm(instance=event, user=user)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Edit Event: {event.title}',
        'action': 'Update'
    }
    
    return render(request, 'company/events/form.html', context)


@login_required
def event_delete(request, id):
    """Delete an event"""
    user = request.user
    event = get_object_or_404(Event, id=id)
    
    # Only CEO or HR can delete events
    if not user.is_ceo and not user.is_hr:
        messages.error(request, 'You do not have permission to delete events.')
        return redirect('company:events_list')
    
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted successfully!')
        return redirect('company:events_list')
    
    context = {
        'event': event
    }
    
    return render(request, 'company/events/delete_confirm.html', context)


@login_required
def event_join(request, id):
    """Join an event"""
    user = request.user
    event = get_object_or_404(Event, id=id)
    
    # Check if user has access
    if event.organization != user.organization:
        messages.error(request, 'You do not have access to this event.')
        return redirect('company:events_list')
    
    if event.attendees.filter(id=user.id).exists():
        messages.info(request, 'You are already attending this event.')
    else:
        event.attendees.add(user)
        messages.success(request, f'You have joined the event "{event.title}"!')
    
    return redirect('company:event_detail', id=id)


@login_required
def event_leave(request, id):
    """Leave an event"""
    user = request.user
    event = get_object_or_404(Event, id=id)
    
    if event.attendees.filter(id=user.id).exists():
        event.attendees.remove(user)
        messages.success(request, f'You have left the event "{event.title}".')
    else:
        messages.info(request, 'You are not attending this event.')
    
    return redirect('company:event_detail', id=id)


# ==================== BIRTHDAYS & ANNIVERSARIES ====================

@login_required
def birthdays_anniversaries(request):
    """View birthdays and anniversaries"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    today = timezone.now().date()
    current_month = today.month
    current_day = today.day
    
    # Get all users in organization
    users = User.objects.filter(
        organization=user.organization,
        is_active=True
    )
    
    # Get birthdays this month - directly from User model
    birthdays_this_month = []
    birthdays_today = []
    
    for u in users:
        if u.birth_date:
            bd = u.birth_date
            if bd.month == current_month:
                birthdays_this_month.append({
                    'user': u,
                    'date': bd,
                    'is_today': bd.day == current_day
                })
                if bd.day == current_day:
                    birthdays_today.append(u)
    
    # Sort by day
    birthdays_this_month.sort(key=lambda x: x['date'].day)
    
    # Get anniversaries this month - directly from User model
    anniversaries_this_month = []
    anniversaries_today = []
    
    for u in users:
        if u.date_of_joining:
            jd = u.date_of_joining
            if jd.month == current_month:
                years = today.year - jd.year
                if today.month < jd.month or (today.month == jd.month and today.day < jd.day):
                    years -= 1
                anniversaries_this_month.append({
                    'user': u,
                    'date': jd,
                    'years': years,
                    'is_today': jd.day == current_day
                })
                if jd.day == current_day:
                    anniversaries_today.append({
                        'user': u,
                        'years': years
                    })
    
    # Sort by day
    anniversaries_this_month.sort(key=lambda x: x['date'].day)
    
    can_manage = user.is_ceo or user.is_hr
    
    context = {
        'birthdays_this_month': birthdays_this_month,
        'birthdays_today': birthdays_today,
        'anniversaries_this_month': anniversaries_this_month,
        'anniversaries_today': anniversaries_today,
        'current_month': today.strftime('%B %Y'),
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/birthdays_anniversaries/list.html', context)


@login_required
def birthday_anniversary_edit(request, user_id):
    """Edit birthday and anniversary for a user"""
    current_user = request.user
    target_user = get_object_or_404(User, id=user_id)
    
    # Only CEO, HR, or the user themselves can edit
    if not current_user.is_ceo and not current_user.is_hr and current_user.id != user_id:
        messages.error(request, 'You do not have permission to edit this information.')
        return redirect('company:birthdays_anniversaries')
    
    # Get or create birthday/anniversary record (for form - signal will sync)
    ba, created = BirthdayAnniversary.objects.get_or_create(user=target_user)
    
    # Sync from User to BA for form display
    ba.birth_date = target_user.birth_date
    ba.joining_date = target_user.date_of_joining
    ba.save()
    
    if request.method == 'POST':
        form = BirthdayAnniversaryForm(request.POST, instance=ba)
        if form.is_valid():
            # Update User model directly (signal will sync to BA)
            target_user.birth_date = form.cleaned_data['birth_date']
            target_user.date_of_joining = form.cleaned_data['joining_date']
            target_user.save()  # Signal will automatically update BirthdayAnniversary
            messages.success(request, f'Birthday and anniversary information updated for {target_user.get_full_name() or target_user.username}!')
            return redirect('company:birthdays_anniversaries')
    else:
        form = BirthdayAnniversaryForm(instance=ba)
    
    context = {
        'form': form,
        'target_user': target_user,
        'title': f'Edit Birthday & Anniversary: {target_user.get_full_name() or target_user.username}',
        'action': 'Update'
    }
    
    return render(request, 'company/birthdays_anniversaries/form.html', context)


# ==================== COMPANY INDEX ====================

@login_required
def company_index(request):
    """Company information index page"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    today = timezone.now().date()
    
    # Get recent announcements (last 5)
    recent_announcements = Announcement.objects.filter(
        organization=user.organization
    ).select_related('created_by').order_by('-is_pinned', '-created_at')[:5]
    
    # Filter active announcements
    recent_announcements = [a for a in recent_announcements if a.is_active()]
    
    # Get upcoming holidays (next 5)
    upcoming_holidays = Holiday.objects.filter(
        organization=user.organization,
        date__gte=today
    ).order_by('date')[:5]
    
    # Get upcoming events (next 5)
    upcoming_events = Event.objects.filter(
        organization=user.organization,
        start_date__gte=timezone.now()
    ).prefetch_related('attendees').order_by('start_date')[:5]
    
    # Get today's birthdays and anniversaries - directly from User model
    current_month = today.month
    current_day = today.day
    
    birthdays_today = []
    anniversaries_today = []
    
    users = User.objects.filter(
        organization=user.organization,
        is_active=True
    )
    
    for u in users:
        # Check birthday
        if u.birth_date and u.birth_date.month == current_month and u.birth_date.day == current_day:
            birthdays_today.append(u)
        # Check anniversary
        if u.date_of_joining and u.date_of_joining.month == current_month and u.date_of_joining.day == current_day:
            years = today.year - u.date_of_joining.year
            if today.month < u.date_of_joining.month or (today.month == u.date_of_joining.month and today.day < u.date_of_joining.day):
                years -= 1
            anniversaries_today.append({'user': u, 'years': years})
    
    # Get active policies count
    policies_count = Policy.objects.filter(
        organization=user.organization,
        is_active=True
    ).count()
    
    can_manage = user.is_ceo or user.is_hr
    
    context = {
        'recent_announcements': recent_announcements,
        'upcoming_holidays': upcoming_holidays,
        'upcoming_events': upcoming_events,
        'birthdays_today': birthdays_today,
        'anniversaries_today': anniversaries_today,
        'policies_count': policies_count,
        'can_manage': can_manage,
        'user': user
    }
    
    return render(request, 'company/index.html', context)
