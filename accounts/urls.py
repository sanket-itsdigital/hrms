from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views.dashboard import (
    dashboard, ceo_dashboard, hr_dashboard, pm_dashboard,
    developer_dashboard, uiux_dashboard, bde_dashboard
)
from .views.auth import logout_view

# Placeholder views
def users_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Users Management',
        'message': 'Users management feature is under development'
    })

def profile_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'User Profile',
        'message': 'User profile feature is under development'
    })

def settings_view(request):
    return render(request, 'placeholder.html', {
        'page_title': 'Settings',
        'message': 'Settings feature is under development'
    })

app_name = 'accounts'

urlpatterns = [
    # Dashboard
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard_redirect'),
    path('dashboard/ceo/', ceo_dashboard, name='ceo'),
    path('dashboard/hr/', hr_dashboard, name='hr'),
    path('dashboard/pm/', pm_dashboard, name='pm'),
    path('dashboard/developer/', developer_dashboard, name='developer'),
    path('dashboard/uiux/', uiux_dashboard, name='uiux'),
    path('dashboard/bde/', bde_dashboard, name='bde'),
    
    # JWT Authentication (API)
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Management
    path('users/', users_view, name='users'),
    path('profile/', profile_view, name='profile'),
    path('settings/', settings_view, name='settings'),
    
    # Django Auth Views
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
