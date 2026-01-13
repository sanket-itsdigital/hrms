from django.contrib import admin
from django.utils.html import format_html
from .models import Payroll, SalaryStructure


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['user', 'base_salary', 'effective_from', 'effective_to', 'is_active', 'created_at']
    list_filter = ['is_active', 'effective_from', 'organization']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'effective_from'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'user', 'base_salary')
        }),
        ('Allowances & Deductions', {
            'fields': ('allowances', 'deductions')
        }),
        ('Effective Period', {
            'fields': ('effective_from', 'effective_to', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'year', 'base_salary', 'gross_salary', 'net_salary', 'status', 'processed_by', 'created_at']
    list_filter = ['status', 'month', 'year', 'organization', 'created_at']
    search_fields = ['user__username', 'user__email', 'notes']
    readonly_fields = ['gross_salary', 'net_salary', 'created_at', 'updated_at', 'preview_payslip']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'user', 'month', 'year', 'status')
        }),
        ('Salary Calculation', {
            'fields': ('base_salary', 'bonuses', 'deductions', 'attendance_deduction', 'gross_salary', 'net_salary')
        }),
        ('Payslip', {
            'fields': ('payslip_generated', 'payslip_file', 'preview_payslip')
        }),
        ('Additional Information', {
            'fields': ('notes', 'processed_by', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_payslip(self, obj):
        if obj.payslip_file:
            return format_html('<a href="{}" target="_blank">View Payslip</a>', obj.payslip_file.url)
        return "No payslip generated"
    preview_payslip.short_description = 'Payslip'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'organization', 'processed_by')
