from django.urls import path
from django.shortcuts import render

app_name = 'tasks'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Tasks List',
        'message': 'Tasks list feature is under development'
    })

def my_tasks_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'My Tasks',
        'message': 'My tasks feature is under development'
    })

def detail_view(request, id):
    return render(request, 'placeholder.html', {
        'page_title': f'Task #{id}',
        'message': f'Task detail view for task #{id} is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
    path('my-tasks/', my_tasks_view, name='my-tasks'),
    path('<int:id>/', detail_view, name='detail'),
]
