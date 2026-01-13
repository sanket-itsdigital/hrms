from django.urls import path
from django.shortcuts import render

app_name = 'notifications'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Notifications',
        'message': 'Notifications list feature is under development'
    })

def detail_view(request, id):
    return render(request, 'placeholder.html', {
        'page_title': f'Notification #{id}',
        'message': f'Notification detail view for notification #{id} is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
    path('<int:id>/', detail_view, name='detail'),
]
