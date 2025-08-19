"""
Solitaire URL Configuration
"""

from django.urls import path
from . import views

app_name = 'solitaire'

urlpatterns = [
    path('', views.solitaire_game, name='game'),
    path('api/<str:action>/', views.solitaire_api, name='api'),
    path('stats/', views.solitaire_stats, name='stats'),
]