# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from maps.views import health_check, get_geo_data, save_discovery, bulk_save_discoveries, get_player_data

def index_view(request):
    """Serve the main game interface"""
    return render(request, 'index.html')

urlpatterns = [
    path('', index_view, name='index'),
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    path('api/geo/', get_geo_data, name='get_geo_data'),
    path('api/discovery/', save_discovery, name='save_discovery'),
    path('api/discoveries/bulk/', bulk_save_discoveries, name='bulk_save_discoveries'),
    path('api/player/', get_player_data, name='get_player_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
