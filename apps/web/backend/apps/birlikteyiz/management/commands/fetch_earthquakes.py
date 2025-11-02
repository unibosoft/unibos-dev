"""
Fetch earthquake data from multiple sources
Run every 5 minutes via cron job
"""

import requests
import re
import json
from datetime import datetime, timedelta
from decimal import Decimal
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.birlikteyiz.models import Earthquake, EarthquakeDataSource, CronJob


class Command(BaseCommand):
    help = 'Fetch earthquake data from all configured sources'
    
    def __init__(self):
        super().__init__()
        self.sources = {
            'KANDILLI': {
                'url': 'http://www.koeri.boun.edu.tr/scripts/lst5.asp',
                'parser': self.parse_kandilli
            },
            'AFAD': {
                'url': 'https://servisnet.afad.gov.tr/apigateway/deprem/apiv2/event/filter',
                'parser': self.parse_afad
            },
            'IRIS': {  # Incorporated Research Institutions for Seismology - Global data
                'url': 'http://service.iris.edu/fdsnws/event/1/query',
                'parser': self.parse_iris
            },
            'USGS': {
                'url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson',
                'parser': self.parse_usgs
            },
            'GFZ': {  # German Research Centre for Geosciences - European data
                'url': 'http://geofon.gfz-potsdam.de/eqinfo/list.php',
                'parser': self.parse_gfz
            }
        }
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Starting earthquake data fetch at {timezone.now()}'))
        
        # Update cron job status
        cron_job, _ = CronJob.objects.get_or_create(
            name='Fetch Earthquakes',
            defaults={
                'command': 'fetch_earthquakes',
                'schedule': '*/5 * * * *'  # Every 5 minutes
            }
        )
        cron_job.status = 'running'
        cron_job.last_run = timezone.now()
        cron_job.save()
        
        total_new = 0
        total_updated = 0
        errors = []
        
        for source_name, config in self.sources.items():
            try:
                # Get or create data source
                data_source, _ = EarthquakeDataSource.objects.get_or_create(
                    name=source_name,
                    defaults={'url': config['url']}
                )
                
                if not data_source.is_active:
                    self.stdout.write(f'Skipping inactive source: {source_name}')
                    continue
                
                self.stdout.write(f'Fetching from {source_name}...')
                
                # Fetch and parse data
                new_count, updated_count = config['parser'](config['url'], data_source)
                
                # Update source stats
                data_source.last_fetch = timezone.now()
                data_source.last_success = timezone.now()
                data_source.fetch_count += 1
                data_source.save()
                
                total_new += new_count
                total_updated += updated_count
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{source_name}: {new_count} new, {updated_count} updated'
                    )
                )
                
            except Exception as e:
                error_msg = f'{source_name}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
                
                # Update source error info
                if 'data_source' in locals():
                    data_source.last_error = str(e)
                    data_source.error_count += 1
                    data_source.save()
        
        # Update cron job result
        cron_job.status = 'failed' if errors else 'success'
        cron_job.run_count += 1
        if not errors:
            cron_job.success_count += 1
        else:
            cron_job.error_count += 1
        
        result_msg = f'Fetched {total_new} new, {total_updated} updated earthquakes'
        if errors:
            result_msg += f'\\nErrors: {"; ".join(errors)}'
        
        cron_job.last_result = result_msg
        cron_job.next_run = timezone.now() + timedelta(minutes=5)
        cron_job.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Completed: {result_msg}')
        )
    
    def parse_kandilli(self, url, data_source):
        """Parse Kandilli Rasathanesi data"""
        new_count = 0
        updated_count = 0
        
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'windows-1254'  # Turkish encoding
            
            # Parse HTML to find the pre-formatted text section
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_element = soup.find('pre')
            
            if not pre_element:
                self.stdout.write('Kandilli: Could not find PRE element in HTML')
                return 0, 0
            
            lines = pre_element.text.split('\n')
        
            # Skip header lines and find data
            data_started = False
            for line in lines:
                # Look for the separator line to know when data starts
                if '------' in line and not data_started:
                    data_started = True
                    continue
                
                if not data_started or not line.strip():
                    continue
                
                try:
                    # Parse fixed-width format or space-separated
                    parts = line.split()
                    if len(parts) < 7:
                        continue
                    
                    # Expected format: Date Time Lat Lon Depth MD ML MW Location...
                    date_str = parts[0]
                    time_str = parts[1]
                    lat = parts[2]
                    lon = parts[3]
                    depth = parts[4]
                    
                    # Find magnitude columns (MD, ML, MW)
                    magnitude = None
                    location_start = 8  # Default position after MW column
                    
                    # Try to parse MD (position 5)
                    if len(parts) > 5 and parts[5] != '-.-':
                        try:
                            magnitude = float(parts[5])
                        except ValueError:
                            pass
                    
                    # Try ML if MD not found (position 6)
                    if not magnitude and len(parts) > 6 and parts[6] != '-.-':
                        try:
                            magnitude = float(parts[6])
                        except ValueError:
                            pass
                    
                    # Try MW if neither MD nor ML found (position 7)
                    if not magnitude and len(parts) > 7 and parts[7] != '-.-':
                        try:
                            magnitude = float(parts[7])
                        except ValueError:
                            pass
                    
                    if not magnitude:
                        continue
                    
                    # Rest is location
                    location = ' '.join(parts[location_start:]) if location_start < len(parts) else 'Unknown'
                
                    # Validate basic fields
                    if not all([date_str, time_str, lat, lon, depth]):
                        continue
                
                    # Parse datetime
                    dt_str = f"{date_str} {time_str}"
                    occurred_at = datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S")
                    # Kandilli uses Turkey time (UTC+3)
                    import pytz
                    turkey_tz = pytz.timezone('Europe/Istanbul')
                    occurred_at = turkey_tz.localize(occurred_at)
                
                    # Create unique ID
                    unique_id = f"KANDILLI_{date_str}_{time_str}_{lat}_{lon}"
                
                    # Save earthquake
                    earthquake, created = Earthquake.objects.update_or_create(
                        unique_id=unique_id,
                        defaults={
                            'source': 'KANDILLI',
                            'magnitude': Decimal(str(magnitude)),
                            'depth': Decimal(depth),
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lon),
                            'location': location.replace('�lk sel', 'İlksel'),  # Fix encoding
                            'occurred_at': occurred_at,
                            'raw_data': {'original_line': line}
                        }
                    )
                
                    if created:
                        new_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    # Skip line if parsing fails
                    continue
                    
        except Exception as e:
            self.stdout.write(f'Error fetching Kandilli data: {e}')
        
        return new_count, updated_count
    
    def parse_afad(self, url, data_source):
        """Parse AFAD data"""
        new_count = 0
        updated_count = 0
        
        # Use the new AFAD API endpoint
        params = {
            'start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d'),
            'minmag': 2.0
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        for event in data:
            try:
                unique_id = f"AFAD_{event['eventID']}"
                
                earthquake, created = Earthquake.objects.update_or_create(
                    unique_id=unique_id,
                    defaults={
                        'source': 'AFAD',
                        'source_id': event['eventID'],
                        'magnitude': Decimal(str(event['magnitude'])),
                        'depth': Decimal(str(event['depth'])),
                        'latitude': Decimal(str(event['latitude'])),
                        'longitude': Decimal(str(event['longitude'])),
                        'location': event['location'],
                        'city': event.get('province'),
                        'district': event.get('district'),
                        'occurred_at': timezone.make_aware(datetime.fromisoformat(event['date'].replace('Z', '+00:00').replace('+00:00', ''))),
                        'raw_data': event
                    }
                )
                
                if created:
                    new_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(f'Error parsing AFAD event: {e}')
                continue
        
        return new_count, updated_count
    
    def parse_iris(self, url, data_source):
        """Parse IRIS (Incorporated Research Institutions for Seismology) data"""
        new_count = 0
        updated_count = 0
        
        try:
            # IRIS FDSNWS parameters for Turkey region
            params = {
                'format': 'text',
                'minmag': 3.0,
                'minlat': 35.0,
                'maxlat': 43.0,
                'minlon': 25.0,
                'maxlon': 45.0,
                'starttime': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'endtime': datetime.now().strftime('%Y-%m-%d'),
                'orderby': 'time-desc'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            # Parse text format (pipe-separated values)
            lines = response.text.strip().split('\n')
            
            # Skip header line
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                try:
                    # Parse pipe-separated values
                    parts = line.split('|')
                    if len(parts) < 13:
                        continue
                    
                    event_id = parts[0]
                    time_str = parts[1]
                    lat = parts[2]
                    lon = parts[3]
                    depth = parts[4]
                    magnitude = parts[10]
                    location = parts[12] if len(parts) > 12 else 'Unknown'
                    
                    # Parse datetime
                    occurred_at = datetime.fromisoformat(time_str.replace('T', ' ').replace('Z', '+00:00'))
                    
                    # Create unique ID
                    unique_id = f"IRIS_{event_id}"
                    
                    earthquake, created = Earthquake.objects.update_or_create(
                        unique_id=unique_id,
                        defaults={
                            'source': 'IRIS',
                            'source_id': event_id,
                            'magnitude': Decimal(magnitude),
                            'depth': Decimal(depth),
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lon),
                            'location': location.strip(),
                            'occurred_at': timezone.make_aware(occurred_at.replace(tzinfo=None)),
                            'raw_data': {'original_line': line}
                        }
                    )
                    
                    if created:
                        new_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.stdout.write(f'Error fetching IRIS data: {e}')
        
        return new_count, updated_count
    
    def parse_usgs(self, url, data_source):
        """Parse USGS GeoJSON data"""
        new_count = 0
        updated_count = 0
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Filter for Turkey and nearby regions
        turkey_bounds = {
            'min_lat': 35.0,
            'max_lat': 43.0,
            'min_lon': 25.0,
            'max_lon': 45.0
        }
        
        for feature in data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            lon, lat, depth = coords
            
            # Check if in Turkey region
            if not (turkey_bounds['min_lat'] <= lat <= turkey_bounds['max_lat'] and
                    turkey_bounds['min_lon'] <= lon <= turkey_bounds['max_lon']):
                continue
            
            try:
                unique_id = f"USGS_{feature['id']}"
                import pytz
                occurred_at = datetime.fromtimestamp(props['time'] / 1000, tz=pytz.UTC)
                
                earthquake, created = Earthquake.objects.update_or_create(
                    unique_id=unique_id,
                    defaults={
                        'source': 'USGS',
                        'source_id': feature['id'],
                        'magnitude': Decimal(str(props['mag'])),
                        'depth': Decimal(str(depth)),
                        'latitude': Decimal(str(lat)),
                        'longitude': Decimal(str(lon)),
                        'location': props['place'],
                        'occurred_at': occurred_at,
                        'intensity': props.get('mmi'),
                        'felt_reports': props.get('felt') or 0,  # Handle None values
                        'raw_data': feature
                    }
                )
                
                if created:
                    new_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(f'Error parsing USGS event: {e}')
                continue
        
        return new_count, updated_count
    
    def parse_gfz(self, url, data_source):
        """Parse GFZ (German Research Centre for Geosciences) data"""
        new_count = 0
        updated_count = 0
        
        try:
            # GFZ provides data via their FDSNWS service
            api_url = 'https://geofon.gfz-potsdam.de/fdsnws/event/1/query'
            params = {
                'format': 'text',
                'minmag': 3.0,
                'minlat': 35.0,
                'maxlat': 43.0,
                'minlon': 25.0,
                'maxlon': 45.0,
                'starttime': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'endtime': datetime.now().strftime('%Y-%m-%d'),
                'orderby': 'time'
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            # Parse text format
            lines = response.text.strip().split('\n')
            
            # Skip header if present
            for line in lines:
                if not line.strip() or line.startswith('#'):
                    continue
                
                try:
                    # Parse pipe-separated values
                    parts = line.split('|')
                    if len(parts) < 13:
                        continue
                    
                    event_id = parts[0]
                    time_str = parts[1]
                    lat = parts[2]
                    lon = parts[3]
                    depth = parts[4]
                    magnitude = parts[10]
                    location = parts[12] if len(parts) > 12 else 'Unknown'
                    
                    # Parse datetime
                    occurred_at = datetime.fromisoformat(time_str.replace('T', ' ').replace('Z', ''))
                    
                    # Create unique ID
                    unique_id = f"GFZ_{event_id}"
                    
                    earthquake, created = Earthquake.objects.update_or_create(
                        unique_id=unique_id,
                        defaults={
                            'source': 'GFZ',
                            'source_id': event_id,
                            'magnitude': Decimal(magnitude),
                            'depth': Decimal(depth),
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lon),
                            'location': location.strip(),
                            'occurred_at': timezone.make_aware(occurred_at),
                            'raw_data': {'original_line': line}
                        }
                    )
                    
                    if created:
                        new_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.stdout.write(f'Error fetching GFZ data: {e}')
        
        return new_count, updated_count