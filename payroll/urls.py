from django.urls import path
from payroll.views.web import (
    list_payroll, create_payroll, update_payroll, process_payroll, mark_paid, change_status, generate_payroll,
    my_payroll, payroll_detail,
)

app_name = 'payroll'

urlpatterns = [
    path('', list_payroll, name='list'),
    path('my-payroll/', my_payroll, name='my-payroll'),
    path('generate/', generate_payroll, name='generate'),
    path('create/', create_payroll, name='create'),
    path('<int:id>/', payroll_detail, name='detail'),
    path('<int:id>/edit/', update_payroll, name='update'),
    path('<int:id>/change-status/', change_status, name='change-status'),
    path('<int:id>/process/', process_payroll, name='process'),
    path('<int:id>/mark-paid/', mark_paid, name='mark-paid'),
]
