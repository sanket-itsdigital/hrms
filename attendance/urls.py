from django.urls import path
from django.shortcuts import render

app_name = 'attendance'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Attendance List',
        'message': 'Attendance list feature is under development'
    })

def my_attendance_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'My Attendance',
        'message': 'My attendance feature is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
    path('my-attendance/', my_attendance_view, name='my-attendance'),
]
