from django.urls import path
from django.shortcuts import render

app_name = 'daily_updates'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Daily Updates',
        'message': 'Daily updates list feature is under development'
    })

def create_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Submit Daily Update',
        'message': 'Daily update submission feature is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
    path('create/', create_view, name='create'),
]
