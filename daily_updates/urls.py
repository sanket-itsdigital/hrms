from django.urls import path, include
from rest_framework.routers import DefaultRouter
from daily_updates.views import DailyUpdateViewSet
from daily_updates.views.web import (
    list_daily_updates, create_daily_update,
    update_daily_update, delete_daily_update
)

app_name = 'daily_updates'

# Create router and register viewsets for API
router = DefaultRouter()
router.register(r'', DailyUpdateViewSet, basename='daily-update-api')

urlpatterns = [
    # Web routes (dashboard views) - accessible via /api/daily-updates/web/
    # IMPORTANT: These MUST come BEFORE the API router to be matched first
    path('web/', list_daily_updates, name='list'),
    path('web/create/', create_daily_update, name='create'),
    path('web/<int:id>/edit/', update_daily_update, name='update'),
    path('web/<int:id>/delete/', delete_daily_update, name='delete'),
    
    # API routes - accessible directly at /api/daily-updates/
    # The router creates: GET /, POST /, GET /{id}/, PUT /{id}/, DELETE /{id}/
    # The 'web' path above will be matched first, so it won't conflict
    path('', include(router.urls)),
]
