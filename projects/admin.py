from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectAssignment, ProjectAttachment, Milestone, Payment


class ProjectAttachmentInline(admin.TabularInline):
    model = ProjectAttachment
    extra = 1
    fields = ['file', 'name', 'description']


class ProjectAssignmentInline(admin.TabularInline):
    model = ProjectAssignment
    extra = 1
    fields = ['user', 'role', 'assigned_by', 'is_active']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'status', 'priority', 'project_manager', 'completion_percentage', 'deadline', 'created_at']
    list_filter = ['status', 'priority', 'organization', 'created_at', 'deadline']
    search_fields = ['name', 'description', 'client_name', 'client_email', 'client_company']
    readonly_fields = ['created_at', 'updated_at', 'completion_percentage']
    date_hierarchy = 'created_at'
    inlines = [ProjectAssignmentInline, ProjectAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'description', 'requirements', 'status', 'priority')
        }),
        ('Project Management', {
            'fields': ('project_manager', 'deadline', 'completion_percentage', 'started_at', 'completed_at')
        }),
        ('Financial Information', {
            'fields': ('budget', 'payment_details')
        }),
        ('Client Information', {
            'fields': ('client_name', 'client_email', 'client_phone', 'client_company')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('organization', 'project_manager', 'created_by')


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role', 'is_active', 'assigned_at', 'assigned_by']
    list_filter = ['role', 'is_active', 'assigned_at']
    search_fields = ['project__name', 'user__username', 'user__email']
    readonly_fields = ['assigned_at']
    date_hierarchy = 'assigned_at'


@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['name', 'project__name', 'description']
    readonly_fields = ['uploaded_at']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'completion_percentage', 'due_date', 'assigned_to', 'created_at']
    list_filter = ['status', 'created_at', 'due_date']
    search_fields = ['name', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'name', 'description', 'status')
        }),
        ('Details', {
            'fields': ('due_date', 'completed_date', 'completion_percentage', 'assigned_to')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['project', 'payment_type', 'amount', 'paid_amount', 'status', 'due_date', 'paid_date', 'created_at']
    list_filter = ['status', 'payment_type', 'due_date', 'created_at']
    search_fields = ['project__name', 'transaction_id', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'milestone', 'payment_type', 'amount', 'paid_amount')
        }),
        ('Payment Details', {
            'fields': ('due_date', 'paid_date', 'status', 'payment_method', 'transaction_id', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
