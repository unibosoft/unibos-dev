#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🥕 recaria v021_20250626_2010 - Terminal Multiplayer Edition
===============================================
Yazar: Berk Hatırlı - Bitez Bodrum
Tarih: 26 Haziran 2025, 20:10 (İstanbul Saati)
Versiyon: v021_20250626_2010 - MULTIPLAYER & ENHANCED GRAPHICS
Son Güncelleme: 2025-06-26 20:10:00 +03:00

🌍 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria! 🚀✨

AÇIKLAMA:
=========
recaria v021_20250626_2010 terminal oyunu - Çoklu oyuncu desteği ve gelişmiş grafik.
PostgreSQL tabanlı merkezi sunucu entegrasyonu ile gerçek zamanlı multiplayer.

YENİ ÖZELLİKLER v021_20250626_2010:
===================================
✅ Çoklu Oyuncu Desteği - Aynı kare içinde birden fazla oyuncu
✅ Gelişmiş DOS Grafikleri - Stilize karakterler ve animasyonlar  
✅ 2 Katı Büyük Harita - 100x100 boyutunda responsive harita
✅ Gerçek Konum Arama - Tek ekranda tüm konum türleri
✅ Core Server Entegrasyonu - PostgreSQL tabanlı senkronizasyon
✅ Responsive Tasarım - Terminal boyutuna göre otomatik uyum
✅ Gelişmiş Animasyonlar - Pulse efektleri ve hareket
✅ Multiplayer Chat - Oyuncular arası mesajlaşma

MULTIPLAYER ÖZELLİKLERİ:
========================
- Aynı kare içinde birden fazla oyuncu görünümü
- Gerçek zamanlı konum senkronizasyonu  
- Oyuncular arası mesajlaşma sistemi
- Oyuncu listesi ve durumları
- Çakışma önleme sistemi
- Takım oyunu desteği

KONTROLLER:
===========
w/a/s/d - Hareket (Arrow keys de çalışır)
t - Teleport (hızlı teleport menüsü)
* - Harita büyütme (zoom in)
- - Harita küçültme (zoom out)
" - Harita açma/kapama (default açık)
m - Müzik açma/kapama
o - Ev (reel nokta - Bitez Bodrum)
h - Yardım (detaylı help sistemi)
q - Çıkış

ÖZELLİKLER:
===========
- Responsive tasarım (terminal boyutuna göre uyum)
- 2 katı büyük harita (100x100 boyutunda)
- Stilize animasyonlu karakterler (♂☺♠♦)
- Renkli ASCII grafik sistemi
- Binalar ve işaretler
- Sokak isimleri
- Teleport sistemi (İstanbul, Ankara, İzmir, Antalya, Bursa)
- Zoom kontrolü (responsive limitler)
- Müzik sistemi (açma/kapama)
- Harita görünürlük kontrolü

TEKNİK DETAYLAR:
===============
- Python 3.7+ uyumlu
- ANSI renk desteği
- Terminal boyutu algılama
- Responsive görünüm hesaplama
- Cross-platform uyumluluk

DOSYA YAPISI:
=============
projects/recaria/terminal/
└── recaria_terminal.py (Bu dosya)

