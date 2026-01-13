from django.contrib import admin
from django.utils.html import format_html
from .models import Leave, LeaveBalance


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'status', 'date_from', 'date_to', 'days', 'approved_by', 'applied_at']
    list_filter = ['status', 'leave_type', 'date_from', 'applied_at', 'organization']
    search_fields = ['user__username', 'user__email', 'reason', 'rejection_reason']
    readonly_fields = ['days', 'applied_at', 'updated_at', 'preview_attachment']
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'user', 'leave_type', 'status')
        }),
        ('Leave Details', {
            'fields': ('date_from', 'date_to', 'days', 'reason', 'attachment', 'preview_attachment')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_attachment(self, obj):
        if obj.attachment:
            return format_html('<a href="{}" target="_blank">View Attachment</a>', obj.attachment.url)
        return "No attachment"
    preview_attachment.short_description = 'Attachment'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'organization', 'approved_by')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'year', 'total_days', 'used_days', 'remaining_days']
    list_filter = ['leave_type', 'year', 'organization']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['remaining_days', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'user', 'leave_type', 'year')
        }),
        ('Leave Balance', {
            'fields': ('total_days', 'used_days', 'remaining_days')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
