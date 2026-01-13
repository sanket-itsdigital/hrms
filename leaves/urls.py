from django.urls import path
from django.shortcuts import render

app_name = 'leaves'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Leaves List',
        'message': 'Leaves list feature is under development'
    })

def my_leaves_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'My Leaves',
        'message': 'My leaves feature is under development'
    })

def create_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Apply for Leave',
        'message': 'Leave application feature is under development'
    })

def approve_view(request, id):
    return render(request, 'placeholder.html', {
        'page_title': f'Approve Leave #{id}',
        'message': f'Leave approval feature for leave #{id} is under development'
    })

def reject_view(request, id):
    return render(request, 'placeholder.html', {
        'page_title': f'Reject Leave #{id}',
        'message': f'Leave rejection feature for leave #{id} is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
    path('my-leaves/', my_leaves_view, name='my-leaves'),
    path('create/', create_view, name='create'),
    path('<int:id>/approve/', approve_view, name='approve'),
    path('<int:id>/reject/', reject_view, name='reject'),
]
