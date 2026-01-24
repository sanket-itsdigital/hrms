from django.urls import path
from payroll.views.web import (
    list_payroll, create_payroll, update_payroll, process_payroll, mark_paid, change_status
)

app_name = 'payroll'

urlpatterns = [
    path('', list_payroll, name='list'),
    path('create/', create_payroll, name='create'),
    path('<int:id>/edit/', update_payroll, name='update'),
    path('<int:id>/change-status/', change_status, name='change-status'),
    path('<int:id>/process/', process_payroll, name='process'),
    path('<int:id>/mark-paid/', mark_paid, name='mark-paid'),
]
