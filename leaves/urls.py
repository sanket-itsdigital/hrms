from django.urls import path
from leaves.views.web import (
    list_leaves, my_leaves, create_leave,
    approve_leave, reject_leave
)

app_name = 'leaves'

urlpatterns = [
    path('', list_leaves, name='list'),
    path('my-leaves/', my_leaves, name='my-leaves'),
    path('create/', create_leave, name='create'),
    path('<int:id>/approve/', approve_leave, name='approve'),
    path('<int:id>/reject/', reject_leave, name='reject'),
]
