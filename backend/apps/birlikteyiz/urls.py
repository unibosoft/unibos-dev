from django.urls import path
from . import views

app_name = 'birlikteyiz'

urlpatterns = [
    path('', views.birlikteyiz_dashboard, name='dashboard'),
    path('earthquakes/', views.earthquake_list, name='earthquake_list'),
    path('cron-jobs/', views.cron_jobs, name='cron_jobs'),
    path('manual-fetch/', views.manual_fetch, name='manual_fetch'),
]
