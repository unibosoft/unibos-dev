from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('', views.administration_dashboard, name='dashboard'),
    path('users/', views.users_list, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('roles/', views.roles_list, name='roles'),
    path('roles/<int:role_id>/', views.role_detail, name='role_detail'),
    path('departments/', views.departments_list, name='departments'),
    path('requests/', views.permission_requests, name='permission_requests'),
    path('logs/', views.audit_logs, name='audit_logs'),
    path('settings/', views.system_settings, name='system_settings'),
    path('screen-lock/', views.screen_lock_settings, name='screen_lock_settings'),
    path('unlock/', views.unlock_screen, name='unlock_screen'),
    path('lock/', views.lock_screen, name='lock_screen'),
    
    # Solitaire management
    path('solitaire/', views.solitaire_dashboard, name='solitaire_dashboard'),
    path('solitaire/players/', views.solitaire_players, name='solitaire_players'),
    path('solitaire/sessions/', views.solitaire_sessions, name='solitaire_sessions'),
    
    # Cron job management
    path('cron-jobs/', views.cron_jobs_admin, name='cron_jobs'),
]