"""
Django backend API for Recaria map-based game
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import json
import logging
import time
from datetime import datetime
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, LineString, Polygon, mapping
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OSMnx
ox.settings.log_console = False
ox.settings.use_cache = True
ox.settings.cache_folder = os.path.join(settings.recaria_DATA_ROOT, 'cache')
ox.settings.default_user_agent = "recaria/v047-beta"

# Ensure cache directory exists
os.makedirs(ox.settings.cache_folder, exist_ok=True)

def health_check(request):
    """
    Simple health check endpoint
    """
    return JsonResponse({
        "status": "ok",
        "version": "0.46-beta",
        "timestamp": datetime.now().isoformat()
    })

def get_geo_data(request):
    """
    Get geographical data around a point
    """
    try:
        # Get parameters
        lat = float(request.GET.get('lat', 37.031))
        lon = float(request.GET.get('lon', 27.303))
        radius = int(request.GET.get('radius', 150))
        
        # Check if we have cached data
        cache_file = os.path.join(
            settings.recaria_DATA_ROOT, 
            f'geo_{lat:.6f}_{lon:.6f}_{radius}.geojson'
        )
        
        if os.path.exists(cache_file):
            # Use cached data
            logger.info(f"Using cached data from {cache_file}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return JsonResponse(data)
        
        # Fetch data from OSM
        logger.info(f"Fetching OSM data for {lat}, {lon} with radius {radius}m")
        start_time = time.time()
        
        # Get street network
        G = ox.graph_from_point((lat, lon), dist=radius, network_type='all')
        
        # Get buildings
        buildings = ox.geometries_from_point(
            (lat, lon), 
            dist=radius, 
            tags={'building': True}
        )
        
        # Get points of interest
        pois = ox.geometries_from_point(
            (lat, lon), 
            dist=radius, 
            tags={
                'amenity': True,
                'shop': True,
                'tourism': True,
                'leisure': True
            }
        )
        
        # Process the data into GeoJSON
        features = []
        
        # Process streets
        for u, v, data in G.edges(data=True):
            if 'geometry' in data:
                geom = data['geometry']
            else:
                # If no geometry attribute, create a straight line
                u_x, u_y = G.nodes[u]['x'], G.nodes[u]['y']
                v_x, v_y = G.nodes[v]['x'], G.nodes[v]['y']
                geom = LineString([(u_x, u_y), (v_x, v_y)])
            
            # Create GeoJSON feature
            feature = {
                "type": "Feature",
                "geometry": mapping(geom),
                "properties": {
                    "type": "road",
                    "name": data.get('name', 'Unnamed Road'),
                    "highway": data.get('highway', 'unknown')
                }
            }
            features.append(feature)
        
        # Process buildings
        if not buildings.empty:
            for idx, building in buildings.iterrows():
                if 'geometry' in building:
                    # Create GeoJSON feature
                    feature = {
                        "type": "Feature",
                        "geometry": mapping(building.geometry),
                        "properties": {
                            "type": "building",
                            "name": building.get('name', 'Unnamed Building'),
                            "building": building.get('building', 'yes')
                        }
                    }
                    features.append(feature)
        
        # Process POIs
        if not pois.empty:
            for idx, poi in pois.iterrows():
                if 'geometry' in poi:
                    # Create GeoJSON feature
                    feature = {
                        "type": "Feature",
                        "geometry": mapping(poi.geometry),
                        "properties": {
                            "type": "point",
                            "name": poi.get('name', 'Unnamed POI'),
                            "amenity": poi.get('amenity', ''),
                            "shop": poi.get('shop', ''),
                            "tourism": poi.get('tourism', ''),
                            "leisure": poi.get('leisure', ''),
                            "description": get_poi_description(poi)
                        }
                    }
                    features.append(feature)
        
        # Create final GeoJSON
        geojson = {
            "center": [lat, lon],
            "radius": radius,
            "features": features
        }
        
        # Cache the result
        with open(cache_file, 'w') as f:
            json.dump(geojson, f)
        
        logger.info(f"OSM data fetched in {time.time() - start_time:.2f} seconds")
        
        return JsonResponse(geojson)
    
    except Exception as e:
        logger.error(f"Error fetching geo data: {str(e)}")
        return JsonResponse({
            "error": str(e),
            "center": [lat, lon],
            "radius": radius,
            "features": []
        }, status=500)

def get_poi_description(poi):
    """Generate a description for a POI based on its tags"""
    if 'name' not in poi:
        return "İlgi çekici bir nokta"
    
    descriptions = []
    
    if 'amenity' in poi:
        if poi['amenity'] == 'restaurant':
            descriptions.append("Lezzetli yemekler sunan bir restoran")
        elif poi['amenity'] == 'cafe':
            descriptions.append("Keyifli bir kafe")
        elif poi['amenity'] == 'bar':
            descriptions.append("Popüler bir bar")
        elif poi['amenity'] == 'bank':
            descriptions.append("Para işlemleriniz için bir banka")
        elif poi['amenity'] == 'pharmacy':
            descriptions.append("Sağlık ürünleri satan bir eczane")
        elif poi['amenity'] == 'hospital':
            descriptions.append("Sağlık hizmetleri sunan bir hastane")
    
    if 'shop' in poi:
        if poi['shop'] == 'supermarket':
            descriptions.append("Günlük ihtiyaçlarınız için bir süpermarket")
        elif poi['shop'] == 'convenience':
            descriptions.append("Hızlı alışveriş için bir market")
        elif poi['shop'] == 'clothes':
            descriptions.append("Moda ürünleri satan bir giyim mağazası")
    
    if 'tourism' in poi:
        if poi['tourism'] == 'hotel':
            descriptions.append("Konaklamak için bir otel")
        elif poi['tourism'] == 'museum':
            descriptions.append("Kültürel bir müze")
        elif poi['tourism'] == 'attraction':
            descriptions.append("Turistik bir cazibe merkezi")
    
    if 'leisure' in poi:
        if poi['leisure'] == 'park':
            descriptions.append("Dinlenmek için güzel bir park")
        elif poi['leisure'] == 'garden':
            descriptions.append("Huzurlu bir bahçe")
        elif poi['leisure'] == 'sports_centre':
            descriptions.append("Spor aktiviteleri için bir merkez")
    
    if descriptions:
        return descriptions[0]
    else:
        return "İlgi çekici bir nokta"

@csrf_exempt
def save_discovery(request):
    """
    Save a player's discovery
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['lat', 'lng', 'name', 'type']
        for field in required_fields:
            if field not in data:
                return JsonResponse({"error": f"Missing required field: {field}"}, status=400)
        
        # Create discovery record
        discovery = {
            "lat": data['lat'],
            "lng": data['lng'],
            "name": data['name'],
            "type": data['type'],
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "player_id": request.session.get('player_id', 'anonymous')
        }
        
        # Save to discoveries file
        discoveries_file = os.path.join(settings.recaria_DATA_ROOT, 'discoveries.json')
        
        if os.path.exists(discoveries_file):
            with open(discoveries_file, 'r') as f:
                discoveries = json.load(f)
        else:
            discoveries = []
        
        discoveries.append(discovery)
        
        with open(discoveries_file, 'w') as f:
            json.dump(discoveries, f)
        
        # Update player stats
        update_player_stats(request, discovery)
        
        return JsonResponse({
            "status": "success",
            "discovery_id": len(discoveries),
            "message": "Discovery saved successfully"
        })
    
    except Exception as e:
        logger.error(f"Error saving discovery: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def bulk_save_discoveries(request):
    """
    Save multiple discoveries at once (for offline sync)
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        
        if 'discoveries' not in data or not isinstance(data['discoveries'], list):
            return JsonResponse({"error": "Missing or invalid 'discoveries' array"}, status=400)
        
        discoveries = data['discoveries']
        saved_count = 0
        
        # Get existing discoveries
        discoveries_file = os.path.join(settings.recaria_DATA_ROOT, 'discoveries.json')
        
        if os.path.exists(discoveries_file):
            with open(discoveries_file, 'r') as f:
                existing_discoveries = json.load(f)
        else:
            existing_discoveries = []
        
        # Process each discovery
        for discovery in discoveries:
            # Validate required fields
            required_fields = ['lat', 'lng', 'name', 'type']
            valid = True
            for field in required_fields:
                if field not in discovery:
                    valid = False
                    break
            
            if valid:
                # Add player_id
                discovery['player_id'] = request.session.get('player_id', 'anonymous')
                
                # Add to existing discoveries
                existing_discoveries.append(discovery)
                saved_count += 1
                
                # Update player stats
                update_player_stats(request, discovery)
        
        # Save all discoveries
        with open(discoveries_file, 'w') as f:
            json.dump(existing_discoveries, f)
        
        return JsonResponse({
            "status": "success",
            "saved_count": saved_count,
            "total_discoveries": len(existing_discoveries),
            "message": f"{saved_count} discoveries saved successfully"
        })
    
    except Exception as e:
        logger.error(f"Error saving bulk discoveries: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def get_player_data(request):
    """
    Get player data
    """
    try:
        # Get player ID from session or create new one
        player_id = request.session.get('player_id')
        
        if not player_id:
            # Generate a new player ID
            player_id = f"player_{int(time.time())}_{random.randint(1000, 9999)}"
            request.session['player_id'] = player_id
        
        # Get player data file
        player_file = os.path.join(settings.recaria_DATA_ROOT, f'player_{player_id}.json')
        
        if os.path.exists(player_file):
            with open(player_file, 'r') as f:
                player_data = json.load(f)
        else:
            # Create new player data
            player_data = {
                "player_id": player_id,
                "level": 1,
                "score": 0,
                "exploration": 0,
                "inventory": [],
                "discoveredLocations": [],
                "achievements": [],
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            
            # Save new player data
            with open(player_file, 'w') as f:
                json.dump(player_data, f)
        
        # Update last login
        player_data['last_login'] = datetime.now().isoformat()
        
        with open(player_file, 'w') as f:
            json.dump(player_data, f)
        
        return JsonResponse(player_data)
    
    except Exception as e:
        logger.error(f"Error getting player data: {str(e)}")
        return JsonResponse({
            "error": str(e),
            "player_id": request.session.get('player_id', 'unknown'),
            "level": 1,
            "score": 0,
            "exploration": 0,
            "inventory": [],
            "discoveredLocations": [],
            "achievements": []
        }, status=500)

def update_player_stats(request, discovery):
    """
    Update player stats based on a discovery
    """
    try:
        # Get player ID from session
        player_id = request.session.get('player_id')
        
        if not player_id:
            return
        
        # Get player data file
        player_file = os.path.join(settings.recaria_DATA_ROOT, f'player_{player_id}.json')
        
        if os.path.exists(player_file):
            with open(player_file, 'r') as f:
                player_data = json.load(f)
        else:
            # Create new player data
            player_data = {
                "player_id": player_id,
                "level": 1,
                "score": 0,
                "exploration": 0,
                "inventory": [],
                "discoveredLocations": [],
                "achievements": [],
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
        
        # Add discovery to player's discovered locations
        player_data['discoveredLocations'].append({
            "lat": discovery['lat'],
            "lng": discovery['lng'],
            "name": discovery['name'],
            "type": discovery['type'],
            "timestamp": discovery.get('timestamp', datetime.now().isoformat())
        })
        
        # Add points based on discovery type
        points = 10  # Default points
        
        if discovery['type'] == 'building':
            points = 15
        elif discovery['type'] == 'road':
            points = 5
        elif discovery['type'] == 'point':
            points = 25
        elif discovery['type'] == 'area':
            points = 10
        
        player_data['score'] += points
        
        # Update level (1 level per 100 points)
        player_data['level'] = (player_data['score'] // 100) + 1
        
        # Update exploration percentage (max 100%)
        player_data['exploration'] = min(100, player_data['score'] // 500)
        
        # Check for achievements
        check_achievements(player_data)
        
        # Save updated player data
        with open(player_file, 'w') as f:
            json.dump(player_data, f)
    
    except Exception as e:
        logger.error(f"Error updating player stats: {str(e)}")

def check_achievements(player_data):
    """
    Check and update player achievements
    """
    achievements = [
        {
            "id": "first_discovery",
            "name": "İlk Keşif",
            "description": "İlk konumu keşfettin!",
            "condition": lambda p: len(p['discoveredLocations']) >= 1,
            "points": 50
        },
        {
            "id": "explorer_novice",
            "name": "Acemi Kaşif",
            "description": "10 konum keşfettin!",
            "condition": lambda p: len(p['discoveredLocations']) >= 10,
            "points": 100
        },
        {
            "id": "road_master",
            "name": "Yol Ustası",
            "description": "5 yol keşfettin!",
            "condition": lambda p: len([loc for loc in p['discoveredLocations'] if loc['type'] == 'road']) >= 5,
            "points": 75
        },
        {
            "id": "building_explorer",
            "name": "Bina Kaşifi",
            "description": "5 bina keşfettin!",
            "condition": lambda p: len([loc for loc in p['discoveredLocations'] if loc['type'] == 'building']) >= 5,
            "points": 75
        },
        {
            "id": "point_collector",
            "name": "Nokta Toplayıcı",
            "description": "3 ilgi noktası keşfettin!",
            "condition": lambda p: len([loc for loc in p['discoveredLocations'] if loc['type'] == 'point']) >= 3,
            "points": 100
        }
    ]
    
    # Check each achievement
    for achievement in achievements:
        if achievement['id'] not in player_data['achievements'] and achievement['condition'](player_data):
            # Achievement unlocked
            player_data['achievements'].append(achievement['id'])
            player_data['score'] += achievement['points']
