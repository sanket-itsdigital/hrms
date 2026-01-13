from django.urls import path
from django.shortcuts import render

app_name = 'projects'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Projects List',
        'message': 'Projects list feature is under development'
    })

def detail_view(request, id):
    return render(request, 'placeholder.html', {
        'page_title': f'Project #{id}',
        'message': f'Project detail view for project #{id} is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
    path('<int:id>/', detail_view, name='detail'),
]
