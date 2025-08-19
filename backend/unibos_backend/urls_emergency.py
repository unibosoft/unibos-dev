"""
Emergency URL Configuration for UNIBOS Backend
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface (disabled in emergency mode)
    # path('admin/', admin.site.urls),
    
    # CCTV Module (with namespace for web interface)
    path('cctv/', include('apps.cctv.urls', namespace='cctv')),
    
    # Documents Module (with namespace for consistency)
    path('documents/', include('apps.documents.urls', namespace='documents')),
    
    # Version Manager Module
    path('version-manager/', include('apps.version_manager.urls', namespace='version_manager')),
    
    # Administration Module
    path('administration/', include('apps.administration.urls', namespace='administration')),
    
    # Movies Module - Movie/Series Collection Management
    path('movies/', include('apps.movies.urls', namespace='movies')),
    
    # Music Module - Music Collection with Spotify Integration
    path('music/', include('apps.music.urls', namespace='music')),
    
    # RestoPOS Module - Restaurant POS System
    path('restopos/', include('apps.restopos.urls', namespace='restopos')),
    
    # Solitaire Game Module
    path('solitaire/', include('apps.solitaire.urls', namespace='solitaire')),
    
    # Birlikteyiz Module - Emergency Response and Earthquake Tracking
    path('birlikteyiz/', include('apps.birlikteyiz.urls', namespace='birlikteyiz')),
    
    # Store Module - E-commerce Marketplace Integration
    path('store/', include('store.urls', namespace='store')),
    
    # Web UI
    path('', include('apps.web_ui.urls')),
]

# Serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar (if installed and in INSTALLED_APPS)
    try:
        # Check if debug_toolbar is in INSTALLED_APPS before trying to use it
        from django.conf import settings
        if 'debug_toolbar' in settings.INSTALLED_APPS:
            import debug_toolbar
            urlpatterns = [
                path('__debug__/', include(debug_toolbar.urls)),
            ] + urlpatterns
    except ImportError:
        pass