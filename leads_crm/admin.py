from django.contrib import admin
from django.utils.html import format_html
from .models import Lead, Proposal, MeetingLog


class ProposalInline(admin.TabularInline):
    model = Proposal
    extra = 0
    fields = ['title', 'amount', 'status', 'sent_at']


class MeetingLogInline(admin.TabularInline):
    model = MeetingLog
    extra = 0
    fields = ['meeting_type', 'date', 'time', 'duration', 'notes', 'logged_by']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'stage', 'expected_revenue', 'probability', 'assigned_to', 'created_at']
    list_filter = ['stage', 'assigned_to', 'organization', 'created_at']
    search_fields = ['name', 'company_name', 'email', 'phone', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [ProposalInline, MeetingLogInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'company_name', 'email', 'phone')
        }),
        ('Lead Details', {
            'fields': ('stage', 'expected_revenue', 'probability', 'notes')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by', 'converted_to_project')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('assigned_to', 'created_by', 'organization', 'converted_to_project')


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'lead', 'amount', 'status', 'sent_at', 'sent_by', 'created_at']
    list_filter = ['status', 'sent_at', 'created_at']
    search_fields = ['title', 'lead__name', 'lead__company_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'preview_file']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lead', 'title', 'description', 'amount', 'status')
        }),
        ('Proposal File', {
            'fields': ('proposal_file', 'preview_file', 'sent_at', 'sent_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_file(self, obj):
        if obj.proposal_file:
            return format_html('<a href="{}" target="_blank">View Proposal</a>', obj.proposal_file.url)
        return "No file"
    preview_file.short_description = 'Proposal File'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('lead', 'sent_by')


@admin.register(MeetingLog)
class MeetingLogAdmin(admin.ModelAdmin):
    list_display = ['lead', 'meeting_type', 'date', 'time', 'duration', 'logged_by', 'created_at']
    list_filter = ['meeting_type', 'date', 'created_at']
    search_fields = ['lead__name', 'lead__company_name', 'notes', 'logged_by__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lead', 'meeting_type', 'date', 'time', 'duration')
        }),
        ('Meeting Details', {
            'fields': ('notes', 'logged_by')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('lead', 'logged_by')
