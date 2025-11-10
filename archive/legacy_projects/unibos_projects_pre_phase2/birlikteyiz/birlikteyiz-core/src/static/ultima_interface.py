#!/usr/bin/env python3
"""
Birlikteyiz - Ultima Online Inspired Interface for Raspberry Pi 5
Emergency Communication System with Classic 2D Isometric Design
"""

import pygame
import sys
import json
import time
import math
import threading
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors (Modern clean palette)
COLORS = {
    'primary_blue': (45, 85, 135),
    'dark_blue': (25, 45, 75),
    'light_blue': (65, 105, 155),
    'accent_blue': (85, 125, 175),
    'dark_gray': (35, 35, 35),
    'medium_gray': (55, 55, 55),
    'light_gray': (75, 75, 75),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'green': (60, 180, 60),
    'red': (200, 60, 60),
    'yellow': (220, 200, 60),
    'orange': (220, 140, 60),
    'transparent_dark': (25, 25, 25, 200),
    'transparent_blue': (45, 85, 135, 180),
    'border_light': (120, 120, 120),
    'border_dark': (40, 40, 40),
    'text_primary': (240, 240, 240),
    'text_secondary': (180, 180, 180),
    'text_accent': (100, 180, 255)
}

class GameState(Enum):
    MAIN_MENU = "main_menu"
    GAME_WORLD = "game_world"
    EMERGENCY_COMMS = "emergency_comms"
    INVENTORY = "inventory"
    SETTINGS = "settings"
    MAP_VIEW = "map_view"

@dataclass
class Player:
    name: str
    x: float
    y: float
    health: int
    max_health: int
    energy: int
    max_energy: int
    level: int
    experience: int
    inventory: List[str]
    equipment: Dict[str, str]

@dataclass
class Device:
    name: str
    x: float
    y: float
    device_type: str
    status: str
    signal_strength: int
    last_seen: datetime

