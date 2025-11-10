"""
Enhanced OpenStreetMap Service with fallback search strategies
"""

import logging
import requests
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from django.core.cache import cache
from django.conf import settings
import json

logger = logging.getLogger(__name__)

class EnhancedOSMService:
    """Enhanced OSM service with multiple search strategies"""
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    USER_AGENT = "UNIBOS/1.0"
    CACHE_TTL = 86400  # 24 hours
    
    # Common Turkish business name variations
    BUSINESS_VARIATIONS = {
        'petrol': ['petrol', 'akaryakıt', 'benzin istasyonu', 'fuel', 'gas station'],
        'market': ['market', 'süpermarket', 'bakkal', 'grocery', 'store'],
        'restaurant': ['restaurant', 'restoran', 'lokanta', 'kebap', 'döner'],
        'cafe': ['cafe', 'kafe', 'kahve', 'coffee'],
        'pharmacy': ['eczane', 'pharmacy', 'apotheke'],
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT
        })
    
    def search_business_multi_strategy(self, name: str, location_hint: str = '', country: str = 'tr') -> Optional[Dict]:
        """
        Search for business using multiple strategies
        """
        # Strategy 1: Direct search
        result = self._search_nominatim(name, location_hint, country)
        if result:
            return result
        
        # Strategy 2: Try with business type variations
        result = self._search_with_variations(name, location_hint, country)
        if result:
            return result
        
        # Strategy 3: Search by amenity type
        result = self._search_by_amenity(name, location_hint, country)
        if result:
            return result
        
        # Strategy 4: Overpass API for detailed search
        result = self._search_overpass(name, location_hint)
        if result:
            return result
        
        # Strategy 5: Fuzzy search
        result = self._fuzzy_search(name, location_hint, country)
        if result:
            return result
        
        logger.warning(f"Could not find business: {name}")
        return None
    
    def _search_nominatim(self, name: str, location_hint: str, country: str) -> Optional[Dict]:
        """Standard Nominatim search"""
        try:
            query = f"{name} {location_hint}".strip()
            
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
                if results:
                    return self._format_result(results[0])
        except Exception as e:
            logger.error(f"Nominatim search error: {e}")
        
        return None
    
    def _search_with_variations(self, name: str, location_hint: str, country: str) -> Optional[Dict]:
        """Search with business type variations"""
        # Detect business type from name
        name_lower = name.lower()
        
        for biz_type, variations in self.BUSINESS_VARIATIONS.items():
            if any(var in name_lower for var in variations):
                # Try each variation
                for variation in variations[:3]:  # Limit to 3 attempts
                    modified_query = f"{name} {variation}"
                    result = self._search_nominatim(modified_query, location_hint, country)
                    if result:
                        return result
        
        return None
    
    def _search_by_amenity(self, name: str, location_hint: str, country: str) -> Optional[Dict]:
        """Search by amenity type"""
        # Determine amenity type
        amenity_map = {
            'petrol': 'fuel',
            'akaryakıt': 'fuel',
            'market': 'supermarket',
            'restaurant': 'restaurant',
            'cafe': 'cafe',
            'eczane': 'pharmacy',
        }
        
        amenity = None
        name_lower = name.lower()
        for keyword, amenity_type in amenity_map.items():
            if keyword in name_lower:
                amenity = amenity_type
                break
        
        if not amenity:
            return None
        
        try:
            params = {
                'amenity': amenity,
                'format': 'json',
                'limit': 20,
                'addressdetails': 1,
                'namedetails': 1,
                'countrycodes': country
            }
            
            if location_hint:
                params['q'] = location_hint
            
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Find best match by name similarity
                best_match = None
                best_score = 0
                
                for result in results:
                    display_name = result.get('display_name', '').lower()
                    name_details = result.get('namedetails', {})
                    
                    # Check various name fields
                    for field in ['name', 'brand', 'operator', 'official_name']:
                        if field in name_details:
                            field_value = name_details[field].lower()
                            score = self._calculate_similarity(name.lower(), field_value)
                            if score > best_score:
                                best_score = score
                                best_match = result
                
                if best_match and best_score > 0.5:
                    return self._format_result(best_match)
        
        except Exception as e:
            logger.error(f"Amenity search error: {e}")
        
        return None
    
    def _search_overpass(self, name: str, location_hint: str) -> Optional[Dict]:
        """Use Overpass API for detailed search"""
        try:
            # Build Overpass query
            name_escaped = name.replace('"', '\\"')
            
            # Search in Turkey by default
            query = f'''
            [out:json][timeout:5];
            area["ISO3166-1"="TR"]->.searchArea;
            (
              node["name"~"{name_escaped}",i](area.searchArea);
              way["name"~"{name_escaped}",i](area.searchArea);
              relation["name"~"{name_escaped}",i](area.searchArea);
            );
            out body;
            '''
            
            response = self.session.post(
                self.OVERPASS_URL,
                data={'data': query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                
                if elements:
                    # Format first result
                    element = elements[0]
                    return {
                        'display_name': element.get('tags', {}).get('name', name),
                        'lat': element.get('lat'),
                        'lon': element.get('lon'),
                        'address': element.get('tags', {}),
                        'type': element.get('type'),
                        'osm_id': element.get('id'),
                        'source': 'overpass'
                    }
        
        except Exception as e:
            logger.error(f"Overpass search error: {e}")
        
        return None
    
    def _fuzzy_search(self, name: str, location_hint: str, country: str) -> Optional[Dict]:
        """Fuzzy search with partial matching"""
        # Split name into parts and search
        name_parts = name.split()
        
        for i in range(len(name_parts), 0, -1):
            partial_name = ' '.join(name_parts[:i])
            result = self._search_nominatim(partial_name, location_hint, country)
            if result:
                return result
        
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity score"""
        # Simple similarity based on common characters
        set1 = set(str1.lower().replace(' ', ''))
        set2 = set(str2.lower().replace(' ', ''))
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _format_result(self, osm_result: Dict) -> Dict:
        """Format OSM result to standard format"""
        address = osm_result.get('address', {})
        
        return {
            'display_name': osm_result.get('display_name', ''),
            'lat': float(osm_result.get('lat', 0)),
            'lon': float(osm_result.get('lon', 0)),
            'osm_id': osm_result.get('osm_id'),
            'osm_type': osm_result.get('osm_type'),
            'place_id': osm_result.get('place_id'),
            'address': {
                'road': address.get('road', ''),
                'neighbourhood': address.get('neighbourhood', ''),
                'suburb': address.get('suburb', ''),
                'city': address.get('city', address.get('town', '')),
                'state': address.get('state', ''),
                'postcode': address.get('postcode', ''),
                'country': address.get('country', '')
            },
            'tags': osm_result.get('extratags', {}),
            'name_details': osm_result.get('namedetails', {}),
            'type': osm_result.get('type'),
            'class': osm_result.get('class'),
            'importance': osm_result.get('importance', 0)
        }
    
    def search_nearby_with_google_fallback(self, name: str, location: str = '') -> Dict:
        """
        Search with Google Places API fallback (requires API key)
        """
        # First try OSM
        osm_result = self.search_business_multi_strategy(name, location)
        
        if osm_result:
            return {
                'success': True,
                'source': 'osm',
                'data': osm_result
            }
        
        # If OSM fails and Google API key is configured
        google_api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
        if google_api_key:
            try:
                # Google Places text search
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                params = {
                    'query': f"{name} {location} Turkey",
                    'key': google_api_key,
                    'region': 'tr',
                    'language': 'tr'
                }
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        place = data['results'][0]
                        return {
                            'success': True,
                            'source': 'google',
                            'data': {
                                'display_name': place.get('name'),
                                'address': place.get('formatted_address'),
                                'lat': place['geometry']['location']['lat'],
                                'lon': place['geometry']['location']['lng'],
                                'place_id': place.get('place_id'),
                                'types': place.get('types', []),
                                'rating': place.get('rating'),
                                'user_ratings_total': place.get('user_ratings_total')
                            }
                        }
            except Exception as e:
                logger.error(f"Google Places search error: {e}")
        
        return {
            'success': False,
            'error': f'Could not find {name} in any database'
        }


# Known Turkish business chains that might not be in OSM
KNOWN_CHAINS = {
    'PAŞALILAR PETROL': {
        'type': 'fuel',
        'brand': 'Paşalılar',
        'amenity': 'fuel',
        'website': 'https://www.pasalilar.com.tr',
        'note': 'Turkish fuel station chain'
    },
    'PETROL OFİSİ': {
        'type': 'fuel',
        'brand': 'Petrol Ofisi',
        'amenity': 'fuel',
        'website': 'https://www.petrolofisi.com.tr'
    },
    'OPET': {
        'type': 'fuel',
        'brand': 'Opet',
        'amenity': 'fuel',
        'website': 'https://www.opet.com.tr'
    },
    'SHELL': {
        'type': 'fuel',
        'brand': 'Shell',
        'amenity': 'fuel',
        'website': 'https://www.shell.com.tr'
    },
    'BP': {
        'type': 'fuel',
        'brand': 'BP',
        'amenity': 'fuel',
        'website': 'https://www.bp.com'
    },
    'TOTAL': {
        'type': 'fuel',
        'brand': 'Total',
        'amenity': 'fuel',
        'website': 'https://www.total.com.tr'
    }
}