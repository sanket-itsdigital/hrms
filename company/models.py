from django.db import models
from django.utils import timezone
from accounts.models import User
from organizations.models import Organization


class Announcement(models.Model):
    """
    Model for company announcements and news updates
    """
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_pinned = models.BooleanField(default=False, help_text="Pin this announcement to the top")
    target_roles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of role names (e.g., ['DEV', 'PM']). Empty list means all roles."
    )
    attachment = models.FileField(
        upload_to='announcements/',
        blank=True,
        null=True,
        help_text="Optional attachment file"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_announcements',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Announcement will be hidden after this date"
    )

    class Meta:
        db_table = 'announcements'
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    def is_active(self):
        """Check if announcement is still active"""
        if self.expires_at:
            return timezone.now() < self.expires_at
        return True


class Policy(models.Model):
    """
    Model for company policy documents
    """
    CATEGORY_CHOICES = [
        ('HR', 'HR Policies'),
        ('IT', 'IT Policies'),
        ('FINANCE', 'Finance Policies'),
        ('LEAVE', 'Leave Policies'),
        ('ATTENDANCE', 'Attendance Policies'),
        ('CODE_OF_CONDUCT', 'Code of Conduct'),
        ('OTHER', 'Other'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='policies'
    )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHER')
    description = models.TextField(blank=True, null=True)
    document = models.FileField(
        upload_to='policies/',
        help_text="Policy document file (PDF, DOC, etc.)"
    )
    version = models.CharField(max_length=20, default='1.0', help_text="Policy version number")
    is_active = models.BooleanField(default=True)
    effective_date = models.DateField(help_text="Date when policy becomes effective")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_policies',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policies'
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'
        ordering = ['-effective_date', '-created_at']

    def __str__(self):
        return f"{self.title} (v{self.version})"


class Holiday(models.Model):
    """
    Model for company holiday calendar
    """
    HOLIDAY_TYPE_CHOICES = [
        ('NATIONAL', 'National Holiday'),
        ('REGIONAL', 'Regional Holiday'),
        ('COMPANY', 'Company Holiday'),
        ('SATURDAY_OFF', 'Saturday Off'),
        ('FESTIVAL', 'Festival'),
        ('OTHER', 'Other'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='holidays'
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPE_CHOICES, default='NATIONAL')
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(
        default=False,
        help_text="If checked, this holiday repeats every year"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_holidays',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'holidays'
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
        ordering = ['date']
        unique_together = ['organization', 'date', 'name']

    def __str__(self):
        return f"{self.name} - {self.date}"

    def is_upcoming(self):
        """Check if holiday is in the future"""
        return self.date >= timezone.now().date()

    @staticmethod
    def get_non_working_dates_for_month(organization, year, month):
        """
        Return a set of dates in the given month that are non-working:
        Sundays + all holidays (national, Saturday off, etc.) for the organization.
        Used for payroll and attendance so salary is not cut for these days.
        """
        import calendar as cal
        from datetime import date
        total_days = cal.monthrange(year, month)[1]
        non_working = set()
        for day in range(1, total_days + 1):
            d = date(year, month, day)
            if d.weekday() == 6:  # Sunday
                non_working.add(d)
        holiday_dates = set(
            Holiday.objects.filter(
                organization=organization,
                date__year=year,
                date__month=month,
            ).values_list('date', flat=True)
        )
        non_working.update(holiday_dates)
        return non_working

    @staticmethod
    def get_holidays_by_date_for_month(organization, year, month):
        """Return dict of date -> list of holiday names for calendar display."""
        from collections import defaultdict
        by_date = defaultdict(list)
        qs = Holiday.objects.filter(
            organization=organization,
            date__year=year,
            date__month=month,
        ).order_by('date')
        for h in qs:
            by_date[h.date].append(h.name)
        return dict(by_date)


class RecurringHolidayRule(models.Model):
    """
    Recurring holiday by weekday occurrence, e.g. "2nd Saturday" or "4th Saturday" of every month.
    All users see these days as holiday in their calendar and payroll does not deduct for them.
    """
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='recurring_holiday_rules',
    )
    name = models.CharField(max_length=255, help_text='e.g. 2nd Saturday Off')
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)  # 0=Mon, 5=Sat, 6=Sun
    week_of_month = models.PositiveSmallIntegerField(
        help_text='1=1st occurrence in month, 2=2nd, 3=3rd, 4=4th, 5=5th',
    )  # 1-5

    class Meta:
        db_table = 'recurring_holiday_rules'
        verbose_name = 'Recurring Holiday Rule'
        verbose_name_plural = 'Recurring Holiday Rules'
        unique_together = ['organization', 'weekday', 'week_of_month']
        ordering = ['weekday', 'week_of_month']

    def __str__(self):
        return f"{self.name} (org {self.organization_id})"

    def get_date_for_month(self, year, month):
        """Return the date for this rule in the given year/month, or None if not possible (e.g. 5th Saturday when month has only 4)."""
        import calendar as cal
        from datetime import date
        total_days = cal.monthrange(year, month)[1]
        count = 0
        for day in range(1, total_days + 1):
            d = date(year, month, day)
            if d.weekday() == self.weekday:
                count += 1
                if count == self.week_of_month:
                    return d
        return None


class Event(models.Model):
    """
    Model for company events management
    """
    EVENT_TYPE_CHOICES = [
        ('MEETING', 'Meeting'),
        ('TRAINING', 'Training'),
        ('CELEBRATION', 'Celebration'),
        ('TEAM_BUILDING', 'Team Building'),
        ('CONFERENCE', 'Conference'),
        ('WORKSHOP', 'Workshop'),
        ('OTHER', 'Other'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='events'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='MEETING')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    venue_link = models.URLField(blank=True, null=True, help_text="Online meeting link if virtual")
    is_virtual = models.BooleanField(default=False)
    attendees = models.ManyToManyField(
        User,
        related_name='events_attending',
        blank=True,
        help_text="Users invited to this event"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_events',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} - {self.start_date.date()}"

    def is_upcoming(self):
        """Check if event is in the future"""
        return self.start_date > timezone.now()

    def is_ongoing(self):
        """Check if event is currently happening"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class BirthdayAnniversary(models.Model):
    """
    Model to track employee birthdays and work anniversaries
    This is automatically populated from User model data
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='birthday_anniversary'
    )
    birth_date = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True, help_text="Date when employee joined the company")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'birthday_anniversaries'
        verbose_name = 'Birthday & Anniversary'
        verbose_name_plural = 'Birthdays & Anniversaries'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Birthday & Anniversary"

    def get_birthday_this_month(self):
        """Check if birthday is this month"""
        if not self.birth_date:
            return False
        today = timezone.now().date()
        return self.birth_date.month == today.month

    def get_birthday_today(self):
        """Check if birthday is today"""
        if not self.birth_date:
            return False
        today = timezone.now().date()
        return self.birth_date.month == today.month and self.birth_date.day == today.day

    def get_anniversary_this_month(self):
        """Check if work anniversary is this month"""
        if not self.joining_date:
            return False
        today = timezone.now().date()
        return self.joining_date.month == today.month

    def get_anniversary_today(self):
        """Check if work anniversary is today"""
        if not self.joining_date:
            return False
        today = timezone.now().date()
        return self.joining_date.month == today.month and self.joining_date.day == today.day

    def get_years_of_service(self):
        """Calculate years of service"""
        if not self.joining_date:
            return None
        today = timezone.now().date()
        years = today.year - self.joining_date.year
        if today.month < self.joining_date.month or (today.month == self.joining_date.month and today.day < self.joining_date.day):
            years -= 1
        return years
