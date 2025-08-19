"""
Recaria - Universe Explorer Game
Created for unibosoft v042
"""

import os
import sys
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils.colors import Colors
from core.utils.logger import Logger
from core.database.manager import DatabaseManager


class RecariaMain:
    """Main class for Recaria universe explorer"""
    
    # Map dimensions
    MAP_WIDTH = 100
    MAP_HEIGHT = 100
    
    # Terrain types
    TERRAIN_TYPES = {
        '~': {'name': 'Su', 'color': 'BLUE', 'walkable': False, 'symbol': '~'},
        '^': {'name': 'Dağ', 'color': 'BRIGHT_BLACK', 'walkable': False, 'symbol': '^'},
        '#': {'name': 'Orman', 'color': 'GREEN', 'walkable': True, 'symbol': '#'},
        '.': {'name': 'Çayır', 'color': 'BRIGHT_GREEN', 'walkable': True, 'symbol': '.'},
        '*': {'name': 'Çöl', 'color': 'YELLOW', 'walkable': True, 'symbol': '*'},
        'o': {'name': 'Taş', 'color': 'BRIGHT_BLACK', 'walkable': False, 'symbol': 'o'},
        '=': {'name': 'Yol', 'color': 'BRIGHT_YELLOW', 'walkable': True, 'symbol': '='},
        '▓': {'name': 'Şehir', 'color': 'CYAN', 'walkable': True, 'symbol': '▓'}
    }
    
    def __init__(self):
        self.colors = Colors()
        self.logger = Logger("Recaria")
        self.db = DatabaseManager()
        self.running = True
        
        # Player stats
        self.player_x = 50
        self.player_y = 50
        self.player_health = 100
        self.player_energy = 100
        self.player_level = 1
        self.player_exp = 0
        self.player_gold = 0
        
        # Character animation
        self.characters = ['♂', '☺', '♠', '♦', '☻', '♥']
        self.current_char_index = 0
        self.animation_counter = 0
        
        # Vehicle/Transport options
        self.vehicles = {
            '1': {'name': 'yürüyerek', 'speed': 1, 'icon': '🚶'},
            '2': {'name': 'bisiklet', 'speed': 3, 'icon': '🚴'},
            '3': {'name': 'araba', 'speed': 10, 'icon': '🚗'},
            '4': {'name': 'uçak', 'speed': 100, 'icon': '✈️'},
            '5': {'name': 'starship', 'speed': 1000, 'icon': '🚀'},
            '6': {'name': 'ışınlanma', 'speed': 99999, 'icon': '⚡'}
        }
        self.current_vehicle = '1'
        
        # Real world location (Bodrum)
        self.real_lat = 37.0344
        self.real_lng = 27.4305
        
        # Game state
        self.game_mode = 'map'  # 'map' or 'teleport'
        self.view_range = 10  # How many tiles to show around player
        self.discovered_tiles = set()  # Tiles player has seen
        self.world_map = []
        
        # Initialize world
        self._generate_world()
        
        # Load or create user profile
        self.user = self._load_user_profile()
    
    def _load_user_profile(self) -> Dict:
        """Load or create user profile"""
        username = os.environ.get('USER', 'explorer')
        user = self.db.get_user(username)
        
        if not user:
            user_id = self.db.create_user(username, settings={
                "recaria": {
                    "total_distance": 0,
                    "locations_visited": 0,
                    "achievements": []
                }
            })
            user = self.db.get_user(username)
        
        return user
    
    def _generate_world(self):
        """Generate 100x100 world map"""
        self.world_map = []
        
        # Create base terrain
        for y in range(self.MAP_HEIGHT):
            row = []
            for x in range(self.MAP_WIDTH):
                # Generate terrain based on position
                rand = random.random()
                
                # Water near edges
                if x < 5 or x > 94 or y < 5 or y > 94:
                    terrain = '~'
                # Mountains
                elif rand < 0.05:
                    terrain = '^'
                # Forest
                elif rand < 0.20:
                    terrain = '#'
                # Desert in certain areas
                elif 30 < x < 70 and 30 < y < 70 and rand < 0.30:
                    terrain = '*'
                # Stone
                elif rand < 0.25:
                    terrain = 'o'
                # Default grassland
                else:
                    terrain = '.'
                
                row.append(terrain)
            self.world_map.append(row)
        
        # Add cities
        cities = [
            (25, 25, "Bodrum"), (75, 25, "İstanbul"), 
            (25, 75, "İzmir"), (75, 75, "Ankara"),
            (50, 50, "Bitez"), (40, 60, "Turgutreis")
        ]
        for cx, cy, name in cities:
            if 0 <= cx < self.MAP_WIDTH and 0 <= cy < self.MAP_HEIGHT:
                self.world_map[cy][cx] = '▓'
        
        # Add roads between cities
        self._add_roads()
        
        self.logger.info(f"Generated {self.MAP_WIDTH}x{self.MAP_HEIGHT} world map")
    
    def _add_roads(self):
        """Add roads connecting cities"""
        # Simple road from Bodrum to Bitez
        for x in range(25, 51):
            y = 25 + int((x - 25) * (50 - 25) / (50 - 25))
            if 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT:
                if self.world_map[y][x] in ['.', '#', '*']:
                    self.world_map[y][x] = '='
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display recaria header"""
        header = f"""
{self.colors.YELLOW}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ██████╗ ███████╗ ██████╗ █████╗ ██████╗ ██╗ █████╗            ║
║   ██╔══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗██║██╔══██╗           ║
║   ██████╔╝█████╗  ██║     ███████║██████╔╝██║███████║           ║
║   ██╔══██╗██╔══╝  ██║     ██╔══██║██╔══██╗██║██╔══██║           ║
║   ██║  ██║███████╗╚██████╗██║  ██║██║  ██║██║██║  ██║           ║
║   ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝           ║
║                                                                   ║
║              🥕  r u h u n u z u   y ü k l e y i n  🥕           ║
╚═══════════════════════════════════════════════════════════════════╝{self.colors.RESET}
        
