from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'status', 'check_in', 'check_out', 'marked_by', 'created_at']
    list_filter = ['status', 'date', 'organization', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'user', 'date', 'status')
        }),
        ('Time Tracking', {
            'fields': ('check_in', 'check_out')
        }),
        ('Additional Information', {
            'fields': ('notes', 'marked_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'organization', 'marked_by')
