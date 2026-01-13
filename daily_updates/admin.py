from django.contrib import admin
from .models import DailyUpdate, DailyUpdateAttachment


class DailyUpdateAttachmentInline(admin.TabularInline):
    model = DailyUpdateAttachment
    extra = 0
    fields = ['file', 'file_type', 'thumbnail']


@admin.register(DailyUpdate)
class DailyUpdateAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'date', 'hours_worked', 'has_figma_link', 'created_at']
    list_filter = ['date', 'organization', 'created_at']
    search_fields = ['user__username', 'project__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    inlines = [DailyUpdateAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'project', 'user', 'date')
        }),
        ('Update Details', {
            'fields': ('description', 'figma_link', 'hours_worked')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_figma_link(self, obj):
        return 'Yes' if obj.figma_link else 'No'
    has_figma_link.boolean = True
    has_figma_link.short_description = 'Figma Link'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'project', 'organization')


@admin.register(DailyUpdateAttachment)
class DailyUpdateAttachmentAdmin(admin.ModelAdmin):
    list_display = ['daily_update', 'file', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['daily_update__user__username', 'file']
    readonly_fields = ['uploaded_at']
