from django.contrib import admin
from company.models import Announcement, Policy, Holiday, Event, BirthdayAnniversary


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'priority', 'is_pinned', 'created_by', 'created_at', 'expires_at']
    list_filter = ['priority', 'is_pinned', 'created_at', 'organization']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'version', 'is_active', 'effective_date', 'created_by', 'created_at']
    list_filter = ['category', 'is_active', 'effective_date', 'organization']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'holiday_type', 'is_recurring', 'organization', 'created_by']
    list_filter = ['holiday_type', 'is_recurring', 'date', 'organization']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'location', 'is_virtual', 'created_by']
    list_filter = ['event_type', 'is_virtual', 'start_date', 'organization']
    search_fields = ['title', 'description', 'location']
    filter_horizontal = ['attendees']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BirthdayAnniversary)
class BirthdayAnniversaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date', 'joining_date', 'get_years_of_service_display']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'get_years_of_service_display']
    
    def get_years_of_service_display(self, obj):
        years = obj.get_years_of_service()
        return f"{years} years" if years is not None else "N/A"
    get_years_of_service_display.short_description = 'Years of Service'
