"""
OpenStreetMap Service for UNIBOS
Provides business search, geocoding, and location enrichment
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class OSMService:
    """OpenStreetMap/Nominatim service for location and business data"""
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    USER_AGENT = "UNIBOS/1.0 (https://unibos.com)"
    CACHE_TTL = 86400  # 24 hours
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT
        })
    
    def search_business(self, name: str, location_hint: str = '', country: str = 'tr') -> Optional[Dict]:
        """
        Search for a business on OpenStreetMap
        
        Args:
            name: Business name to search
            location_hint: Additional location info (city, district, etc)
            country: Country code (default: 'tr' for Turkey)
            
        Returns:
            Dictionary with business information or None
        """
        # Check cache first
        cache_key = f"osm_business_{name}_{location_hint}_{country}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"🎯 OSM cache hit for: {name}")
            return cached
        
        try:
            # Build search query
            query = f"{name}"
            if location_hint:
                query = f"{name} {location_hint}"
            
            logger.info(f"🗺️ OSM search: {query} (country: {country})")
            
            # Search parameters
            params = {
                'q': query,
                'format': 'json',
                'limit': 10,
                'addressdetails': 1,
                'extratags': 1,
                'namedetails': 1,
                'countrycodes': country
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Find best match
                best_match = self._find_best_business_match(results, name)
                if best_match:
                    # Enrich with details
                    enriched = self._enrich_with_details(best_match)
                    
                    # Cache the result
                    cache.set(cache_key, enriched, self.CACHE_TTL)
                    
                    logger.info(f"✅ OSM found: {enriched.get('display_name', '')}")
                    return enriched
                else:
                    logger.info(f"⚠️ No exact match for: {name}")
            
        except requests.RequestException as e:
            logger.error(f"OSM request error: {e}")
        except Exception as e:
            logger.error(f"OSM search error: {e}")
        
        return None
    
    def _find_best_business_match(self, results: List[Dict], name: str) -> Optional[Dict]:
        """Find the best matching business from search results"""
        if not results:
            return None
        
        name_lower = name.lower()
        business_types = {
            'shop', 'supermarket', 'store', 'restaurant', 'cafe', 
            'pharmacy', 'bank', 'hotel', 'mall', 'market'
        }
        
        # Score each result
        scored_results = []
        for result in results:
            score = 0
            
            # Check type/class
            osm_type = result.get('type', '').lower()
            osm_class = result.get('class', '').lower()
            
            if any(bt in osm_type for bt in business_types):
                score += 10
            if any(bt in osm_class for bt in business_types):
                score += 10
            
            # Check name similarity
            display_name = result.get('display_name', '').lower()
            if name_lower in display_name:
                score += 5
            
            # Check if it has business-related tags
            extratags = result.get('extratags', {})
            if 'phone' in extratags or 'opening_hours' in extratags:
                score += 5
            if 'brand' in extratags or 'website' in extratags:
                score += 3
            
            if score > 0:
                scored_results.append((score, result))
        
        # Return highest scoring result
        if scored_results:
            scored_results.sort(key=lambda x: x[0], reverse=True)
            return scored_results[0][1]
        
        return None
    
    def _enrich_with_details(self, result: Dict) -> Dict:
        """Enrich a search result with additional details"""
        enriched = {
            'osm_id': result.get('osm_id'),
            'osm_type': result.get('osm_type'),
            'display_name': result.get('display_name', ''),
            'lat': float(result.get('lat', 0)),
            'lon': float(result.get('lon', 0)),
            'type': result.get('type'),
            'class': result.get('class'),
            'importance': result.get('importance', 0)
        }
        
        # Extract address components
        if 'address' in result:
            addr = result['address']
            enriched['address'] = {
                'road': addr.get('road', ''),
                'neighbourhood': addr.get('neighbourhood', ''),
                'suburb': addr.get('suburb', ''),
                'district': addr.get('state_district', ''),
                'city': addr.get('city', addr.get('town', '')),
                'state': addr.get('state', ''),
                'postcode': addr.get('postcode', ''),
                'country': addr.get('country', '')
            }
            
            # Build formatted address
            addr_parts = []
            for key in ['road', 'neighbourhood', 'district', 'city']:
                if enriched['address'].get(key):
                    addr_parts.append(enriched['address'][key])
            enriched['formatted_address'] = ', '.join(addr_parts)
        
        # Extract business info from extratags
        extratags = result.get('extratags', {})
        if extratags:
            # Phone numbers
            for phone_key in ['phone', 'contact:phone', 'contact:mobile']:
                if phone_key in extratags:
                    enriched['phone'] = extratags[phone_key]
                    break
            
            # Website
            for web_key in ['website', 'contact:website', 'url']:
                if web_key in extratags:
                    enriched['website'] = extratags[web_key]
                    break
            
            # Opening hours
            if 'opening_hours' in extratags:
                enriched['opening_hours'] = extratags['opening_hours']
            
            # Brand/chain info
            if 'brand' in extratags:
                enriched['brand'] = extratags['brand']
            if 'brand:wikidata' in extratags:
                enriched['brand_wikidata'] = extratags['brand:wikidata']
            
            # Payment methods
            payment_methods = []
            for key, value in extratags.items():
                if key.startswith('payment:') and value == 'yes':
                    payment_methods.append(key.replace('payment:', ''))
            if payment_methods:
                enriched['payment_methods'] = payment_methods
        
        # Try to get more details if we have OSM ID
        if enriched.get('osm_id') and enriched.get('osm_type'):
            additional = self._get_place_details(
                enriched['osm_type'], 
                enriched['osm_id']
            )
            if additional:
                enriched.update(additional)
        
        return enriched
    
    def _get_place_details(self, osm_type: str, osm_id: int) -> Optional[Dict]:
        """Get detailed information about a specific place"""
        try:
            params = {
                'osmtype': osm_type[0].upper(),  # N, W, or R
                'osmid': osm_id,
                'format': 'json',
                'addressdetails': 1,
                'extratags': 1
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/details",
                params=params,
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                details = {}
                
                # Extract additional tags
                if 'extratags' in data:
                    tags = data['extratags']
                    
                    # Social media
                    for social in ['facebook', 'instagram', 'twitter']:
                        key = f'contact:{social}'
                        if key in tags:
                            if 'social_media' not in details:
                                details['social_media'] = {}
                            details['social_media'][social] = tags[key]
                    
                    # Email
                    if 'contact:email' in tags:
                        details['email'] = tags['contact:email']
                    
                    # Wheelchair access
                    if 'wheelchair' in tags:
                        details['wheelchair_access'] = tags['wheelchair']
                    
                    # Cuisine (for restaurants)
                    if 'cuisine' in tags:
                        details['cuisine'] = tags['cuisine']
                
                return details
                
        except Exception as e:
            logger.warning(f"OSM details fetch error: {e}")
        
        return None
    
    def geocode(self, address: str, country: str = 'tr') -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates
        
        Args:
            address: Address string to geocode
            country: Country code
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        cache_key = f"osm_geocode_{address}_{country}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': country
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    lat = float(results[0]['lat'])
                    lon = float(results[0]['lon'])
                    coords = (lat, lon)
                    cache.set(cache_key, coords, self.CACHE_TTL)
                    return coords
                    
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
        
        return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Convert coordinates to address
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Address dictionary or None
        """
        cache_key = f"osm_reverse_{lat}_{lon}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/reverse",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, self.CACHE_TTL)
                return data
                
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
        
        return None
    
    def find_nearby(self, lat: float, lon: float, amenity: str, radius: int = 1000) -> List[Dict]:
        """
        Find nearby amenities/businesses
        
        Args:
            lat: Latitude
            lon: Longitude
            amenity: Type of amenity (restaurant, pharmacy, atm, etc)
            radius: Search radius in meters
            
        Returns:
            List of nearby places
        """
        # This would typically use Overpass API for better results
        # For now, using Nominatim search with location bias
        try:
            params = {
                'q': amenity,
                'format': 'json',
                'limit': 20,
                'bounded': 1,
                'viewbox': f"{lon-0.01},{lat+0.01},{lon+0.01},{lat-0.01}",
                'extratags': 1
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Calculate distances and sort
                nearby = []
                for result in results:
                    place_lat = float(result.get('lat', 0))
                    place_lon = float(result.get('lon', 0))
                    
                    # Simple distance calculation (not perfect but good enough)
                    distance = ((place_lat - lat) ** 2 + (place_lon - lon) ** 2) ** 0.5
                    distance_meters = distance * 111000  # Rough conversion
                    
                    if distance_meters <= radius:
                        result['distance'] = int(distance_meters)
                        nearby.append(result)
                
                nearby.sort(key=lambda x: x['distance'])
                return nearby
                
        except Exception as e:
            logger.error(f"Nearby search error: {e}")
        
        return []


# Singleton instance
osm_service = OSMService()