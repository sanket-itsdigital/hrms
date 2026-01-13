from django.urls import path
from django.shortcuts import render

app_name = 'leads_crm'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Leads List',
        'message': 'Leads list feature is under development'
    })

def create_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Add New Lead',
        'message': 'Add new lead feature is under development'
    })

def proposals_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Proposals',
        'message': 'Proposals feature is under development'
    })

def meetings_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Meeting Logs',
        'message': 'Meeting logs feature is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
    path('create/', create_view, name='create'),
    path('proposals/', proposals_view, name='proposals'),
    path('meetings/', meetings_view, name='meetings'),
]
