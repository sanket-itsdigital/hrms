from django.urls import path
from django.shortcuts import render

app_name = 'reports'

# Placeholder views
def index_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Reports',
        'message': 'Reports feature is under development'
    })

urlpatterns = [
    path('', index_view, name='index'),
]
