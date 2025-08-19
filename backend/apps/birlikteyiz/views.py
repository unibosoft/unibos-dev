from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.management import call_command
from datetime import timedelta
import threading
from .models import (
    Earthquake, EarthquakeDataSource, CronJob,
    MeshNode, EmergencyMessage, DisasterZone, ResourcePoint
)


@login_required
def birlikteyiz_dashboard(request):
    """Main dashboard for Birlikteyiz module"""
    
    # Get recent earthquakes
    recent_earthquakes = Earthquake.objects.filter(
        occurred_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-occurred_at')[:50]
    
    # Get active disaster zones
    active_zones = DisasterZone.objects.filter(
        is_active=True
    ).order_by('-severity', '-declared_at')[:5]
    
    # Get mesh network stats
    total_nodes = MeshNode.objects.count()
    online_nodes = MeshNode.objects.filter(is_online=True).count()
    recent_messages = EmergencyMessage.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Get resource points
    resource_points = ResourcePoint.objects.filter(
        is_operational=True
    ).select_related()[:10]
    
    # Get data sources
    data_sources = EarthquakeDataSource.objects.all()
    
    # Count earthquakes for badge
    earthquake_count = Earthquake.objects.filter(
        occurred_at__gte=timezone.now() - timedelta(days=1),
        magnitude__gte=3.0
    ).count()
    
    context = {
        'recent_earthquakes': recent_earthquakes,
        'active_zones': active_zones,
        'total_nodes': total_nodes,
        'online_nodes': online_nodes,
        'recent_messages': recent_messages,
        'resource_points': resource_points,
        'data_sources': data_sources,
        'earthquake_count': earthquake_count,
    }
    
    return render(request, 'birlikteyiz/dashboard.html', context)


@login_required
def earthquake_list(request):
    """List all earthquakes with filtering"""
    
    earthquakes = Earthquake.objects.all()
    
    # Filtering
    magnitude_min = request.GET.get('magnitude_min')
    if magnitude_min:
        earthquakes = earthquakes.filter(magnitude__gte=magnitude_min)
    
    source = request.GET.get('source')
    if source:
        earthquakes = earthquakes.filter(source=source)
    
    city = request.GET.get('city')
    if city:
        earthquakes = earthquakes.filter(
            Q(city__icontains=city) | Q(location__icontains=city)
        )
    
    days = request.GET.get('days', 7)
    try:
        days = int(days)
    except:
        days = 7
    
    earthquakes = earthquakes.filter(
        occurred_at__gte=timezone.now() - timedelta(days=days)
    ).order_by('-occurred_at')
    
    # Pagination
    paginator = Paginator(earthquakes, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get data sources
    sources = EarthquakeDataSource.objects.all()
    
    context = {
        'page_obj': page_obj,
        'sources': sources,
        'filter_magnitude': magnitude_min,
        'filter_source': source,
        'filter_city': city,
        'filter_days': days,
    }
    
    return render(request, 'birlikteyiz/earthquake_list.html', context)


@login_required
def cron_jobs(request):
    """Display and manage cron jobs"""
    
    # Ensure earthquake fetch job exists
    fetch_job, _ = CronJob.objects.get_or_create(
        name='Fetch Earthquakes',
        defaults={
            'command': 'python manage.py fetch_earthquakes',
            'schedule': '*/5 * * * *',
            'is_active': True
        }
    )
    
    jobs = CronJob.objects.all().order_by('name')
    
    context = {
        'jobs': jobs,
    }
    
    return render(request, 'birlikteyiz/cron_jobs.html', context)


@login_required
@require_POST
def manual_fetch(request):
    """Manually trigger earthquake data fetch"""
    
    try:
        # Run the command in a background thread to not block the request
        def fetch_data():
            call_command('fetch_earthquakes')
        
        thread = threading.Thread(target=fetch_data)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({'success': True, 'message': 'veri çekme işlemi başlatıldı'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})