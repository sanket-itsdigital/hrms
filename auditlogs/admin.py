from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'object_type', 'object_repr', 'action_by', 'ip_address', 'created_at']
    list_filter = ['action_type', 'object_type', 'organization', 'created_at']
    search_fields = ['object_repr', 'action_by__username', 'description', 'ip_address']
    readonly_fields = ['created_at', 'formatted_old_value', 'formatted_new_value']
    date_hierarchy = 'created_at'
    list_per_page = 100
    can_delete = False  # Audit logs should not be deleted
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'action_by', 'action_type', 'object_type', 'object_id', 'object_repr')
        }),
        ('Changes', {
            'fields': ('formatted_old_value', 'formatted_new_value', 'description')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_old_value(self, obj):
        if obj.old_value:
            import json
            return format_html('<pre>{}</pre>', json.dumps(obj.old_value, indent=2))
        return "-"
    formatted_old_value.short_description = 'Old Value'
    
    def formatted_new_value(self, obj):
        if obj.new_value:
            import json
            return format_html('<pre>{}</pre>', json.dumps(obj.new_value, indent=2))
        return "-"
    formatted_new_value.short_description = 'New Value'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('action_by', 'organization')
    
    def has_add_permission(self, request):
        return False  # Audit logs should only be created automatically
    
    def has_delete_permission(self, request, obj=None):
        return False  # Audit logs should not be deleted