{self.colors.YELLOW}🌍 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria! 🚀✨{self.colors.RESET}
        """
        print(header)
    
    def display_status(self):
        """Display current status"""
        print(f"\n{self.colors.GREEN}━━━ Durum ━━━{self.colors.RESET}")
        print(f"📍 Konum: [{self.player_x}, {self.player_y}] - {self._get_terrain_at(self.player_x, self.player_y)['name']}")
        print(f"❤️  Sağlık: {self._get_health_bar()} ⚡ Enerji: {self._get_energy_bar()}")
        print(f"⭐ Seviye: {self.player_level} (EXP: {self.player_exp}/100) 💰 Altın: {self.player_gold}")
        print(f"🗺️  Keşif: {len(self.discovered_tiles)}/{self.MAP_WIDTH * self.MAP_HEIGHT} karo")
    
    def _get_terrain_at(self, x: int, y: int) -> Dict:
        """Get terrain info at position"""
        if 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT:
            terrain_char = self.world_map[y][x]
            return self.TERRAIN_TYPES.get(terrain_char, self.TERRAIN_TYPES['.'])
        return self.TERRAIN_TYPES['.']
    
    def _get_health_bar(self) -> str:
        """Get health bar visualization"""
        bar_length = 10
        filled = int((self.player_health / 100) * bar_length)
        empty = bar_length - filled
        
        color = self.colors.GREEN
        if self.player_health < 30:
            color = self.colors.RED
        elif self.player_health < 60:
            color = self.colors.YELLOW
        
        return f"{color}{'█' * filled}{self.colors.DIM}{'░' * empty}{self.colors.RESET} {self.player_health}%"
    
    def _get_energy_bar(self) -> str:
        """Get energy bar visualization"""
        bar_length = 10
        filled = int((self.player_energy / 100) * bar_length)
        empty = bar_length - filled
        
        color = self.colors.GREEN
        if self.player_energy < 30:
            color = self.colors.RED
        elif self.player_energy < 60:
            color = self.colors.YELLOW
        
        return f"{color}{'█' * filled}{self.colors.DIM}{'░' * empty}{self.colors.RESET} {self.player_energy}%"
    
    def get_current_character(self) -> str:
        """Get current animated character"""
        return self.characters[self.current_char_index]
    
    def animate_character(self):
        """Animate character by cycling through symbols"""
        self.animation_counter += 1
        if self.animation_counter % 5 == 0:  # Change every 5 frames
            self.current_char_index = (self.current_char_index + 1) % len(self.characters)
    
    def get_real_world_coords(self) -> Tuple[float, float]:
        """Convert game position to real world coordinates"""
        # Map game coordinates to real world (Bodrum region)
        # Game world 100x100 maps to roughly 50km x 50km area around Bodrum
        lat_offset = (self.player_y - 50) * 0.005  # ~0.5km per tile
        lng_offset = (self.player_x - 50) * 0.006  # ~0.6km per tile
        
        real_lat = self.real_lat + lat_offset
        real_lng = self.real_lng + lng_offset
        
        return real_lat, real_lng
    
    def display_map(self):
        """Display the game map around player"""
        # Animate character
        self.animate_character()
        
        # Update discovered tiles
        for dy in range(-self.view_range, self.view_range + 1):
            for dx in range(-self.view_range, self.view_range + 1):
                tile_x = self.player_x + dx
                tile_y = self.player_y + dy
                if 0 <= tile_x < self.MAP_WIDTH and 0 <= tile_y < self.MAP_HEIGHT:
                    self.discovered_tiles.add((tile_x, tile_y))
        
        # Get real world coordinates
        real_lat, real_lng = self.get_real_world_coords()
        
        # Display enhanced header with real coordinates
        print(f"\n{self.colors.CYAN}╔═══════════════════════════════════════════════════════╗{self.colors.RESET}")
        print(f"{self.colors.CYAN}║{self.colors.RESET} 🌍 recaria - Evren Keşfi                             {self.colors.CYAN}║{self.colors.RESET}")
        print(f"{self.colors.CYAN}║{self.colors.RESET} Oyun Konumu: [{self.player_x:3}, {self.player_y:3}]                             {self.colors.CYAN}║{self.colors.RESET}")
        print(f"{self.colors.CYAN}║{self.colors.RESET} Gerçek Konum: {real_lat:.4f}°N, {real_lng:.4f}°E          {self.colors.CYAN}║{self.colors.RESET}")
        print(f"{self.colors.CYAN}║{self.colors.RESET} Araç: {self.vehicles[self.current_vehicle]['icon']} {self.vehicles[self.current_vehicle]['name']:<20}            {self.colors.CYAN}║{self.colors.RESET}")
        print(f"{self.colors.CYAN}╚═══════════════════════════════════════════════════════╝{self.colors.RESET}")
        
        # Display map with border
        print(f"\n{self.colors.DIM}┌{'─' * (self.view_range * 2 + 1)}┐{self.colors.RESET}")
        
        for dy in range(-self.view_range, self.view_range + 1):
            line = f"{self.colors.DIM}│{self.colors.RESET}"
            for dx in range(-self.view_range, self.view_range + 1):
                tile_x = self.player_x + dx
                tile_y = self.player_y + dy
                
                if dx == 0 and dy == 0:
                    # Player position with animated character
                    character = self.get_current_character()
                    line += f"{self.colors.RED}{character}{self.colors.RESET}"
                elif 0 <= tile_x < self.MAP_WIDTH and 0 <= tile_y < self.MAP_HEIGHT:
                    terrain_char = self.world_map[tile_y][tile_x]
                    terrain = self.TERRAIN_TYPES[terrain_char]
                    color = getattr(self.colors, terrain['color'])
                    
                    if (tile_x, tile_y) in self.discovered_tiles:
                        line += f"{color}{terrain['symbol']}{self.colors.RESET}"
                    else:
                        line += f"{self.colors.DIM}?{self.colors.RESET}"
                else:
                    # Out of bounds
                    line += " "
            line += f"{self.colors.DIM}│{self.colors.RESET}"
            print(line)
        
        print(f"{self.colors.DIM}└{'─' * (self.view_range * 2 + 1)}┘{self.colors.RESET}")
    
    def display_navigation_menu(self):
        """Display navigation menu"""
        if self.game_mode == 'map':
            print(f"\n{self.colors.GREEN}━━━ Hareket ━━━{self.colors.RESET}")
            print(f"{self.colors.BOLD}W/A/S/D{self.colors.RESET} → Hareket et")
            print(f"{self.colors.BOLD}+/-{self.colors.RESET} → Yakınlaştır/Uzaklaştır")
            print(f"{self.colors.BOLD}T{self.colors.RESET} → Işınlanma modu")
            print(f"{self.colors.BOLD}I{self.colors.RESET} → Envanter")
            print(f"{self.colors.BOLD}M{self.colors.RESET} → Büyük harita")
            print(f"{self.colors.BOLD}R{self.colors.RESET} → Dinlen")
            print(f"{self.colors.BOLD}H{self.colors.RESET} → Yardım")
            print(f"{self.colors.BOLD}0{self.colors.RESET} → Ana menüye dön")
        else:
            print(f"\n{self.colors.CYAN}━━━ Işınlanma Noktaları ━━━{self.colors.RESET}")
            print(f"{self.colors.BOLD}1{self.colors.RESET} → Bodrum [25, 25]")
            print(f"{self.colors.BOLD}2{self.colors.RESET} → İstanbul [75, 25]")
            print(f"{self.colors.BOLD}3{self.colors.RESET} → İzmir [25, 75]")
            print(f"{self.colors.BOLD}4{self.colors.RESET} → Ankara [75, 75]")
            print(f"{self.colors.BOLD}5{self.colors.RESET} → Bitez [50, 50]")
            print(f"{self.colors.BOLD}6{self.colors.RESET} → Turgutreis [40, 60]")
            print(f"{self.colors.BOLD}M{self.colors.RESET} → Harita moduna dön")
            print(f"{self.colors.BOLD}0{self.colors.RESET} → Ana menüye dön")
        
        print(f"\n{self.colors.DIM}Komut girin...{self.colors.RESET}")
    
    def handle_movement(self, direction: str):
        """Handle player movement"""
        new_x, new_y = self.player_x, self.player_y
        
        if direction.lower() == 'w':
            new_y -= 1
        elif direction.lower() == 's':
            new_y += 1
        elif direction.lower() == 'a':
            new_x -= 1
        elif direction.lower() == 'd':
            new_x += 1
        
        # Check bounds
        if 0 <= new_x < self.MAP_WIDTH and 0 <= new_y < self.MAP_HEIGHT:
            # Check if terrain is walkable
            terrain = self._get_terrain_at(new_x, new_y)
            if terrain['walkable']:
                # Move player
                self.player_x = new_x
                self.player_y = new_y
                self.player_energy = max(0, self.player_energy - 1)
                
                # Random encounters
                if random.random() < 0.1:
                    self._handle_encounter()
            else:
                print(f"\n{self.colors.RED}Bu yöne gidemezsiniz! ({terrain['name']}){self.colors.RESET}")
                time.sleep(1)
        else:
            print(f"\n{self.colors.RED}Harita sınırına ulaştınız!{self.colors.RESET}")
            time.sleep(1)
    
    def _handle_encounter(self):
        """Handle random encounters"""
        encounters = [
            ("Altın buldunuz!", lambda: setattr(self, 'player_gold', self.player_gold + random.randint(1, 10))),
            ("Enerji kristali!", lambda: setattr(self, 'player_energy', min(100, self.player_energy + 20))),
            ("Şifalı bitki!", lambda: setattr(self, 'player_health', min(100, self.player_health + 10))),
            ("Tuzak!", lambda: setattr(self, 'player_health', max(0, self.player_health - 10))),
            ("Deneyim kazandınız!", lambda: self._gain_exp(10))
        ]
        
        encounter_text, encounter_action = random.choice(encounters)
        print(f"\n{self.colors.YELLOW}⚡ {encounter_text}{self.colors.RESET}")
        encounter_action()
        time.sleep(1)
    
    def _gain_exp(self, amount: int):
        """Gain experience points"""
        self.player_exp += amount
        if self.player_exp >= 100:
            self.player_level += 1
            self.player_exp -= 100
            self.player_health = 100
            self.player_energy = 100
            print(f"{self.colors.GREEN}🎉 Seviye atladınız! Seviye {self.player_level}{self.colors.RESET}")
    
    def handle_teleport(self, destination_index: int):
        """Handle teleportation to destination"""
        cities = [
            (25, 25, "Bodrum"), (75, 25, "İstanbul"), 
            (25, 75, "İzmir"), (75, 75, "Ankara"),
            (50, 50, "Bitez"), (40, 60, "Turgutreis")
        ]
        
        if 1 <= destination_index <= len(cities):
            x, y, name = cities[destination_index - 1]
            if x == self.player_x and y == self.player_y:
                print(f"\n{self.colors.YELLOW}Zaten {name} konumundasınız!{self.colors.RESET}")
                time.sleep(1)
                return
        
            # Calculate energy cost
            distance = abs(x - self.player_x) + abs(y - self.player_y)
            energy_cost = min(50, distance // 2)
            
            if self.player_energy < energy_cost:
                print(f"\n{self.colors.RED}Yetersiz enerji! Gerekli: {energy_cost}, Mevcut: {self.player_energy}{self.colors.RESET}")
                time.sleep(2)
                return
            
            # Teleportation animation
            print(f"\n{self.colors.CYAN}Işınlanma başlatılıyor... {name}{self.colors.RESET}")
            for i in range(3):
                print(f"{'.' * (i + 1)}", end='\r')
                time.sleep(0.5)
            
            # Deduct energy and move
            self.player_energy -= energy_cost
            self.player_x = x
            self.player_y = y
            
            # Log activity
            self.db.log_activity("recaria", f"Teleported to {name}", self.user['id'])
            
            print(f"\n{self.colors.GREEN}✓ {name} konumuna ışınlandınız!{self.colors.RESET}")
            time.sleep(2)
        else:
            print(f"\n{self.colors.RED}Geçersiz hedef!{self.colors.RESET}")
            time.sleep(1)
    
    def handle_zoom(self, direction: str):
        """Handle map zoom"""
        if direction == '+':
            self.view_range = max(5, self.view_range - 2)
            print(f"\n{self.colors.GREEN}Yakınlaştırıldı!{self.colors.RESET}")
        elif direction == '-':
            self.view_range = min(20, self.view_range + 2)
            print(f"\n{self.colors.GREEN}Uzaklaştırıldı!{self.colors.RESET}")
        time.sleep(0.5)
    
    def handle_rest(self):
        """Handle resting"""
        print(f"\n{self.colors.CYAN}Dinleniyorsunuz...{self.colors.RESET}")
        time.sleep(1)
        
        self.player_health = min(100, self.player_health + 20)
        self.player_energy = min(100, self.player_energy + 30)
        
        print(f"{self.colors.GREEN}✓ Sağlık ve enerji yenilendi!{self.colors.RESET}")
        time.sleep(1)
    
    def handle_big_map(self):
        """Show big map view"""
        self.clear_screen()
        print(f"{self.colors.CYAN}🗺️  Büyük Harita (100x100){self.colors.RESET}")
        print("=" * 60)
        
        # Show mini map 20x20
        for y in range(0, 100, 5):
            line = ""
            for x in range(0, 100, 5):
                if abs(x - self.player_x) < 3 and abs(y - self.player_y) < 3:
                    line += f"{self.colors.YELLOW}@{self.colors.RESET}"
                elif self.world_map[y][x] == '▓':
                    line += f"{self.colors.CYAN}▓{self.colors.RESET}"
                elif self.world_map[y][x] == '~':
                    line += f"{self.colors.BLUE}~{self.colors.RESET}"
                elif self.world_map[y][x] == '^':
                    line += f"{self.colors.BRIGHT_BLACK}^{self.colors.RESET}"
                else:
                    line += f"{self.colors.DIM}.{self.colors.RESET}"
            print(line)
        
        print("\n" + "=" * 60)
        print(f"Konumunuz: [{self.player_x}, {self.player_y}]")
        print(f"Keşif: {len(self.discovered_tiles)}/{self.MAP_WIDTH * self.MAP_HEIGHT} karo")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_scan(self):
        """Scan current location"""
        print(f"\n{self.colors.CYAN}🔍 Tarama yapılıyor...{self.colors.RESET}")
        time.sleep(1)
        
        # Random discoveries
        discoveries = [
            "Gizemli bir sinyal algılandı!",
            "Yeni bir element keşfedildi!",
            "Eski bir medeniyet izi bulundu!",
            "Kuantum anomalisi tespit edildi!",
            "Yaşam belirtisi algılandı!"
        ]
        
        if random.random() > 0.5:
            discovery = random.choice(discoveries)
            print(f"{self.colors.GREEN}✨ {discovery}{self.colors.RESET}")
            self.quantum_charge = min(100, self.quantum_charge + 10)
            print(f"{self.colors.YELLOW}+10 Kuantum Yükü{self.colors.RESET}")
        else:
            print(f"{self.colors.DIM}Özel bir şey bulunamadı.{self.colors.RESET}")
        
        time.sleep(2)
    
    def handle_recharge(self):
        """Recharge energy"""
        if self.energy >= 100:
            print(f"\n{self.colors.YELLOW}Enerji zaten dolu!{self.colors.RESET}")
            time.sleep(1)
            return
        
        print(f"\n{self.colors.CYAN}⚡ Enerji dolduruluyor...{self.colors.RESET}")
        
        while self.energy < 100:
            self.energy = min(100, self.energy + 10)
            print(f"\r{self._get_energy_bar()}", end='')
            time.sleep(0.3)
        
        print(f"\n{self.colors.GREEN}✓ Enerji dolu!{self.colors.RESET}")
        time.sleep(1)
    
    def _check_achievements(self):
        """Check and award achievements"""
        achievements = []
        
        if len(self.visited_locations) >= 3:
            achievements.append("🏆 İlk Kaşif - 3 konum ziyaret edildi")
        
        if len(self.visited_locations) >= 5:
            achievements.append("🌟 Yıldız Gezgini - 5 konum ziyaret edildi")
        
        if any(loc['type'] == 'quantum' for loc in self.visited_locations):
            achievements.append("🌀 Kuantum Yolcusu - Merkez noktasına ulaşıldı")
        
        if len(self.visited_locations) == len(self.LAUNCH_POINTS):
            achievements.append("🎯 Evren Ustası - Tüm konumlar ziyaret edildi")
        
        # Update user settings
        current_achievements = self.user.get('settings', {}).get('recaria', {}).get('achievements', [])
        new_achievements = [a for a in achievements if a not in current_achievements]
        
        if new_achievements:
            for achievement in new_achievements:
                print(f"\n{self.colors.YELLOW}🎉 Yeni Başarı: {achievement}{self.colors.RESET}")
            
            # Update database
            settings = self.user.get('settings', {})
            settings['recaria']['achievements'] = achievements
            settings['recaria']['locations_visited'] = len(self.visited_locations)
            # Note: In real implementation, we'd update the user settings in DB
            
            time.sleep(2)
    
    def show_achievements(self):
        """Show achievements"""
        self.clear_screen()
        print(f"{self.colors.CYAN}🏆 Başarılar{self.colors.RESET}")
        print("=" * 50)
        
        achievements = self.user.get('settings', {}).get('recaria', {}).get('achievements', [])
        
        if achievements:
            for achievement in achievements:
                print(f"• {achievement}")
        else:
            print(f"{self.colors.DIM}Henüz başarı kazanılmadı.{self.colors.RESET}")
        
        print("\n" + "=" * 50)
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def show_help(self):
        """Show help"""
        self.clear_screen()
        print(f"{self.colors.CYAN}📖 Recaria Yardım{self.colors.RESET}")
        print("=" * 60)
        
        help_text = f"""
