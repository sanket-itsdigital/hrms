from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import calendar
import csv

from attendance.models import Attendance
from attendance.forms import AttendanceForm, AttendanceBulkForm
from accounts.models import User
from company.models import Holiday


@login_required
def list_attendance(request):
    """List all attendance records with filtering"""
    user = request.user

    # Get user's organization
    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    organization = user.organization

    # Base queryset
    if user.is_ceo or user.is_hr:
        # CEO/HR can see all attendance in organization
        # but exclude attendance records for users with role 'CEO' and for superusers (admin accounts)
        attendances = (
            Attendance.objects.filter(organization=organization)
            .exclude(user__role__name="CEO")
            .exclude(user__is_superuser=True)
            .select_related("user", "marked_by")
            .order_by("-date", "user__first_name")
        )
    else:
        # Others see only their own attendance
        attendances = (
            Attendance.objects.filter(user=user, organization=organization)
            .select_related("user", "marked_by")
            .order_by("-date")
        )

    # Filtering
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    user_filter = request.GET.get("user", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if search_query:
        attendances = attendances.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(notes__icontains=search_query)
        )

    if status_filter:
        attendances = attendances.filter(status=status_filter)

    if user_filter and (user.is_ceo or user.is_hr):
        attendances = attendances.filter(user_id=user_filter)

    if date_from:
        attendances = attendances.filter(date__gte=date_from)

    if date_to:
        attendances = attendances.filter(date__lte=date_to)

    # Pagination
    paginator = Paginator(attendances, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get users for filter dropdown (only for CEO/HR)
    users = None
    if user.is_ceo or user.is_hr:
        users = (
            User.objects.filter(organization=organization, is_active=True)
            .exclude(role__name="CEO")
            .exclude(is_superuser=True)
            .order_by("first_name", "last_name")
        )

    # Statistics
    total_records = attendances.count()
    present_count = attendances.filter(status="PRESENT").count()
    absent_count = attendances.filter(status="ABSENT").count()
    leave_count = attendances.filter(status="LEAVE").count()
    late_count = attendances.filter(status="LATE").count()
    wfh_count = attendances.filter(status="WORK_FROM_HOME").count()

    context = {
        "page_obj": page_obj,
        "attendances": page_obj,
        "users": users,
        "total_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "leave_count": leave_count,
        "late_count": late_count,
        "wfh_count": wfh_count,
        "search_query": search_query,
        "status_filter": status_filter,
        "user_filter": user_filter,
        "date_from": date_from,
        "date_to": date_to,
        "can_edit": user.is_ceo or user.is_hr,
    }

    return render(request, "attendance/list.html", context)


@login_required
def my_attendance(request):
    """View own attendance in calendar format with punch in/out functionality"""
    user = request.user

    # CEO does not need to punch in/out
    if user.is_ceo:
        messages.info(request, "Attendance punch in/out is not required for CEO.")
        return redirect("accounts:dashboard")

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    organization = user.organization

    # Handle punch in/out - use IST date
    today = localtime(timezone.now()).date()
    today_attendance, created = Attendance.objects.get_or_create(
        user=user,
        organization=organization,
        date=today,
        defaults={"status": "PRESENT", "marked_by": user},
    )

    if request.method == "POST":
        action = request.POST.get("action")
        # Get current time in IST
        current_datetime = localtime(timezone.now())
        current_time = current_datetime.time()

        if action == "punch_in":
            if not today_attendance.check_in:
                today_attendance.check_in = current_time
                today_attendance.status = "PRESENT"
                today_attendance.marked_by = user
                today_attendance.save()
                messages.success(
                    request, f'Punched in at {current_time.strftime("%H:%M:%S")} IST'
                )
            else:
                messages.warning(request, "You have already punched in today.")

        elif action == "punch_out":
            if today_attendance.check_in and not today_attendance.check_out:
                today_attendance.check_out = current_time
                today_attendance.marked_by = user
                today_attendance.save()
                messages.success(
                    request, f'Punched out at {current_time.strftime("%H:%M:%S")} IST'
                )
            elif not today_attendance.check_in:
                messages.warning(request, "Please punch in first.")
            else:
                messages.warning(request, "You have already punched out today.")

        return redirect("attendance:my-attendance")

    # Get year and month from request
    year = request.GET.get("year", timezone.now().year)
    month = request.GET.get("month", timezone.now().month)

    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month

    # Get attendance for the month
    attendances = Attendance.objects.filter(
        user=user, organization=organization, date__year=year, date__month=month
    ).order_by("date")

    # Refresh today's attendance
    today_attendance.refresh_from_db()

    # Convert check_in and check_out times to IST for display
    # Note: TimeField doesn't store timezone, so old records might be in UTC
    # We'll convert old UTC times (created before timezone change) to IST
    check_in_ist = today_attendance.check_in
    check_out_ist = today_attendance.check_out

    # If attendance was created today and time seems like UTC (very early morning < 6 AM),
    # and current IST time is much later, convert it to IST
    if today_attendance.check_in and today_attendance.date == today:
        current_ist_time = localtime(timezone.now()).time()
        # If stored time is before 6 AM but current IST time is after 10 AM,
        # it's likely an old UTC time that needs conversion
        if (
            today_attendance.check_in.hour < 6
            and current_ist_time.hour >= 10
            and today_attendance.created_at.date() == today
        ):
            # Convert UTC to IST (add 5 hours 30 minutes)
            from datetime import timedelta

            check_in_dt = datetime.combine(
                today_attendance.date, today_attendance.check_in
            )
            check_in_ist_dt = check_in_dt + timedelta(hours=5, minutes=30)
            check_in_ist = check_in_ist_dt.time()
            # Update the record with IST time
            today_attendance.check_in = check_in_ist
            today_attendance.save(update_fields=["check_in"])

    if today_attendance.check_out and today_attendance.date == today:
        current_ist_time = localtime(timezone.now()).time()
        # Similar check for check_out
        if (
            today_attendance.check_out.hour < 6
            and current_ist_time.hour >= 10
            and today_attendance.updated_at.date() == today
        ):
            from datetime import timedelta

            check_out_dt = datetime.combine(
                today_attendance.date, today_attendance.check_out
            )
            check_out_ist_dt = check_out_dt + timedelta(hours=5, minutes=30)
            check_out_ist = check_out_ist_dt.time()
            # Update the record with IST time
            today_attendance.check_out = check_out_ist
            today_attendance.save(update_fields=["check_out"])

    # Calculate work duration if both times are present
    work_duration = None
    if check_in_ist and check_out_ist:
        from datetime import date as date_obj

        check_in_dt = datetime.combine(date_obj.today(), check_in_ist)
        check_out_dt = datetime.combine(date_obj.today(), check_out_ist)
        duration = check_out_dt - check_in_dt
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        work_duration = f"{hours}h {minutes}m"

    # Holidays (Saturday off, national, etc.) for calendar display
    holidays_by_date = Holiday.get_holidays_by_date_for_month(organization, year, month)
    holiday_dates = set(holidays_by_date.keys())

    # Create calendar data
    cal = calendar.monthcalendar(year, month)
    calendar_data = []

    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                date = datetime(year, month, day).date()
                attendance = attendances.filter(date=date).first()
                is_sunday = date.weekday() == 6  # Monday=0, Sunday=6
                is_company_holiday = date in holiday_dates
                is_holiday = is_sunday or is_company_holiday
                is_future = date > today
                week_data.append({
                    "day": day,
                    "date": date,
                    "attendance": attendance,
                    "is_sunday": is_sunday,
                    "is_holiday": is_holiday,
                    "holiday_names": holidays_by_date.get(date, []),
                    "is_future": is_future,
                })
        calendar_data.append(week_data)

    # Statistics for the month
    total_days = len([d for week in cal for d in week if d != 0])
    present_days = attendances.filter(status="PRESENT").count()
    absent_days = attendances.filter(status="ABSENT").count()
    leave_days = attendances.filter(status="LEAVE").count()
    late_days = attendances.filter(status="LATE").count()
    half_days = attendances.filter(status="HALF_DAY").count()
    wfh_days = attendances.filter(status="WORK_FROM_HOME").count()

    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    context = {
        "calendar_data": calendar_data,
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "present_days": present_days,
        "absent_days": absent_days,
        "leave_days": leave_days,
        "late_days": late_days,
        "half_days": half_days,
        "wfh_days": wfh_days,
        "total_days": total_days,
        "today_attendance": today_attendance,
        "today": today,
        "work_duration": work_duration,
        "check_in_ist": check_in_ist,
        "check_out_ist": check_out_ist,
    }

    return render(request, "attendance/my_attendance.html", context)


@login_required
def attendance_calendar_view(request):
    """Calendar view of attendance for CEO/HR with user filter (view only, no punch in/out)."""
    user = request.user

    if not (user.is_ceo or user.is_hr):
        messages.error(request, "You do not have permission to view this page.")
        return redirect("accounts:dashboard")

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    organization = user.organization

    # Users for filter (exclude CEO and superusers, same as list)
    users = (
        User.objects.filter(organization=organization, is_active=True)
        .exclude(role__name="CEO")
        .exclude(is_superuser=True)
        .order_by("first_name", "last_name", "email")
    )

    user_filter = request.GET.get("user", "")
    try:
        selected_user_id = int(user_filter) if user_filter else None
    except (ValueError, TypeError):
        selected_user_id = None

    # Resolve which user's calendar to show
    selected_user = None
    if selected_user_id and users.filter(id=selected_user_id).exists():
        selected_user = users.get(id=selected_user_id)
    elif users.exists():
        selected_user = users.first()
        selected_user_id = selected_user.id

    year = request.GET.get("year", timezone.now().year)
    month = request.GET.get("month", timezone.now().month)
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month

    calendar_data = []
    present_days = absent_days = leave_days = late_days = half_days = wfh_days = total_days = 0

    if selected_user:
        attendances = Attendance.objects.filter(
            user=selected_user,
            organization=organization,
            date__year=year,
            date__month=month,
        ).order_by("date")

        holidays_by_date = Holiday.get_holidays_by_date_for_month(organization, year, month)
        holiday_dates = set(holidays_by_date.keys())

        today = timezone.now().date()
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append(None)
                else:
                    date = datetime(year, month, day).date()
                    att = attendances.filter(date=date).first()
                    is_sunday = date.weekday() == 6
                    is_company_holiday = date in holiday_dates
                    is_holiday = is_sunday or is_company_holiday
                    is_future = date > today
                    week_data.append({
                        "day": day,
                        "date": date,
                        "attendance": att,
                        "is_sunday": is_sunday,
                        "is_holiday": is_holiday,
                        "holiday_names": holidays_by_date.get(date, []),
                        "is_future": is_future,
                    })
            calendar_data.append(week_data)

        total_days = len([d for week in cal for d in week if d != 0])
        present_days = attendances.filter(status="PRESENT").count()
        absent_days = attendances.filter(status="ABSENT").count()
        leave_days = attendances.filter(status="LEAVE").count()
        late_days = attendances.filter(status="LATE").count()
        half_days = attendances.filter(status="HALF_DAY").count()
        wfh_days = attendances.filter(status="WORK_FROM_HOME").count()

    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    today = timezone.now().date()

    # Build nav links preserving user filter
    base_query = f"&user={selected_user_id}" if selected_user_id else ""

    context = {
        "calendar_data": calendar_data,
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "present_days": present_days,
        "absent_days": absent_days,
        "leave_days": leave_days,
        "late_days": late_days,
        "half_days": half_days,
        "wfh_days": wfh_days,
        "total_days": total_days,
        "users": users,
        "selected_user": selected_user,
        "user_filter": selected_user_id,
        "base_query": base_query,
        "today": today,
    }

    return render(request, "attendance/calendar_view.html", context)


@login_required
def create_attendance(request):
    """Create a new attendance record"""
    user = request.user

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(
            request, "You do not have permission to create attendance records."
        )
        return redirect("attendance:my-attendance")

    if request.method == "POST":
        form = AttendanceForm(request.POST, user=user, organization=user.organization)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.organization = user.organization
            attendance.marked_by = user
            attendance.save()
            messages.success(
                request,
                f"Attendance record created successfully for {attendance.user.get_full_name()}!",
            )
            return redirect("attendance:list")
    else:
        form = AttendanceForm(user=user, organization=user.organization)

    return render(
        request,
        "attendance/form.html",
        {"form": form, "title": "Create Attendance Record"},
    )


@login_required
def update_attendance(request, id):
    """Update an existing attendance record"""
    user = request.user
    attendance = get_object_or_404(Attendance, id=id)

    # Check permissions
    if not (user.is_ceo or user.is_hr):
        if attendance.user != user:
            messages.error(
                request, "You do not have permission to edit this attendance record."
            )
            return redirect("attendance:my-attendance")

    if request.method == "POST":
        form = AttendanceForm(
            request.POST, instance=attendance, user=user, organization=user.organization
        )
        if form.is_valid():
            attendance = form.save(commit=False)
            if user.is_ceo or user.is_hr:
                attendance.marked_by = user
            attendance.save()
            messages.success(request, "Attendance record updated successfully!")
            return redirect("attendance:list")
    else:
        form = AttendanceForm(
            instance=attendance, user=user, organization=user.organization
        )

    return render(
        request,
        "attendance/form.html",
        {"form": form, "attendance": attendance, "title": "Update Attendance Record"},
    )


@login_required
def delete_attendance(request, id):
    """Delete an attendance record"""
    user = request.user
    attendance = get_object_or_404(Attendance, id=id)

    # Check permissions
    if not (user.is_ceo or user.is_hr):
        messages.error(
            request, "You do not have permission to delete attendance records."
        )
        return redirect("attendance:my-attendance")

    if request.method == "POST":
        user_name = attendance.user.get_full_name()
        attendance.delete()
        messages.success(
            request, f"Attendance record for {user_name} deleted successfully!"
        )
        return redirect("attendance:list")

    return render(request, "attendance/delete_confirm.html", {"attendance": attendance})


@login_required
def bulk_attendance(request):
    """Bulk attendance entry"""
    user = request.user

    if not (user.is_ceo or user.is_hr):
        messages.error(
            request, "You do not have permission to perform bulk attendance entry."
        )
        return redirect("attendance:my-attendance")

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = AttendanceBulkForm(
            request.POST, user=user, organization=user.organization
        )
        if form.is_valid():
            date = form.cleaned_data["date"]
            users = form.cleaned_data["users"]
            status = form.cleaned_data["status"]
            check_in = form.cleaned_data.get("check_in")
            check_out = form.cleaned_data.get("check_out")

            created_count = 0
            updated_count = 0
            skipped_count = 0

            for user_obj in users:
                attendance, created = Attendance.objects.get_or_create(
                    user=user_obj,
                    date=date,
                    organization=user.organization,
                    defaults={
                        "status": status,
                        "check_in": check_in,
                        "check_out": check_out,
                        "marked_by": user,
                    },
                )

                if created:
                    created_count += 1
                else:
                    # Update existing record
                    attendance.status = status
                    if check_in:
                        attendance.check_in = check_in
                    if check_out:
                        attendance.check_out = check_out
                    attendance.marked_by = user
                    attendance.save()
                    updated_count += 1

            messages.success(
                request,
                f"Bulk attendance updated: {created_count} created, {updated_count} updated for {date}.",
            )
            return redirect("attendance:list")
    else:
        form = AttendanceBulkForm(user=user, organization=user.organization)

    return render(
        request,
        "attendance/bulk_form.html",
        {"form": form, "title": "Bulk Attendance Entry"},
    )


@login_required
def attendance_report(request):
    """Generate attendance reports"""
    user = request.user

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("accounts:dashboard")

    organization = user.organization

    # Get report parameters
    report_type = request.GET.get("type", "monthly")  # monthly or yearly
    year = request.GET.get("year", timezone.now().year)
    month = request.GET.get("month", timezone.now().month)
    user_id = request.GET.get("user", "")

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
                organization=organization, user_id=user_id
            )
        else:
            attendances = (
                Attendance.objects.filter(organization=organization)
                .exclude(user__role__name="CEO")
                .exclude(user__is_superuser=True)
            )
    else:
        attendances = Attendance.objects.filter(user=user, organization=organization)

    # Filter by date range
    if report_type == "monthly" and month:
        attendances = attendances.filter(date__year=year, date__month=month)
        date_range = f"{calendar.month_name[month]} {year}"
    else:
        attendances = attendances.filter(date__year=year)
        date_range = f"{year}"

    # Calculate statistics
    total_days = attendances.count()
    present_days = attendances.filter(status="PRESENT").count()
    absent_days = attendances.filter(status="ABSENT").count()
    leave_days = attendances.filter(status="LEAVE").count()
    late_days = attendances.filter(status="LATE").count()
    half_days = attendances.filter(status="HALF_DAY").count()
    wfh_days = attendances.filter(status="WORK_FROM_HOME").count()

    # Group by user if viewing all
    if user.is_ceo or user.is_hr and not user_id:
        user_stats = (
            attendances.values(
                "user__id", "user__first_name", "user__last_name", "user__email"
            )
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status="PRESENT")),
                absent=Count("id", filter=Q(status="ABSENT")),
                leave=Count("id", filter=Q(status="LEAVE")),
                late=Count("id", filter=Q(status="LATE")),
                half_day=Count("id", filter=Q(status="HALF_DAY")),
                wfh=Count("id", filter=Q(status="WORK_FROM_HOME")),
            )
            .order_by("user__first_name", "user__last_name")
        )
    else:
        user_stats = None

    # Get users for filter
    users = None
    if user.is_ceo or user.is_hr:
        users = (
            User.objects.filter(organization=organization, is_active=True)
            .exclude(role__name="CEO")
            .exclude(is_superuser=True)
            .order_by("first_name", "last_name")
        )

    context = {
        "report_type": report_type,
        "year": year,
        "month": month,
        "date_range": date_range,
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "leave_days": leave_days,
        "late_days": late_days,
        "half_days": half_days,
        "wfh_days": wfh_days,
        "user_stats": user_stats,
        "users": users,
        "selected_user": user_id,
    }

    return render(request, "attendance/report.html", context)


