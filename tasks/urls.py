from django.urls import path
from tasks.views.web import (
    list_tasks, my_tasks, detail_task, create_task,
    update_task, delete_task, kanban_board, task_reporting,
    update_task_status
)

app_name = 'tasks'

urlpatterns = [
    path('', list_tasks, name='list'),
    path('my-tasks/', my_tasks, name='my-tasks'),
    path('create/', create_task, name='create'),
    path('kanban/', kanban_board, name='kanban'),
    path('kanban/<int:project_id>/', kanban_board, name='kanban_project'),
    path('reporting/', task_reporting, name='reporting'),
    path('<int:id>/', detail_task, name='detail'),
    path('<int:id>/edit/', update_task, name='update'),
    path('<int:id>/delete/', delete_task, name='delete'),
    path('<int:id>/update-status/', update_task_status, name='update_status'),
]