🎮 NASIL OYNANIR?
• 100x100 büyüklüğünde bir dünyayı keşfedin
• W/A/S/D tuşları ile hareket edin
• Şehirler arasında ışınlanın (T tuşu)
• Haritayı yakınlaştırıp uzaklaştırın (+/-)

🗺️ HARİTA SEMBOLLERİ
{self.colors.BLUE}~{self.colors.RESET} Su (geçilemez)
{self.colors.BRIGHT_BLACK}^{self.colors.RESET} Dağ (geçilemez)
{self.colors.GREEN}#{self.colors.RESET} Orman
{self.colors.BRIGHT_GREEN}.{self.colors.RESET} Çayır
{self.colors.YELLOW}*{self.colors.RESET} Çöl
{self.colors.BRIGHT_BLACK}o{self.colors.RESET} Taş (geçilemez)
{self.colors.BRIGHT_YELLOW}={self.colors.RESET} Yol
{self.colors.CYAN}▓{self.colors.RESET} Şehir
{self.colors.YELLOW}@{self.colors.RESET} Siz

⚡ KAYNAK YÖNETİMİ
• Sağlık: Tuzaklardan kaçının, şifalı bitkiler bulun
• Enerji: Her hareket 1 enerji harcar
• Dinlenme (R): Sağlık ve enerji yeniler

