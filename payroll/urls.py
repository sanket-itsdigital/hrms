from django.urls import path
from django.shortcuts import render

app_name = 'payroll'

# Placeholder views
def list_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Payroll List',
        'message': 'Payroll list feature is under development'
    })

urlpatterns = [
    path('', list_view, name='list'),
]