@login_required
def export_attendance(request):
    """Export attendance data to CSV"""
    user = request.user

    if not user.organization:
        messages.error(request, "You are not associated with an organization.")
        return redirect("attendance:list")

    organization = user.organization

    # Get filter parameters
    year = request.GET.get("year", timezone.now().year)
    month = request.GET.get("month", "")
    user_id = request.GET.get("user", "")
    status = request.GET.get("status", "")

    # Base queryset
    if user.is_ceo or user.is_hr:
        attendances = (
            Attendance.objects.filter(organization=organization)
            .exclude(user__role__name="CEO")
            .exclude(user__is_superuser=True)
        )
        if user_id:
            attendances = attendances.filter(user_id=user_id)
    else:
        attendances = Attendance.objects.filter(user=user, organization=organization)

    # Apply filters
    if year:
        attendances = attendances.filter(date__year=year)
    if month:
        attendances = attendances.filter(date__month=month)
    if status:
        attendances = attendances.filter(status=status)

    attendances = attendances.select_related("user", "marked_by").order_by(
        "-date", "user__first_name"
    )

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    filename = f'attendance_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Date",
            "Employee Name",
            "Email",
            "Status",
            "Check In",
            "Check Out",
            "Notes",
            "Marked By",
            "Created At",
        ]
    )

    for attendance in attendances:
        writer.writerow(
            [
                attendance.date.strftime("%Y-%m-%d"),
                attendance.user.get_full_name(),
                attendance.user.email,
                attendance.get_status_display(),
                attendance.check_in.strftime("%H:%M:%S") if attendance.check_in else "",
                (
                    attendance.check_out.strftime("%H:%M:%S")
                    if attendance.check_out
                    else ""
                ),
                attendance.notes or "",
                attendance.marked_by.get_full_name() if attendance.marked_by else "",
                attendance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    return response