🏆 İLERLEME
• Altın toplayın
• Deneyim kazanarak seviye atlayın
• Tüm haritayı keşfedin
• Gizli hazineleri bulun
        """
        
        print(help_text)
        print("=" * 60)
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def run(self):
        """Main game loop"""
        self.clear_screen()
        self.display_header()
        
        # Log game start
        self.db.log_activity("recaria", "Game started", self.user['id'])
        
        while self.running:
            self.clear_screen()
            self.display_header()
            self.display_status()
            
            if self.game_mode == 'map':
                self.display_map()
            
            self.display_navigation_menu()
            
            try:
                # Get single key input
                if os.name == 'nt':  # Windows
                    import msvcrt
                    choice = msvcrt.getch().decode('utf-8', errors='ignore')
                else:  # Unix/Linux/MacOS
                    import termios, tty
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        choice = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                # Handle choice based on mode
                if self.game_mode == 'map':
                    if choice.lower() in 'wasd':
                        self.handle_movement(choice)
                    elif choice in '+-':
                        self.handle_zoom(choice)
                    elif choice.lower() == 't':
                        self.game_mode = 'teleport'
                    elif choice.lower() == 'm':
                        self.handle_big_map()
                    elif choice.lower() == 'r':
                        self.handle_rest()
                    elif choice.lower() == 'h':
                        self.show_help()
                    elif choice == '0':
                        self.running = False
                else:  # teleport mode
                    if choice in '123456':
                        self.handle_teleport(int(choice))
                        self.game_mode = 'map'
                    elif choice.lower() == 'm':
                        self.game_mode = 'map'
                    elif choice == '0':
                        self.running = False
                    
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self.logger.error(f"Game error: {e}")
                print(f"\n{self.colors.RED}Hata: {e}{self.colors.RESET}")
                time.sleep(2)
        
        # Log game end
        self.db.log_activity("recaria", "Game ended", self.user['id'])
        print(f"\n{self.colors.YELLOW}Recaria'dan çıkılıyor...{self.colors.RESET}")
        time.sleep(1)


if __name__ == "__main__":
    # Test run
    game = RecariaMain()
    game.run()