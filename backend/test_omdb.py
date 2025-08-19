#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from apps.movies.omdb_service import OMDBService

# Test the API
service = OMDBService()
result = service.search_movies('The Matrix')

print('API Test Result:')
if result.get('Response') == 'True':
    print(f'✅ Success! Found {result.get("totalResults", 0)} results')
    for movie in result.get('Search', [])[:3]:
        print(f"  - {movie['Title']} ({movie['Year']})")
else:
    print(f'❌ Error: {result.get("Error", "Unknown")}')
    
# Show usage stats
stats = service.get_usage_stats()
print(f'\nAPI Usage: {stats["used"]}/{stats["limit"]} ({stats["remaining"]} remaining)')

# Show cache stats
cache_stats = service.get_cache_stats()
print(f'\nCache Stats:')
print(f'  Total entries: {cache_stats["total_entries"]}')
print(f'  Search cached: {cache_stats["search_cached"]}')
print(f'  Detail cached: {cache_stats["detail_cached"]}')