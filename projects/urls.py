from django.urls import path, include
from rest_framework.routers import DefaultRouter
from projects.views import ProjectViewSet
from projects.views.web import (
    list_projects, detail_project, create_project,
    update_project, delete_project,
    create_milestone, update_milestone, delete_milestone,
    create_payment, update_payment, delete_payment,
    api_documentation_index, api_documentation, create_api_page, update_api_page, delete_api_page,
    create_api_endpoint, update_api_endpoint, delete_api_endpoint
)

app_name = 'projects'

# Create router and register viewsets for API
router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project-api')

urlpatterns = [
    # Web routes (dashboard views) - these take precedence
    path('', list_projects, name='list'),
    path('create/', create_project, name='create'),
    path('<int:id>/', detail_project, name='detail'),
    path('<int:id>/edit/', update_project, name='update'),
    path('<int:id>/delete/', delete_project, name='delete'),
    
    # Milestone routes
    path('<int:project_id>/milestones/create/', create_milestone, name='milestone_create'),
    path('<int:project_id>/milestones/<int:milestone_id>/edit/', update_milestone, name='milestone_update'),
    path('<int:project_id>/milestones/<int:milestone_id>/delete/', delete_milestone, name='milestone_delete'),
    
    # Payment routes
    path('<int:project_id>/payments/create/', create_payment, name='payment_create'),
    path('<int:project_id>/payments/<int:payment_id>/edit/', update_payment, name='payment_update'),
    path('<int:project_id>/payments/<int:payment_id>/delete/', delete_payment, name='payment_delete'),
    
    # API Documentation routes
    path('api-docs/', api_documentation_index, name='api_documentation_index'),
    path('<int:project_id>/api-docs/', api_documentation, name='api_documentation'),
    path('<int:project_id>/api-docs/pages/create/', create_api_page, name='create_api_page'),
    path('<int:project_id>/api-docs/pages/<int:page_id>/edit/', update_api_page, name='update_api_page'),
    path('<int:project_id>/api-docs/pages/<int:page_id>/delete/', delete_api_page, name='delete_api_page'),
    path('<int:project_id>/api-docs/pages/<int:page_id>/endpoints/create/', create_api_endpoint, name='create_api_endpoint'),
    path('<int:project_id>/api-docs/endpoints/<int:endpoint_id>/edit/', update_api_endpoint, name='update_api_endpoint'),
    path('<int:project_id>/api-docs/endpoints/<int:endpoint_id>/delete/', delete_api_endpoint, name='delete_api_endpoint'),
    
    # API routes - accessible via /api/projects/api/
    path('api/', include(router.urls)),
]
