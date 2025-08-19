#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recaria_cache_system v017 - 20GB Cache ve Overpass API Entegrasyonu
Yazar: Berk Hatırlı - Bitez Bodrum
Tarih: 25 Haziran 2025
"""

import os
import json
import time
import sqlite3
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path

class RecariaCacheSystem:
    def __init__(self, cache_dir="recaria_cache", max_size_gb=20):
        self.cache_dir = Path(cache_dir)
        # Daha makul bir cache boyutu: 2GB (20GB çok fazla)
        self.max_size_bytes = min(max_size_gb, 2) * 1024 * 1024 * 1024  # Max 2GB
        self.db_path = self.cache_dir / "cache.db"
        self.cache_ttl_days = 30  # Cache entries expire after 30 days
        
        # Cache dizinini oluştur
        self.cache_dir.mkdir(exist_ok=True)
        
        # Veritabanını başlat
        self.init_database()
        
        # Overpass API endpoint
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Başlangıçta temizlik yap
        self.cleanup_expired_entries()
        
    def init_database(self):
        """Cache veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                data_type TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_location ON cache_entries(latitude, longitude)
        ''')
        
        conn.commit()
        conn.close()
        
    def get_cache_size(self):
        """Toplam cache boyutunu hesapla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(size_bytes) FROM cache_entries')
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result[0] else 0
        
    def cleanup_expired_entries(self):
        """Süresi dolmuş cache girişlerini temizle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 30 günden eski girişleri sil
        expiry_date = datetime.now() - timedelta(days=self.cache_ttl_days)
        
        cursor.execute('''
            SELECT file_path FROM cache_entries 
            WHERE created_at < ?
        ''', (expiry_date,))
        
        expired_files = cursor.fetchall()
        
        for (file_path,) in expired_files:
            try:
                os.remove(self.cache_dir / file_path)
            except FileNotFoundError:
                pass
        
        cursor.execute('''
            DELETE FROM cache_entries 
            WHERE created_at < ?
        ''', (expiry_date,))
        
        conn.commit()
        conn.close()
        
        return len(expired_files)
    
    def cleanup_old_entries(self):
        """Eski cache girişlerini temizle (LRU)"""
        current_size = self.get_cache_size()
        
        # %90'ı aştıysa temizlik yap (proaktif)
        if current_size > self.max_size_bytes * 0.9:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # En eski erişilen dosyaları bul
            cursor.execute('''
                SELECT file_path, size_bytes 
                FROM cache_entries 
                ORDER BY last_accessed ASC
            ''')
            
            entries_to_delete = []
            size_to_free = current_size - (self.max_size_bytes * 0.8)  # %80'e düşür
            freed_size = 0
            
            for file_path, size_bytes in cursor.fetchall():
                if freed_size >= size_to_free:
                    break
                    
                entries_to_delete.append(file_path)
                freed_size += size_bytes
                
                # Dosyayı sil
                try:
                    os.remove(self.cache_dir / file_path)
                except FileNotFoundError:
                    pass
                    
            # Veritabanından sil
            if entries_to_delete:
                placeholders = ','.join(['?' for _ in entries_to_delete])
                cursor.execute(f'''
                    DELETE FROM cache_entries 
                    WHERE file_path IN ({placeholders})
                ''', entries_to_delete)
                
            conn.commit()
            conn.close()
            
            return len(entries_to_delete)
        
        return 0
        
    def generate_cache_key(self, query_type, location, radius=1000):
        """Cache anahtarı oluştur"""
        key_data = f"{query_type}_{location}_{radius}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def get_from_cache(self, cache_key):
        """Cache'den veri al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, location_name, latitude, longitude, data_type
            FROM cache_entries 
            WHERE key = ?
        ''', (cache_key,))
        
        result = cursor.fetchone()
        
        if result:
            file_path, location_name, latitude, longitude, data_type = result
            
            # Son erişim zamanını güncelle
            cursor.execute('''
                UPDATE cache_entries 
                SET last_accessed = CURRENT_TIMESTAMP 
                WHERE key = ?
            ''', (cache_key,))
            
            conn.commit()
            
            # Dosyayı oku
            try:
                with open(self.cache_dir / file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                conn.close()
                return {
                    'data': data,
                    'location_name': location_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'data_type': data_type,
                    'from_cache': True
                }
            except FileNotFoundError:
                # Dosya bulunamadı, cache girişini sil
                cursor.execute('DELETE FROM cache_entries WHERE key = ?', (cache_key,))
                conn.commit()
                
        conn.close()
        return None
        
    def save_to_cache(self, cache_key, data, location_name, latitude, longitude, data_type):
        """Veriyi cache'e kaydet"""
        # Önce süresi dolmuş girişleri temizle
        self.cleanup_expired_entries()
        
        # Sonra boyut kontrolü yap
        self.cleanup_old_entries()
        
        # Dosya adı oluştur
        timestamp = int(time.time())
        file_name = f"{cache_key}_{timestamp}.json"
        file_path = self.cache_dir / file_name
        
        # Veriyi dosyaya kaydet
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # Dosya boyutunu hesapla
        file_size = file_path.stat().st_size
        
        # Veritabanına kaydet
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache_entries 
            (key, file_path, size_bytes, location_name, latitude, longitude, data_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cache_key, file_name, file_size, location_name, latitude, longitude, data_type))
        
        conn.commit()
        conn.close()
        
    def query_overpass_api(self, query):
        """Overpass API'ye sorgu gönder"""
        try:
            response = requests.post(
                self.overpass_url,
                data=query,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Overpass API hatası: {e}")
            return None
            
    def get_location_data(self, location_name, latitude=None, longitude=None):
        """Konum verilerini al (cache'den veya API'den)"""
        
        # Koordinatları belirle
        if latitude is None or longitude is None:
            # Konum adından koordinat bul
            coords = self.geocode_location(location_name)
            if coords:
                latitude, longitude = coords
            else:
                return None
                
        # Cache anahtarı oluştur
        cache_key = self.generate_cache_key("location_data", f"{latitude},{longitude}")
        
        # Önce cache'e bak
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        # API'den veri al
        api_data = self.fetch_location_from_api(latitude, longitude, location_name)
        
        if api_data:
            # Cache'e kaydet
            self.save_to_cache(
                cache_key, 
                api_data, 
                location_name, 
                latitude, 
                longitude, 
                "location_data"
            )
            
            return {
                'data': api_data,
                'location_name': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'data_type': 'location_data',
                'from_cache': False
            }
            
        return None
        
    def fetch_location_from_api(self, latitude, longitude, location_name):
        """API'den konum verilerini çek"""
        
        # Overpass QL sorgusu
        radius = 1000  # 1km yarıçap
        
        query = f"""
        [out:json][timeout:25];
        (
          way["highway"](around:{radius},{latitude},{longitude});
          way["building"](around:{radius},{latitude},{longitude});
          way["amenity"](around:{radius},{latitude},{longitude});
          way["shop"](around:{radius},{latitude},{longitude});
          relation["type"="route"]["route"="bus"](around:{radius},{latitude},{longitude});
        );
        out geom;
        """
        
        result = self.query_overpass_api(query)
        
        if result:
            # Veriyi işle
            processed_data = self.process_overpass_data(result)
            return processed_data
            
        return None
        
    def process_overpass_data(self, raw_data):
        """Overpass API verisini işle"""
        processed = {
            'streets': [],
            'buildings': [],
            'amenities': [],
            'shops': [],
            'transport': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if 'elements' in raw_data:
            for element in raw_data['elements']:
                tags = element.get('tags', {})
                
                # Yollar
                if 'highway' in tags:
                    street_name = tags.get('name', 'İsimsiz Yol')
                    processed['streets'].append({
                        'name': street_name,
                        'type': tags['highway'],
                        'id': element['id']
                    })
                    
                # Binalar
                elif 'building' in tags:
                    building_name = tags.get('name', 'İsimsiz Bina')
                    processed['buildings'].append({
                        'name': building_name,
                        'type': tags['building'],
                        'id': element['id']
                    })
                    
                # Tesisler
                elif 'amenity' in tags:
                    amenity_name = tags.get('name', 'İsimsiz Tesis')
                    processed['amenities'].append({
                        'name': amenity_name,
                        'type': tags['amenity'],
                        'id': element['id']
                    })
                    
                # Dükkanlar
                elif 'shop' in tags:
                    shop_name = tags.get('name', 'İsimsiz Dükkan')
                    processed['shops'].append({
                        'name': shop_name,
                        'type': tags['shop'],
                        'id': element['id']
                    })
                    
        return processed
        
    def geocode_location(self, location_name):
        """Konum adından koordinat bul"""
        # Basit geocoding (gerçek uygulamada Nominatim API kullanılabilir)
        locations = {
            'istanbul': (41.0082, 28.9784),
            'ankara': (39.9334, 32.8597),
            'izmir': (38.4192, 27.1287),
            'antalya': (36.8969, 30.7133),
            'bursa': (40.1826, 29.0665),
            'bodrum': (37.0344, 27.4305),
            'bitez': (37.0333, 27.3833)
        }
        
        return locations.get(location_name.lower())
        
    def search_businesses(self, business_type, location_name, latitude=None, longitude=None):
        """İşletme ara"""
        
        if latitude is None or longitude is None:
            coords = self.geocode_location(location_name)
            if coords:
                latitude, longitude = coords
            else:
                return []
                
        cache_key = self.generate_cache_key("business_search", f"{business_type}_{latitude},{longitude}")
        
        # Cache'e bak
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            return cached_data['data']
            
        # API'den ara
        businesses = self.fetch_businesses_from_api(business_type, latitude, longitude)
        
        if businesses:
            self.save_to_cache(
                cache_key,
                businesses,
                location_name,
                latitude,
                longitude,
                "business_search"
            )
            
        return businesses
        
    def fetch_businesses_from_api(self, business_type, latitude, longitude):
        """API'den işletme ara"""
        
        # Overpass QL sorgusu
        radius = 5000  # 5km yarıçap
        
        query = f"""
        [out:json][timeout:25];
        (
          node["shop"~"{business_type}"](around:{radius},{latitude},{longitude});
          way["shop"~"{business_type}"](around:{radius},{latitude},{longitude});
          node["amenity"~"{business_type}"](around:{radius},{latitude},{longitude});
          way["amenity"~"{business_type}"](around:{radius},{latitude},{longitude});
        );
        out center;
        """
        
        result = self.query_overpass_api(query)
        
        businesses = []
        
        if result and 'elements' in result:
            for element in result['elements']:
                tags = element.get('tags', {})
                name = tags.get('name', f'İsimsiz {business_type}')
                
                # Koordinatları al
                if 'lat' in element and 'lon' in element:
                    lat, lon = element['lat'], element['lon']
                elif 'center' in element:
                    lat, lon = element['center']['lat'], element['center']['lon']
                else:
                    continue
                    
                # Mesafeyi hesapla
                distance = self.calculate_distance(latitude, longitude, lat, lon)
                
                businesses.append({
                    'name': name,
                    'type': tags.get('shop', tags.get('amenity', business_type)),
                    'distance_km': round(distance, 2),
                    'latitude': lat,
                    'longitude': lon
                })
                
        # Mesafeye göre sırala
        businesses.sort(key=lambda x: x['distance_km'])
        
        return businesses[:10]  # En yakın 10 işletme
        
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """İki nokta arası mesafe hesapla (km)"""
        import math
        
        R = 6371  # Dünya yarıçapı (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
        
    def get_cache_stats(self):
        """Cache istatistiklerini al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*), SUM(size_bytes) FROM cache_entries')
        count, total_size = cursor.fetchone()
        
        cursor.execute('''
            SELECT data_type, COUNT(*) 
            FROM cache_entries 
            GROUP BY data_type
        ''')
        
        by_type = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_entries': count or 0,
            'total_size_bytes': total_size or 0,
            'total_size_mb': round((total_size or 0) / (1024 * 1024), 2),
            'total_size_gb': round((total_size or 0) / (1024 * 1024 * 1024), 2),
            'max_size_gb': self.max_size_bytes / (1024 * 1024 * 1024),
            'usage_percent': round(((total_size or 0) / self.max_size_bytes) * 100, 2),
            'ttl_days': self.cache_ttl_days,
            'by_type': by_type
        }

# Test fonksiyonu
def test_cache_system():
    """Cache sistemini test et"""
    cache = RecariaCacheSystem()
    
    print("🧪 Cache sistemi test ediliyor...")
    
    # İstatistikleri göster
    stats = cache.get_cache_stats()
    print(f"📊 Cache İstatistikleri:")
    print(f"   Toplam girdi: {stats['total_entries']}")
    print(f"   Toplam boyut: {stats['total_size_mb']} MB")
    print(f"   Kullanım: %{stats['usage_percent']}")
    
    # Konum verisi al
    print("\n🌍 Bitez konum verisi alınıyor...")
    location_data = cache.get_location_data("bitez", 37.0333, 27.3833)
    
    if location_data:
        print(f"✅ Veri alındı: {len(location_data['data']['streets'])} sokak")
        print(f"   Cache'den: {'Evet' if location_data['from_cache'] else 'Hayır'}")
    
    # İşletme ara
    print("\n🍦 Dondurmacı aranıyor...")
    businesses = cache.search_businesses("ice_cream", "bitez", 37.0333, 27.3833)
    
    print(f"✅ {len(businesses)} işletme bulundu")
    for business in businesses[:3]:
        print(f"   {business['name']} - {business['distance_km']} km")

if __name__ == "__main__":
    test_cache_system()

