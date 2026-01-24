from django.urls import path
from reports.views.web import (
    reports_index, attendance_report, payroll_report,
    projects_report, leads_report
)

app_name = 'reports'

urlpatterns = [
    path('', reports_index, name='index'),
    path('attendance/', attendance_report, name='attendance'),
    path('payroll/', payroll_report, name='payroll'),
    path('projects/', projects_report, name='projects'),
    path('leads/', leads_report, name='leads'),
]
