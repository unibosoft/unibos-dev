from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'birlikteyiz'

# REST API Router
router = DefaultRouter()
router.register(r'earthquakes', api_views.EarthquakeViewSet, basename='api-earthquake')
router.register(r'data-sources', api_views.DataSourceViewSet, basename='api-datasource')
router.register(r'disaster-zones', api_views.DisasterZoneViewSet, basename='api-zone')
router.register(r'mesh-nodes', api_views.MeshNodeViewSet, basename='api-node')

urlpatterns = [
    # Web UI
    path('', views.birlikteyiz_dashboard, name='dashboard'),
    path('earthquakes/', views.earthquake_list, name='earthquake_list'),
    path('map/', views.earthquake_map, name='earthquake_map'),
    path('cron-jobs/', views.cron_jobs, name='cron_jobs'),
    path('manual-fetch/', views.manual_fetch, name='manual_fetch'),

    # REST API
    path('api/', include(router.urls)),
]