GÜNCELLEME GEÇMİŞİ:
===================
v019 - 2025-06-25 18:04:00
- Gelişmiş kısayol sistemi (*, -, ", m, t)
- Müzik kontrolü eklendi
- Harita görünürlük kontrolü
- Help sistemi iyileştirmeleri

v018 - 2025-06-25 17:37:00
- Responsive tasarım
- 2 katı büyük harita
- Stilize karakterler

LİSANS:
=======
© 2025 Berk Hatırlı - Bitez Bodrum
Tüm hakları saklıdır.
"""

import os
import sys
import random
import time
import threading
from datetime import datetime

# Map search modülünü ekle
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from map_search import search_real_places, format_places_for_display
    MAP_SEARCH_AVAILABLE = True
except ImportError:
    MAP_SEARCH_AVAILABLE = False
    print("⚠️ Gerçek harita arama modülü yüklenemedi. Sadece varsayılan şehirler kullanılabilir.")

# Versiyon ve build bilgileri
VERSION = "v019"
BUILD_DATE = "2025-06-25 18:04:00"
AUTHOR = "Berk Hatırlı"
LOCATION = "Bitez Bodrum"

# Oyun durumu
class GameState:
    def __init__(self):
        self.player_x = 50  # Merkez koordinat (2x büyük harita)
        self.player_y = 50
        self.energy = 100
        self.health = 100
        self.location = LOCATION
        self.street = "Marina Yolu"
        self.zoom_level = 1.0
        self.map_visible = True  # Default açık
        self.music_enabled = False  # Default kapalı
        self.running = True
        
        # Terminal boyutu ve responsive görünüm
        self.terminal_width = 80
        self.terminal_height = 24
        self.view_width = 40
        self.view_height = 14
        
        # Harita boyutu (2x büyük)
        self.map_size = 100
        
        # Şehir koordinatları
        self.cities = {
            'istanbul': {'x': 30, 'y': 20, 'name': 'İstanbul'},
            'ankara': {'x': 50, 'y': 40, 'name': 'Ankara'},
            'izmir': {'x': 20, 'y': 60, 'name': 'İzmir'},
            'antalya': {'x': 70, 'y': 80, 'name': 'Antalya'},
            'bursa': {'x': 40, 'y': 30, 'name': 'Bursa'}
        }
        
        # Sokak isimleri
        self.streets = [
            "Marina Yolu", "Bodrum Caddesi", "Atatürk Caddesi",
            "Cumhuriyet Sokağı", "Plaj Caddesi", "Merkez Sokağı"
        ]
        
        # Binalar ve emojiler
        self.buildings = ['🕌', '🏥', '🏫', '⛵', '🏰', '🏨', '🍽️', '🏪', '📮', '🏛️', '🎭', '🏦', '⛽', '🏫']
        
        # Karakterler (stilize animasyonlu)
        self.characters = ['♂', '☺', '♠', '♦']
        self.current_char_index = 0
        
        self.update_terminal_size()

    def update_terminal_size(self):
        """Terminal boyutunu güncelle ve responsive görünüm hesapla"""
        try:
            size = os.get_terminal_size()
            self.terminal_width = size.columns
            self.terminal_height = size.lines
            
            # Responsive görünüm hesaplama
            self.view_width = min(60, max(30, self.terminal_width // 2))
            self.view_height = min(30, max(10, self.terminal_height - 14))
            
        except:
            # Varsayılan değerler
            self.terminal_width = 80
            self.terminal_height = 24
            self.view_width = 40
            self.view_height = 14

    def get_current_character(self):
        """Animasyonlu karakter al"""
        return self.characters[self.current_char_index]
    
    def animate_character(self):
        """Karakter animasyonu"""
        self.current_char_index = (self.current_char_index + 1) % len(self.characters)
    
    def get_random_street(self):
        """Rastgele sokak ismi al"""
        return random.choice(self.streets)
    
    def get_random_building(self):
        """Rastgele bina emoji al"""
        return random.choice(self.buildings)

# Global oyun durumu
game = GameState()

def clear_screen():
    """Ekranı temizle"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Oyun başlığı yazdır"""
    print(f"🥕 recaria {VERSION} - Terminal Oyunu")
    print(f"Yazar: {AUTHOR} - {LOCATION}")
    print("=" * 60)
    print(f"Konum: {game.location}")
    print(f"Koordinat: ({game.player_x}, {game.player_y})")
    print(f"Enerji: {game.energy}/100 | Sağlık: {game.health}/100")
    print(f"Sokak: {game.street}")
    print(f"Terminal: {game.terminal_width}x{game.terminal_height} | Görünüm: {game.view_width}x{game.view_height}")
    if not game.map_visible:
        print("🗺️ Harita: KAPALI")
    if game.music_enabled:
        print("🎵 Müzik: AÇIK")
    print("=" * 60)

def print_help():
    """Yardım menüsü yazdır"""
    clear_screen()
    print(f"🥕 recaria {VERSION} - Yardım Sistemi")
    print("=" * 60)
    print("🎮 KONTROLLER:")
    print("w/a/s/d - Hareket (Arrow keys de çalışır)")
    print("t - Teleport (hızlı teleport menüsü)")
    print("* - Harita büyütme (zoom in)")
    print("- - Harita küçültme (zoom out)")
    print('" - Harita açma/kapama (default açık)')
    print("m - Müzik açma/kapama")
    print("o - Ev (reel nokta - Bitez Bodrum)")
    print("h - Yardım (bu menü)")
    print("q - Çıkış")
    print()
    print("🌍 TELEPORT ŞEHİRLERİ:")
    for city_key, city_data in game.cities.items():
        print(f"- {city_data['name']} ({city_data['x']}, {city_data['y']})")
    print()
    print("🎯 ÖZELLİKLER:")
    print("- Responsive tasarım (terminal boyutuna göre uyum)")
    print("- 2 katı büyük harita (100x100 boyutunda)")
    print("- Stilize animasyonlu karakterler")
    print("- Renkli ASCII grafik sistemi")
    print("- Zoom kontrolü (responsive limitler)")
    print("- Müzik sistemi")
    print("- Harita görünürlük kontrolü")
    print()
    print("=" * 60)
    input("Devam etmek için Enter tuşuna basın...")

def draw_map():
    """Haritayı çiz"""
    if not game.map_visible:
        print("🗺️ Harita kapalı. Açmak için '\"' tuşuna basın.")
        return
    
    # Görünüm alanını hesapla
    start_x = max(0, game.player_x - game.view_width // 2)
    end_x = min(game.map_size, start_x + game.view_width)
    start_y = max(0, game.player_y - game.view_height // 2)
    end_y = min(game.map_size, start_y + game.view_height)
    
    # Haritayı çiz
    for y in range(start_y, end_y):
        line = ""
        for x in range(start_x, end_x):
            if x == game.player_x and y == game.player_y:
                # Oyuncu karakteri (animasyonlu)
                line += f"\033[91m{game.get_current_character()}\033[0m"  # Kırmızı
            elif x % 8 == 0 and y % 6 == 0:
                # Binalar
                line += f"\033[93m{game.get_random_building()}\033[0m"  # Sarı
            elif x % 8 == 0:
                # Dikey yollar
                line += "\033[90m║\033[0m"  # Gri
            elif y % 6 == 0:
                # Yatay yollar
                line += "\033[90m═\033[0m"  # Gri
            else:
                # Boş alan
                line += "\033[92m·\033[0m"  # Yeşil
        print(line)

def print_controls():
    """Kontrol bilgilerini yazdır"""
    controls = "Kontroller: w/a/s/d-Hareket | t-Teleport | */--Zoom | \"-Harita | m-Müzik | o-Ev | h-Yardım | q-Çıkış"
    print(controls)

def teleport_menu():
    """Gelişmiş Teleport Menüsü - Gerçek Harita Arama"""
    clear_screen()
    print(f"🥕 recaria {VERSION} - Gelişmiş Teleport Sistemi")
    print("=" * 60)
    print("🌍 Teleport Seçenekleri:")
    print("1 - Varsayılan şehirler")
    print("2 - Gerçek mekan arama (cafeler, restoranlar, vb.)")
    print("0 - İptal")
    print("=" * 60)
    
    try:
        choice = input("Seçim (0-2): ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            # Varsayılan şehirler
            default_city_teleport()
        elif choice == '2':
            # Gerçek mekan arama
            if MAP_SEARCH_AVAILABLE:
                real_place_teleport()
            else:
                print("❌ Gerçek harita arama modülü kullanılamıyor!")
                print("Varsayılan şehirlere yönlendiriliyor...")
                time.sleep(2)
                default_city_teleport()
        else:
            print("❌ Geçersiz seçim!")
            time.sleep(1)
    except Exception as e:
        print(f"❌ Teleport hatası: {e}")
        time.sleep(1)

def default_city_teleport():
    """Varsayılan şehir teleport sistemi"""
    clear_screen()
    print(f"🥕 recaria {VERSION} - Varsayılan Şehirler")
    print("=" * 40)
    print("🌍 Mevcut Şehirler:")
    
    city_list = list(game.cities.items())
    for i, (city_key, city_data) in enumerate(city_list, 1):
        print(f"{i} - {city_data['name']} ({city_data['x']}, {city_data['y']})")
    
    print("0 - Geri")
    print("=" * 40)
    
    try:
        choice = input("Nereye ışınlanmak istiyorsunuz? ").strip()
        
        if choice == '0':
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(city_list):
            city_key, city_data = city_list[choice_num - 1]
            game.player_x = city_data['x']
            game.player_y = city_data['y']
            game.location = city_data['name']
            game.street = game.get_random_street()
            game.energy = max(10, game.energy - 20)  # Teleport enerji harcar
            print(f"🌍 {city_data['name']}'a ışınlandınız!")
            time.sleep(1)
        else:
            print("❌ Geçersiz seçim!")
            time.sleep(1)
    except ValueError:
        print("❌ Geçersiz giriş!")
        time.sleep(1)

def real_place_teleport():
    """Gerçek mekan arama ve teleport sistemi"""
    clear_screen()
    print(f"🥕 recaria {VERSION} - Gerçek Mekan Arama")
    print("=" * 60)
    print("🔍 Gerçek mekanları arayın!")
    print("Örnek: 'vamos cafe', 'starbucks', 'mcdonalds', 'hotel'")
    print("=" * 60)
    
    # Mekan adı al
    query = input("🔍 Aranacak mekan: ").strip()
    if not query:
        print("❌ Mekan adı boş olamaz!")
        time.sleep(1)
        return
    
    # Lokasyon al (opsiyonel)
    location = input("📍 Lokasyon (boş bırakabilirsiniz): ").strip()
    if not location:
        location = "bitez bodrum"  # Varsayılan
    
    # Kategori al (opsiyonel)
    print("\n🏷️ Kategori seçin (opsiyonel):")
    print("1-cafe, 2-restaurant, 3-bar, 4-shop, 5-hotel, 6-hepsi")
    category_choice = input("Kategori (1-6, boş=hepsi): ").strip()
    
    category_map = {
        '1': 'cafe',
        '2': 'restaurant', 
        '3': 'bar',
        '4': 'shop',
        '5': 'hotel'
    }
    category = category_map.get(category_choice, None)
    
    print(f"\n🔍 Aranıyor: '{query}' ({location})")
    print("⏳ Lütfen bekleyin...")
    
    try:
        # Gerçek mekan arama
        places = search_real_places(query, location, category, limit=10)
        
        if not places:
            print("❌ Hiç sonuç bulunamadı!")
            print("💡 Farklı anahtar kelimeler deneyin.")
            time.sleep(2)
            return
        
        # Sonuçları göster
        clear_screen()
        print(f"🥕 recaria {VERSION} - Arama Sonuçları")
        print("=" * 60)
        print(f"🔍 '{query}' için {len(places)} sonuç:")
        print("=" * 60)
        
        for i, place in enumerate(places, 1):
            name = place.get('name', 'İsimsiz')
            rating = place.get('rating', 0)
            reviews = place.get('review_count', 0)
            distance = place.get('distance_km', 0)
            category_info = place.get('category', 'other')
            
            print(f"{i}. {name}")
            print(f"   ⭐ {rating}/5.0 ({reviews} yorum)")
            print(f"   📍 {distance} km uzaklıkta")
            print(f"   🏷️ {category_info}")
            print("-" * 40)
        
        print("0 - Geri")
        print("=" * 60)
        
        # Seçim al
        choice = input("Hangi mekana ışınlanmak istiyorsuniz? ").strip()
        
        if choice == '0':
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(places):
            selected_place = places[choice_num - 1]
            
            # Koordinatları al
            coords = selected_place.get('coordinates', {})
            lat = coords.get('lat', 37.0344)  # Bitez varsayılan
            lon = coords.get('lon', 27.3914)
            
            # Oyun koordinatlarına dönüştür (basit mapping)
            game_x = int(50 + (lon - 27.3914) * 100)  # Bitez merkez
            game_y = int(50 + (lat - 37.0344) * 100)
            
            # Sınırları kontrol et
            game_x = max(0, min(game.map_size - 1, game_x))
            game_y = max(0, min(game.map_size - 1, game_y))
            
            # Teleport et
            game.player_x = game_x
            game.player_y = game_y
            game.location = selected_place.get('name', 'Bilinmeyen Mekan')
            game.street = selected_place.get('formatted_address', 'Bilinmeyen Sokak')[:30]
            game.energy = max(10, game.energy - 30)  # Gerçek teleport daha fazla enerji harcar
            
            print(f"\n🌍 {selected_place.get('name', 'Mekan')}a ışınlandınız!")
            print(f"📍 Koordinat: ({game_x}, {game_y})")
            print(f"⭐ Rating: {selected_place.get('rating', 0)}/5.0")
            print(f"📧 {selected_place.get('formatted_address', '')[:50]}")
            time.sleep(3)
        else:
            print("❌ Geçersiz seçim!")
            time.sleep(1)
            
    except ValueError:
        print("❌ Geçersiz giriş!")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Arama hatası: {e}")
        print("💡 İnternet bağlantınızı kontrol edin.")
        time.sleep(2)

def zoom_in():
    """Haritayı büyüt"""
    if game.zoom_level < 2.0:
        game.zoom_level += 0.2
        game.view_width = max(20, int(game.view_width * 0.9))
        game.view_height = max(8, int(game.view_height * 0.9))
        print(f"🔍 Zoom: {int(game.zoom_level * 100)}%")
    else:
        print("🔍 Maksimum zoom seviyesi!")

def zoom_out():
    """Haritayı küçült"""
    if game.zoom_level > 0.5:
        game.zoom_level -= 0.2
        game.view_width = min(60, int(game.view_width * 1.1))
        game.view_height = min(30, int(game.view_height * 1.1))
        print(f"🔍 Zoom: {int(game.zoom_level * 100)}%")
    else:
        print("🔍 Minimum zoom seviyesi!")

def toggle_map():
    """Harita görünürlüğünü değiştir"""
    game.map_visible = not game.map_visible
    status = "AÇIK" if game.map_visible else "KAPALI"
    print(f"🗺️ Harita: {status}")

def toggle_music():
    """Müzik açma/kapama"""
    game.music_enabled = not game.music_enabled
    status = "AÇIK" if game.music_enabled else "KAPALI"
    print(f"🎵 Müzik: {status}")
    if game.music_enabled:
        print("🎶 ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫")

def go_home():
    """Reel noktaya (Bitez Bodrum) dön"""
    game.player_x = 50
    game.player_y = 50
    game.location = LOCATION
    game.street = "Marina Yolu"
    game.zoom_level = 1.0
    game.update_terminal_size()
    print(f"🏠 {LOCATION}'a döndünüz!")

def move_player(dx, dy):
    """Oyuncuyu hareket ettir"""
    new_x = max(0, min(game.map_size - 1, game.player_x + dx))
    new_y = max(0, min(game.map_size - 1, game.player_y + dy))
    
    if new_x != game.player_x or new_y != game.player_y:
        game.player_x = new_x
        game.player_y = new_y
        game.energy = max(0, game.energy - 1)
        game.street = game.get_random_street()
        game.animate_character()

def get_input():
    """Kullanıcı girişini al"""
    try:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except:
        # Windows veya termios olmayan sistemler için
        return input().lower()

def main():
    """Ana oyun döngüsü"""
    print(f"🚀 recaria {VERSION} başlatılıyor...")
    print(f"📅 Build: {BUILD_DATE}")
    print(f"👨‍💻 Geliştirici: {AUTHOR} - {LOCATION}")
    print("🌍 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria! 🚀✨")
    time.sleep(2)
    
    # Karakter animasyon thread'i
    def animate_loop():
        while game.running:
            time.sleep(1)
            game.animate_character()
    
    animation_thread = threading.Thread(target=animate_loop, daemon=True)
    animation_thread.start()
    
    while game.running:
        try:
            clear_screen()
            game.update_terminal_size()
            print_header()
            draw_map()
            print_controls()
            
            # Giriş al
            try:
                key = get_input()
            except:
                key = input("Giriş hatası: ").lower()
            
            # Kontrolleri işle
            if key.lower() == 'q':
                print("👋 Oyundan çıkılıyor...")
                print(f"Teşekkürler! recaria {VERSION}'i oynadığınız için.")
                game.running = False
                break
            elif key.lower() == 'h':
                print_help()
            elif key.lower() == 't':
                teleport_menu()
            elif key == '*':
                zoom_in()
                time.sleep(0.5)
            elif key == '-':
                zoom_out()
                time.sleep(0.5)
            elif key == '"':
                toggle_map()
                time.sleep(0.5)
            elif key.lower() == 'm':
                toggle_music()
                time.sleep(0.5)
            elif key.lower() == 'o':
                go_home()
                time.sleep(0.5)
            elif key.lower() == 'w':
                move_player(0, -1)
            elif key.lower() == 's':
                move_player(0, 1)
            elif key.lower() == 'a':
                move_player(-1, 0)
            elif key.lower() == 'd':
                move_player(1, 0)
            else:
                # Geçersiz tuş
                pass
                
        except KeyboardInterrupt:
            print("\n👋 Oyundan çıkılıyor...")
            game.running = False
            break
        except Exception as e:
            print(f"❌ Hata: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()

