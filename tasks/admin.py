from django.contrib import admin
from django.utils.html import format_html
from .models import Task, TaskComment, TaskActivity


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['user', 'comment', 'created_at']


class TaskActivityInline(admin.TabularInline):
    model = TaskActivity
    extra = 0
    readonly_fields = ['created_at']
    fields = ['user', 'action', 'description', 'old_value', 'new_value', 'created_at']
    can_delete = False


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assigned_to', 'deadline', 'is_overdue', 'created_at']
    list_filter = ['status', 'priority', 'is_overdue', 'project', 'created_at', 'deadline']
    search_fields = ['title', 'description', 'project__name', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue', 'completed_at']
    date_hierarchy = 'created_at'
    inlines = [TaskCommentInline, TaskActivityInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'description', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by', 'deadline')
        }),
        ('Status', {
            'fields': ('is_overdue', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('project', 'assigned_to', 'created_by')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'comment_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'action', 'description', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    can_delete = False  # Audit logs should not be deleted