class UltimaInterface:
    """Main interface class inspired by Ultima Online"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Birlikteyiz - Emergency Communication System")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.current_state = GameState.MAIN_MENU
        self.player = self._load_player_data()
        self.devices = self._load_device_data()
        
        # UI Elements
        self.fonts = self._load_fonts()
        self.panels = self._create_panels()
        
        # Map and world
        self.world_offset_x = 0
        self.world_offset_y = 0
        self.zoom_level = 1.0
        
        # Emergency system
        self.emergency_active = False
        self.emergency_messages = []
        self.lora_status = "ACTIVE"
        self.wifi_status = "CONNECTED"
        
        # Animation and effects
        self.animation_time = 0
        self.blink_timer = 0
        
    def _load_fonts(self):
        """Load fonts for the interface"""
        try:
            return {
                'small': pygame.font.Font(None, 16),
                'medium': pygame.font.Font(None, 20),
                'large': pygame.font.Font(None, 24),
                'title': pygame.font.Font(None, 32)
            }
        except:
            # Fallback to default font
            return {
                'small': pygame.font.Font(None, 16),
                'medium': pygame.font.Font(None, 20),
                'large': pygame.font.Font(None, 24),
                'title': pygame.font.Font(None, 32)
            }
    
    def _load_player_data(self):
        """Load player data from file or create default"""
        try:
            with open('/opt/birlikteyiz/data/player.json', 'r') as f:
                data = json.load(f)
                return Player(
                    name=data.get('name', 'octopus'),
                    x=data.get('x', 512),
                    y=data.get('y', 384),
                    health=data.get('health', 100),
                    max_health=data.get('max_health', 100),
                    energy=data.get('energy', 100),
                    max_energy=data.get('max_energy', 100),
                    level=data.get('level', 1),
                    experience=data.get('experience', 0),
                    inventory=data.get('inventory', []),
                    equipment=data.get('equipment', {})
                )
        except:
            return Player(
                name='octopus',
                x=512, y=384,
                health=100, max_health=100,
                energy=100, max_energy=100,
                level=1, experience=0,
                inventory=['Emergency Radio', 'First Aid Kit'],
                equipment={'weapon': 'Emergency Beacon', 'armor': 'Safety Vest'}
            )
    
    def _load_device_data(self):
        """Load nearby device data"""
        return [
            Device('dolphin', 450, 300, 'Pi Zero 2W', 'ONLINE', 85, datetime.now()),
            Device('eagle', 600, 500, 'Pi 5', 'ONLINE', 72, datetime.now()),
            Device('mountain', 300, 200, 'Pi Zero 2W', 'OFFLINE', 0, datetime.now())
        ]
    
    def _create_panels(self):
        """Create UI panel definitions"""
        return {
            'character': pygame.Rect(10, 10, 280, 400),
            'minimap': pygame.Rect(SCREEN_WIDTH - 210, 10, 200, 200),
            'inventory': pygame.Rect(SCREEN_WIDTH - 210, 220, 200, 300),
            'chat': pygame.Rect(10, SCREEN_HEIGHT - 150, 600, 140),
            'status_bar': pygame.Rect(10, SCREEN_HEIGHT - 200, 600, 40),
            'emergency_panel': pygame.Rect(300, 10, 400, 300)
        }
    
    def draw_panel_background(self, rect, alpha=200, panel_type="default"):
        """Draw a modern, clean panel background"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Main background - flat color, no gradients
        if panel_type == "primary":
            bg_color = (*COLORS['primary_blue'], alpha)
        elif panel_type == "dark":
            bg_color = (*COLORS['dark_gray'], alpha)
        else:
            bg_color = (*COLORS['transparent_dark'], alpha)
        
        pygame.draw.rect(panel_surface, bg_color, (0, 0, rect.width, rect.height))
        
        # Simple border - single line, no ornate decorations
        border_color = COLORS['border_light']
        pygame.draw.rect(panel_surface, border_color, (0, 0, rect.width, rect.height), 1)
        
        # Optional inner highlight for depth
        if panel_type == "primary":
            highlight_color = COLORS['accent_blue']
            pygame.draw.line(panel_surface, highlight_color, (1, 1), (rect.width-2, 1))
            pygame.draw.line(panel_surface, highlight_color, (1, 1), (1, rect.height-2))
        
        self.screen.blit(panel_surface, rect.topleft)
    
    def draw_character_panel(self):
        """Draw character information panel with modern design"""
        panel = self.panels['character']
        self.draw_panel_background(panel, panel_type="primary")
        
        # Title - clean, simple text
        title_text = self.fonts['large'].render(f"{self.player.name}", True, COLORS['text_primary'])
        title_rect = title_text.get_rect(centerx=panel.centerx, y=panel.y + 15)
        self.screen.blit(title_text, title_rect)
        
        # Character representation - simple, clean rectangle
        char_rect = pygame.Rect(panel.x + 30, panel.y + 50, 80, 120)
        pygame.draw.rect(self.screen, COLORS['accent_blue'], char_rect)
        pygame.draw.rect(self.screen, COLORS['border_light'], char_rect, 2)
        
        # Character status text
        status_text = self.fonts['medium'].render("Emergency Responder", True, COLORS['text_secondary'])
        status_rect = status_text.get_rect(centerx=char_rect.centerx, y=char_rect.bottom + 10)
        self.screen.blit(status_text, status_rect)
        
        # Stats section - clean layout
        stats_y = panel.y + 200
        
        # Health bar - modern flat design
        self.draw_modern_stat_bar(panel.x + 130, stats_y, 130, 18, 
                                 self.player.health, self.player.max_health, 
                                 COLORS['red'], "Health")
        
        # Energy bar
        self.draw_modern_stat_bar(panel.x + 130, stats_y + 30, 130, 18,
                                 self.player.energy, self.player.max_energy,
                                 COLORS['green'], "Energy")
        
        # Level and Experience - clean text layout
        level_text = self.fonts['medium'].render(f"Level: {self.player.level}", True, COLORS['text_primary'])
        self.screen.blit(level_text, (panel.x + 30, stats_y + 65))
        
        exp_text = self.fonts['small'].render(f"Experience: {self.player.experience}", True, COLORS['text_secondary'])
        self.screen.blit(exp_text, (panel.x + 30, stats_y + 85))
        
        # Equipment slots - modern grid
        self.draw_modern_equipment_slots(panel.x + 30, stats_y + 110)
    
    def draw_modern_stat_bar(self, x, y, width, height, current, maximum, color, label):
        """Draw a modern, flat stat bar"""
        # Background
        pygame.draw.rect(self.screen, COLORS['dark_gray'], (x, y, width, height))
        
        # Fill
        if maximum > 0:
            fill_width = int((current / maximum) * width)
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        
        # Border
        pygame.draw.rect(self.screen, COLORS['border_light'], (x, y, width, height), 1)
        
        # Text - clean, readable
        text = self.fonts['small'].render(f"{label}: {current}/{maximum}", True, COLORS['text_primary'])
        self.screen.blit(text, (x, y - 18))
    
    def draw_modern_equipment_slots(self, x, y):
        """Draw modern equipment slots"""
        slot_size = 36
        slot_spacing = 40
        slots = [
            ('weapon', 'Emergency Beacon'),
            ('armor', 'Safety Vest'),
            ('accessory', 'GPS Tracker')
        ]
        
        for i, (slot_type, item) in enumerate(slots):
            slot_x = x + (i % 3) * slot_spacing
            slot_y = y + (i // 3) * slot_spacing
            
            # Slot background - modern flat design
            pygame.draw.rect(self.screen, COLORS['medium_gray'], 
                           (slot_x, slot_y, slot_size, slot_size))
            pygame.draw.rect(self.screen, COLORS['border_light'], 
                           (slot_x, slot_y, slot_size, slot_size), 1)
            
            # Item representation - simple colored square
            if item:
                item_color = COLORS['green'] if slot_type == 'weapon' else COLORS['accent_blue']
                pygame.draw.rect(self.screen, item_color, 
                               (slot_x + 3, slot_y + 3, slot_size - 6, slot_size - 6))
                pygame.draw.rect(self.screen, COLORS['border_light'], 
                               (slot_x + 3, slot_y + 3, slot_size - 6, slot_size - 6), 1)
    
    def draw_minimap(self):
        """Draw circular minimap (Ultima Online style)"""
        panel = self.panels['minimap']
        center_x = panel.centerx
        center_y = panel.centery
        radius = 90
        
        # Background circle
        pygame.draw.circle(self.screen, COLORS['dark_gray'], (center_x, center_y), radius)
        pygame.draw.circle(self.screen, COLORS['gold'], (center_x, center_y), radius, 2)
        
        # Map content (simplified)
        # Draw terrain
        for i in range(-radius, radius, 10):
            for j in range(-radius, radius, 10):
                if i*i + j*j < radius*radius:
                    # Terrain color based on position
                    terrain_color = COLORS['green'] if (i + j) % 20 == 0 else COLORS['dark_gray']
                    pygame.draw.rect(self.screen, terrain_color, 
                                   (center_x + i, center_y + j, 8, 8))
        
        # Draw player position (center)
        pygame.draw.circle(self.screen, COLORS['yellow'], (center_x, center_y), 3)
        
        # Draw other devices
        for device in self.devices:
            if device.status == 'ONLINE':
                # Calculate relative position
                rel_x = int((device.x - self.player.x) * 0.1)
                rel_y = int((device.y - self.player.y) * 0.1)
                
                if rel_x*rel_x + rel_y*rel_y < radius*radius:
                    device_color = COLORS['green'] if device.device_type == 'Pi 5' else COLORS['blue']
                    pygame.draw.circle(self.screen, device_color, 
                                     (center_x + rel_x, center_y + rel_y), 2)
        
        # Compass directions
        compass_texts = [
            ('N', center_x, center_y - radius - 15),
            ('S', center_x, center_y + radius + 5),
            ('E', center_x + radius + 10, center_y),
            ('W', center_x - radius - 15, center_y)
        ]
        
        for text, x, y in compass_texts:
            compass_surface = self.fonts['small'].render(text, True, COLORS['gold'])
            text_rect = compass_surface.get_rect(center=(x, y))
            self.screen.blit(compass_surface, text_rect)
    
    def draw_inventory_panel(self):
        """Draw inventory/backpack panel"""
        panel = self.panels['inventory']
        self.draw_panel_background(panel)
        
        # Title
        title_text = self.fonts['medium'].render("Backpack", True, COLORS['gold'])
        title_rect = title_text.get_rect(centerx=panel.centerx, y=panel.y + 10)
        self.screen.blit(title_text, title_rect)
        
        # Inventory grid
        slot_size = 32
        slots_per_row = 5
        start_x = panel.x + 10
        start_y = panel.y + 35
        
        for i, item in enumerate(self.player.inventory[:20]):  # Max 20 items
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = start_x + col * (slot_size + 2)
            slot_y = start_y + row * (slot_size + 2)
            
            # Slot background
            pygame.draw.rect(self.screen, COLORS['dark_gray'], 
                           (slot_x, slot_y, slot_size, slot_size))
            pygame.draw.rect(self.screen, COLORS['gold'], 
                           (slot_x, slot_y, slot_size, slot_size), 1)
            
            # Item representation
            item_color = COLORS['red'] if 'Emergency' in item else COLORS['green']
            pygame.draw.rect(self.screen, item_color, 
                           (slot_x + 2, slot_y + 2, slot_size - 4, slot_size - 4))
        
        # Item list
        list_y = start_y + 140
        for i, item in enumerate(self.player.inventory[:8]):
            item_text = self.fonts['small'].render(item, True, COLORS['white'])
            self.screen.blit(item_text, (panel.x + 10, list_y + i * 16))
    
    def draw_emergency_panel(self):
        """Draw emergency communications panel"""
        if not self.emergency_active:
            return
            
        panel = self.panels['emergency_panel']
        self.draw_panel_background(panel, alpha=220)
        
        # Blinking title for emergency
        if self.blink_timer % 60 < 30:  # Blink every second
            title_color = COLORS['red']
        else:
            title_color = COLORS['yellow']
        
        title_text = self.fonts['large'].render("EMERGENCY ACTIVE", True, title_color)
        title_rect = title_text.get_rect(centerx=panel.centerx, y=panel.y + 10)
        self.screen.blit(title_text, title_rect)
        
        # Emergency options
        options = [
            "Send SOS Signal",
            "Broadcast Location",
            "Request Medical Aid",
            "Report Hazard",
            "Cancel Emergency"
        ]
        
        for i, option in enumerate(options):
            option_y = panel.y + 50 + i * 30
            option_color = COLORS['red'] if i == len(options) - 1 else COLORS['white']
            
            option_text = self.fonts['medium'].render(f"{i+1}. {option}", True, option_color)
            self.screen.blit(option_text, (panel.x + 20, option_y))
        
        # Status indicators
        status_y = panel.y + 220
        
        lora_color = COLORS['green'] if self.lora_status == 'ACTIVE' else COLORS['red']
        lora_text = self.fonts['small'].render(f"LoRa: {self.lora_status}", True, lora_color)
        self.screen.blit(lora_text, (panel.x + 20, status_y))
        
        wifi_color = COLORS['green'] if self.wifi_status == 'CONNECTED' else COLORS['red']
        wifi_text = self.fonts['small'].render(f"WiFi: {self.wifi_status}", True, wifi_color)
        self.screen.blit(wifi_text, (panel.x + 20, status_y + 20))
    
    def draw_status_bar(self):
        """Draw bottom status bar"""
        panel = self.panels['status_bar']
        self.draw_panel_background(panel, alpha=200)
        
        # Network status
        status_items = [
            f"LoRa: {self.lora_status}",
            f"WiFi: {self.wifi_status}",
            f"Devices: {len([d for d in self.devices if d.status == 'ONLINE'])}",
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        ]
        
        for i, item in enumerate(status_items):
            item_x = panel.x + 10 + i * 140
            item_color = COLORS['green'] if 'ACTIVE' in item or 'CONNECTED' in item else COLORS['white']
            
            item_text = self.fonts['small'].render(item, True, item_color)
            self.screen.blit(item_text, (item_x, panel.y + 12))
    
    def draw_chat_panel(self):
        """Draw chat/message panel"""
        panel = self.panels['chat']
        self.draw_panel_background(panel, alpha=150)
        
        # Title
        title_text = self.fonts['medium'].render("Communications", True, COLORS['gold'])
        self.screen.blit(title_text, (panel.x + 10, panel.y + 5))
        
        # Recent messages
        messages = [
            "[15:30] dolphin: System check - all OK",
            "[15:25] eagle: Weather update - storm approaching",
            "[15:20] mountain: Low battery warning",
            "[15:15] System: Network scan complete"
        ]
        
        for i, message in enumerate(messages[-5:]):  # Show last 5 messages
            msg_y = panel.y + 30 + i * 16
            msg_color = COLORS['yellow'] if 'System:' in message else COLORS['white']
            
            msg_text = self.fonts['small'].render(message, True, msg_color)
            self.screen.blit(msg_text, (panel.x + 10, msg_y))
        
        # Input area
        input_rect = pygame.Rect(panel.x + 10, panel.bottom - 25, panel.width - 20, 20)
        pygame.draw.rect(self.screen, COLORS['dark_gray'], input_rect)
        pygame.draw.rect(self.screen, COLORS['gold'], input_rect, 1)
        
        input_text = self.fonts['small'].render("Type message...", True, COLORS['light_gray'])
        self.screen.blit(input_text, (input_rect.x + 5, input_rect.y + 3))
    
    def draw_world_view(self):
        """Draw the main world view (isometric style)"""
        # Simple grid-based world for now
        tile_size = 32
        
        for x in range(0, SCREEN_WIDTH, tile_size):
            for y in range(0, SCREEN_HEIGHT, tile_size):
                # Checkerboard pattern
                if (x // tile_size + y // tile_size) % 2 == 0:
                    tile_color = COLORS['green']
                else:
                    tile_color = COLORS['dark_gray']
                
                pygame.draw.rect(self.screen, tile_color, (x, y, tile_size, tile_size))
                pygame.draw.rect(self.screen, COLORS['gray'], (x, y, tile_size, tile_size), 1)
        
        # Draw player
        player_rect = pygame.Rect(self.player.x - 16, self.player.y - 16, 32, 32)
        pygame.draw.ellipse(self.screen, COLORS['yellow'], player_rect)
        pygame.draw.ellipse(self.screen, COLORS['gold'], player_rect, 2)
        
        # Player name
        name_text = self.fonts['small'].render(self.player.name, True, COLORS['white'])
        name_rect = name_text.get_rect(centerx=self.player.x, y=self.player.y - 30)
        self.screen.blit(name_text, name_rect)
        
        # Draw other devices
        for device in self.devices:
            if device.status == 'ONLINE':
                device_color = COLORS['blue'] if device.device_type == 'Pi Zero 2W' else COLORS['green']
                device_rect = pygame.Rect(device.x - 12, device.y - 12, 24, 24)
                pygame.draw.ellipse(self.screen, device_color, device_rect)
                pygame.draw.ellipse(self.screen, COLORS['white'], device_rect, 1)
                
                # Device name
                device_text = self.fonts['small'].render(device.name, True, COLORS['white'])
                device_text_rect = device_text.get_rect(centerx=device.x, y=device.y - 25)
                self.screen.blit(device_text, device_text_rect)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.emergency_active:
                        self.emergency_active = False
                    else:
                        self.running = False
                
                elif event.key == pygame.K_e:
                    self.emergency_active = not self.emergency_active
                
                elif event.key == pygame.K_m:
                    self.current_state = GameState.MAP_VIEW
                
                elif event.key == pygame.K_i:
                    self.current_state = GameState.INVENTORY
                
                # Movement keys
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.player.y = max(50, self.player.y - 32)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.player.y = min(SCREEN_HEIGHT - 50, self.player.y + 32)
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.player.x = max(50, self.player.x - 32)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.player.x = min(SCREEN_WIDTH - 50, self.player.x + 32)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Handle UI clicks
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_mouse_click(mouse_pos)
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks on UI elements"""
        # Check if click is on emergency panel
        if self.emergency_active and self.panels['emergency_panel'].collidepoint(pos):
            # Handle emergency options
            pass
        
        # Check if click is on minimap
        elif self.panels['minimap'].collidepoint(pos):
            # Handle minimap navigation
            pass
    
    def update(self):
        """Update game state"""
        self.animation_time += 1
        self.blink_timer += 1
        
        # Update device status (simulate)
        if self.animation_time % 300 == 0:  # Every 5 seconds
            for device in self.devices:
                if device.name == 'mountain':
                    device.status = 'ONLINE' if device.status == 'OFFLINE' else 'OFFLINE'
    
    def render(self):
        """Main render function"""
        # Clear screen
        self.screen.fill(COLORS['black'])
        
        # Draw world view
        self.draw_world_view()
        
        # Draw UI panels
        self.draw_character_panel()
        self.draw_minimap()
        self.draw_inventory_panel()
        self.draw_status_bar()
        self.draw_chat_panel()
        
        # Draw emergency panel if active
        if self.emergency_active:
            self.draw_emergency_panel()
        
        # Draw help text
        help_text = self.fonts['small'].render("E: Emergency | WASD: Move | ESC: Exit", 
                                             True, COLORS['white'])
        self.screen.blit(help_text, (10, 10))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Starting Birlikteyiz Ultima-style Interface...")
        print("Controls:")
        print("  WASD / Arrow Keys: Move")
        print("  E: Toggle Emergency Panel")
        print("  ESC: Exit")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    try:
        interface = UltimaInterface()
        interface.run()
    except Exception as e:
        print(f"Error starting interface: {e}")
        print("Falling back to terminal interface...")
        # Fallback to DOS interface
        import subprocess
        subprocess.run(['/opt/birlikteyiz/venv/bin/python', 
                       '/opt/birlikteyiz/src/static/dos_game.py'])

if __name__ == "__main__":
    main()

