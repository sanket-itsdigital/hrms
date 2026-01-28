from django.urls import path
from attendance.views.web import (
    list_attendance, my_attendance, attendance_calendar_view,
    create_attendance, update_attendance, delete_attendance, bulk_attendance,
    attendance_report, export_attendance
)

app_name = 'attendance'

urlpatterns = [
    path('', list_attendance, name='list'),
    path('calendar/', attendance_calendar_view, name='calendar'),
    path('my-attendance/', my_attendance, name='my-attendance'),
    path('create/', create_attendance, name='create'),
    path('bulk/', bulk_attendance, name='bulk'),
    path('<int:id>/', update_attendance, name='update'),
    path('<int:id>/delete/', delete_attendance, name='delete'),
    path('report/', attendance_report, name='report'),
    path('export/', export_attendance, name='export'),
]
