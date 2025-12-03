"""
URL Configuration for Node Registry API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NodeViewSet

app_name = 'nodes'

router = DefaultRouter()
router.register('', NodeViewSet, basename='node')

urlpatterns = [
    path('', include(router.urls)),
]
