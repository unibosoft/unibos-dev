#!/usr/bin/env python3
"""
Birlikteyiz DOS-Style Game Interface
SSH Compatible Terminal Game Engine
"""

import os
import sys
import time
import random
import json
import threading
import select
import termios
import tty
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform color support
init()

class TerminalDetector:
    """Detect terminal capabilities and SSH session"""
    
    def __init__(self):
        self.is_ssh = self._detect_ssh()
        self.width, self.height = self._get_terminal_size()
        self.color_support = self._detect_color_support()
        self.utf8_support = self._detect_utf8_support()
        
    def _detect_ssh(self):
        """Detect if running in SSH session"""
        return bool(os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'))
    
    def _get_terminal_size(self):
        """Get terminal dimensions"""
        try:
            import shutil
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24
    
    def _detect_color_support(self):
        """Detect if terminal supports colors"""
        try:
            import subprocess
            result = subprocess.run(['tput', 'colors'], capture_output=True, text=True)
            return int(result.stdout.strip()) >= 8
        except:
            return True  # Assume color support
    
    def _detect_utf8_support(self):
        """Detect UTF-8 support for box drawing"""
        encoding = sys.stdout.encoding or 'ascii'
        return 'utf' in encoding.lower()

class DOSInterface:
    """DOS-style terminal interface for SSH compatibility"""
    
    def __init__(self):
        self.terminal = TerminalDetector()
        self.running = True
        self.current_screen = "main_menu"
        self.player_data = self._load_player_data()
        
        # Color scheme
        if self.terminal.color_support:
            self.colors = {
                'header': Fore.CYAN + Style.BRIGHT,
                'title': Fore.YELLOW + Style.BRIGHT,
                'text': Fore.WHITE,
                'highlight': Fore.GREEN + Style.BRIGHT,
                'warning': Fore.YELLOW,
                'error': Fore.RED + Style.BRIGHT,
                'success': Fore.GREEN,
                'dim': Fore.WHITE + Style.DIM,
                'reset': Style.RESET_ALL
            }
        else:
            # Fallback for terminals without color
            self.colors = {k: '' for k in ['header', 'title', 'text', 'highlight', 
                                         'warning', 'error', 'success', 'dim', 'reset']}
    
    def _load_player_data(self):
        """Load player data from local storage"""
        try:
            with open('/opt/birlikteyiz/data/player.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'name': 'octopus',
                'level': 1,
                'experience': 0,
                'health': 100,
                'energy': 100,
                'location': {'x': 0, 'y': 0},
                'inventory': [],
                'achievements': [],
                'last_login': datetime.now().isoformat()
            }
    
    def _save_player_data(self):
        """Save player data to local storage"""
        try:
            os.makedirs('/opt/birlikteyiz/data', exist_ok=True)
            with open('/opt/birlikteyiz/data/player.json', 'w') as f:
                json.dump(self.player_data, f, indent=2)
        except Exception as e:
            print(f"Error saving player data: {e}")
    
    def clear_screen(self):
        """Clear screen and show header"""
        os.system('clear')
        self._draw_header()
    
    def _draw_header(self):
        """Draw responsive header based on terminal width"""
        c = self.colors
        
        if self.terminal.width >= 80:
            # Full header for wide terminals
            print(f"{c['header']}╔{'═' * 78}╗{c['reset']}")
            print(f"{c['header']}║{c['title']}{'BIRLIKTEYIZ - EMERGENCY COMMUNICATION & LIFE RPG':^78}{c['header']}║{c['reset']}")
            print(f"{c['header']}║{c['dim']}{'SSH Compatible DOS Interface':^78}{c['header']}║{c['reset']}")
            print(f"{c['header']}╚{'═' * 78}╝{c['reset']}")
        elif self.terminal.width >= 60:
            # Medium header
            print(f"{c['header']}╔{'═' * 58}╗{c['reset']}")
            print(f"{c['header']}║{c['title']}{'BIRLIKTEYIZ':^58}{c['header']}║{c['reset']}")
            print(f"{c['header']}║{c['dim']}{'Emergency Communication':^58}{c['header']}║{c['reset']}")
            print(f"{c['header']}╚{'═' * 58}╝{c['reset']}")
        else:
            # Narrow header
            print(f"{c['header']}╔{'═' * (self.terminal.width - 2)}╗{c['reset']}")
            print(f"{c['header']}║{c['title']}{'BIRLIKTEYIZ':^{self.terminal.width - 2}}{c['header']}║{c['reset']}")
            print(f"{c['header']}╚{'═' * (self.terminal.width - 2)}╝{c['reset']}")
        
        # Show SSH session info
        if self.terminal.is_ssh:
            print(f"{c['dim']}SSH Session: {self.terminal.width}x{self.terminal.height} | "
                  f"Colors: {self.terminal.color_support}{c['reset']}")
        print()
    
    def _draw_box(self, width, height, title=""):
        """Draw a box with optional title"""
        c = self.colors
        
        # Adjust width to terminal
        if width > self.terminal.width - 4:
            width = self.terminal.width - 4
        
        # Top border
        if title:
            title_len = len(title)
            if title_len > width - 4:
                title = title[:width-7] + "..."
                title_len = len(title)
            padding = (width - title_len - 2) // 2
            print(f"{c['header']}┌{'─' * (width-2)}┐{c['reset']}")
            print(f"{c['header']}│{' ' * padding}{c['title']}{title}{' ' * (width - title_len - padding - 2)}{c['header']}│{c['reset']}")
            print(f"{c['header']}├{'─' * (width-2)}┤{c['reset']}")
        else:
            print(f"{c['header']}┌{'─' * (width-2)}┐{c['reset']}")
        
        # Content area
        for _ in range(height - 3 if title else height - 2):
            print(f"{c['header']}│{' ' * (width-2)}│{c['reset']}")
        
        # Bottom border
        print(f"{c['header']}└{'─' * (width-2)}┘{c['reset']}")
    
    def _get_key_input(self, timeout=None):
        """Get single key input with optional timeout (SSH compatible)"""
        if self.terminal.is_ssh and timeout:
            # For SSH with timeout, use select
            if select.select([sys.stdin], [], [], timeout)[0]:
                return sys.stdin.read(1)
            return None
        else:
            # Standard input
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                if timeout:
                    if select.select([sys.stdin], [], [], timeout)[0]:
                        return sys.stdin.read(1)
                    return None
                else:
                    return sys.stdin.read(1)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def show_main_menu(self):
        """Show main game menu"""
        self.clear_screen()
        c = self.colors
        
        # Player status
        print(f"{c['highlight']}Player: {self.player_data['name']} | "
              f"Level: {self.player_data['level']} | "
              f"Health: {self.player_data['health']}/100{c['reset']}")
        print()
        
        # ASCII art map (simplified for SSH)
        if self.terminal.width >= 60:
            self._show_ascii_map()
        else:
            print(f"{c['text']}[MAP VIEW - Terminal too narrow for full display]{c['reset']}")
        
        print()
        
        # Menu options
        print(f"{c['title']}═══ MAIN MENU ═══{c['reset']}")
        print(f"{c['text']}[1] Explore Area{c['reset']}")
        print(f"{c['text']}[2] Emergency Communications{c['reset']}")
        print(f"{c['text']}[3] Inventory & Trading{c['reset']}")
        print(f"{c['text']}[4] Network Status{c['reset']}")
        print(f"{c['text']}[5] Settings{c['reset']}")
        print(f"{c['text']}[Q] Quit{c['reset']}")
        print()
        
        # Status bar
        self._show_status_bar()
        
        print(f"{c['highlight']}Select option: {c['reset']}", end='', flush=True)
        
        key = self._get_key_input()
        if key:
            self._handle_menu_input(key.lower())
    
    def _show_ascii_map(self):
        """Show ASCII art map of the area"""
        c = self.colors
        
        # Simple ASCII map representation
        map_data = [
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "░░░░░░██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "░░░░░░██@@██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "░░░░░░██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
        ]
        
        # Add player position
        px, py = self.player_data['location']['x'], self.player_data['location']['y']
        
        print(f"{c['dim']}Current Area - Your Location: ({px}, {py}){c['reset']}")
        for i, line in enumerate(map_data):
            if i == py and 0 <= px < len(line):
                # Show player position
                line = line[:px] + f"{c['highlight']}@{c['reset']}" + line[px+1:]
            print(f"{c['success']}{line[:self.terminal.width-4]}{c['reset']}")
    
    def _show_status_bar(self):
        """Show status bar at bottom"""
        c = self.colors
        
        # Network status
        network_status = "LoRa: ON | WiFi: ON | Emergency: OFF"
        
        # Time
        current_time = datetime.now().strftime("%H:%M:%S")
        
        status_line = f"Status: {network_status} | Time: {current_time}"
        
        if len(status_line) > self.terminal.width:
            status_line = status_line[:self.terminal.width-3] + "..."
        
        print(f"{c['dim']}{status_line}{c['reset']}")
    
    def _handle_menu_input(self, key):
        """Handle menu input"""
        if key == '1':
            self.show_exploration_screen()
        elif key == '2':
            self.show_emergency_comms()
        elif key == '3':
            self.show_inventory()
        elif key == '4':
            self.show_network_status()
        elif key == '5':
            self.show_settings()
        elif key == 'q':
            self.quit_game()
        else:
            # Invalid input, show menu again
            self.show_main_menu()
    
    def show_exploration_screen(self):
        """Show exploration interface"""
        self.clear_screen()
        c = self.colors
        
        print(f"{c['title']}═══ EXPLORATION MODE ═══{c['reset']}")
        print()
        
        # Show larger map for exploration
        self._show_detailed_map()
        
        print()
        print(f"{c['text']}Movement: [W]Up [S]Down [A]Left [D]Right{c['reset']}")
        print(f"{c['text']}Actions: [E]Examine [I]Inventory [M]Main Menu{c['reset']}")
        print()
        
        # Random events
        if random.random() < 0.3:
            events = [
                "You found a useful item!",
                "You discovered a new location!",
                "You met another survivor!",
                "You found emergency supplies!"
            ]
            print(f"{c['highlight']}Event: {random.choice(events)}{c['reset']}")
            print()
        
        print(f"{c['highlight']}Action: {c['reset']}", end='', flush=True)
        
        key = self._get_key_input()
        if key:
            self._handle_exploration_input(key.lower())
    
    def _show_detailed_map(self):
        """Show detailed exploration map"""
        c = self.colors
        
        # More detailed ASCII map for exploration
        detailed_map = [
            "████████████████████████████████████████████████████████",
            "█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "█░██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "█░██@@██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "█░██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "████████████████████████████████████████████████████████",
        ]
        
        px, py = self.player_data['location']['x'], self.player_data['location']['y']
        
        for i, line in enumerate(detailed_map):
            if i == py and 0 <= px < len(line):
                line = line[:px] + f"{c['highlight']}@{c['reset']}" + line[px+1:]
            print(f"{c['success']}{line[:self.terminal.width-2]}{c['reset']}")
    
    def _handle_exploration_input(self, key):
        """Handle exploration input"""
        if key in ['w', 'a', 's', 'd']:
            self._move_player(key)
        elif key == 'e':
            self._examine_location()
        elif key == 'i':
            self.show_inventory()
        elif key == 'm':
            self.show_main_menu()
        else:
            self.show_exploration_screen()
    
    def _move_player(self, direction):
        """Move player in specified direction"""
        x, y = self.player_data['location']['x'], self.player_data['location']['y']
        
        if direction == 'w' and y > 1:
            y -= 1
        elif direction == 's' and y < 6:
            y += 1
        elif direction == 'a' and x > 1:
            x -= 1
        elif direction == 'd' and x < 55:
            x += 1
        
        self.player_data['location']['x'] = x
        self.player_data['location']['y'] = y
        self._save_player_data()
        
        self.show_exploration_screen()
    
    def _examine_location(self):
        """Examine current location"""
        self.clear_screen()
        c = self.colors
        
        print(f"{c['title']}═══ LOCATION EXAMINATION ═══{c['reset']}")
        print()
        
        x, y = self.player_data['location']['x'], self.player_data['location']['y']
        
        # Generate location description based on coordinates
        descriptions = [
            f"You are at coordinates ({x}, {y}). The area looks peaceful.",
            f"This location ({x}, {y}) has some interesting features.",
            f"You notice emergency supplies might be hidden here at ({x}, {y}).",
            f"This spot ({x}, {y}) would be good for setting up communications."
        ]
        
        print(f"{c['text']}{random.choice(descriptions)}{c['reset']}")
        print()
        
        # Random discoveries
        if random.random() < 0.4:
            items = ["Emergency Radio", "First Aid Kit", "Solar Charger", "Water Purifier"]
            found_item = random.choice(items)
            print(f"{c['highlight']}You found: {found_item}!{c['reset']}")
            self.player_data['inventory'].append(found_item)
            self._save_player_data()
            print()
        
        print(f"{c['dim']}Press any key to continue...{c['reset']}")
        self._get_key_input()
        self.show_exploration_screen()
    
    def show_emergency_comms(self):
        """Show emergency communications interface"""
        self.clear_screen()
        c = self.colors
        
        print(f"{c['title']}═══ EMERGENCY COMMUNICATIONS ═══{c['reset']}")
        print()
        
        print(f"{c['text']}[1] Send SOS Signal{c['reset']}")
        print(f"{c['text']}[2] Broadcast Message{c['reset']}")
        print(f"{c['text']}[3] Check Messages{c['reset']}")
        print(f"{c['text']}[4] Network Scan{c['reset']}")
        print(f"{c['text']}[M] Main Menu{c['reset']}")
        print()
        
        # Show recent emergency activity
        print(f"{c['warning']}Recent Emergency Activity:{c['reset']}")
        print(f"{c['dim']}• No active emergencies in your area{c['reset']}")
        print(f"{c['dim']}• 3 devices online in mesh network{c['reset']}")
        print(f"{c['dim']}• Last message: 15 minutes ago{c['reset']}")
        print()
        
        print(f"{c['highlight']}Select option: {c['reset']}", end='', flush=True)
        
        key = self._get_key_input()
        if key:
            if key.lower() == 'm':
                self.show_main_menu()
            else:
                # Handle emergency comm options
                self.show_emergency_comms()
    
    def show_inventory(self):
        """Show inventory and trading interface"""
        self.clear_screen()
        c = self.colors
        
        print(f"{c['title']}═══ INVENTORY & TRADING ═══{c['reset']}")
        print()
        
        print(f"{c['text']}Your Inventory:{c['reset']}")
        if self.player_data['inventory']:
            for i, item in enumerate(self.player_data['inventory'], 1):
                print(f"{c['highlight']}  {i}. {item}{c['reset']}")
        else:
            print(f"{c['dim']}  (Empty){c['reset']}")
        
        print()
        print(f"{c['text']}[T] Trade with nearby players{c['reset']}")
        print(f"{c['text']}[U] Use item{c['reset']}")
        print(f"{c['text']}[M] Main Menu{c['reset']}")
        print()
        
        print(f"{c['highlight']}Action: {c['reset']}", end='', flush=True)
        
        key = self._get_key_input()
        if key and key.lower() == 'm':
            self.show_main_menu()
        else:
            self.show_inventory()
    
    def show_network_status(self):
        """Show network status and connected devices"""
        self.clear_screen()
        c = self.colors
        
        print(f"{c['title']}═══ NETWORK STATUS ═══{c['reset']}")
        print()
        
        # Network information
        print(f"{c['success']}LoRa Network: ACTIVE{c['reset']}")
        print(f"{c['success']}WiFi: CONNECTED{c['reset']}")
        print(f"{c['text']}Signal Strength: -45 dBm{c['reset']}")
        print(f"{c['text']}Range: ~8.5 km{c['reset']}")
        print()
        
        print(f"{c['text']}Connected Devices:{c['reset']}")
        devices = [
            ("dolphin", "Pi Zero 2W", "2.3km", "-52 dBm"),
            ("eagle", "Pi 5", "5.1km", "-68 dBm"),
            ("mountain", "Pi Zero 2W", "Offline", "N/A")
        ]
        
        for name, model, distance, signal in devices:
            status_color = c['success'] if distance != "Offline" else c['error']
            print(f"{status_color}  • {name} ({model}) - {distance} - {signal}{c['reset']}")
        
        print()
        print(f"{c['dim']}Press any key to return to main menu...{c['reset']}")
        self._get_key_input()
        self.show_main_menu()
    
    def show_settings(self):
        """Show settings menu"""
        self.clear_screen()
        c = self.colors
        
        print(f"{c['title']}═══ SETTINGS ═══{c['reset']}")
        print()
        
        print(f"{c['text']}[1] Change Device Name{c['reset']}")
        print(f"{c['text']}[2] Network Settings{c['reset']}")
        print(f"{c['text']}[3] Emergency Contacts{c['reset']}")
        print(f"{c['text']}[4] System Information{c['reset']}")
        print(f"{c['text']}[M] Main Menu{c['reset']}")
        print()
        
        # System info
        print(f"{c['dim']}Current Device: {self.player_data['name']}{c['reset']}")
        print(f"{c['dim']}SSH Session: {self.terminal.is_ssh}{c['reset']}")
        print(f"{c['dim']}Terminal: {self.terminal.width}x{self.terminal.height}{c['reset']}")
        print()
        
        print(f"{c['highlight']}Select option: {c['reset']}", end='', flush=True)
        
        key = self._get_key_input()
        if key and key.lower() == 'm':
            self.show_main_menu()
        else:
            self.show_settings()
    
    def quit_game(self):
        """Quit the game"""
        self.clear_screen()
        c = self.colors
        
        print(f"{c['title']}═══ GOODBYE ═══{c['reset']}")
        print()
        print(f"{c['text']}Thank you for using Birlikteyiz!{c['reset']}")
        print(f"{c['text']}Emergency communication system remains active.{c['reset']}")
        print()
        print(f"{c['dim']}Your progress has been saved.{c['reset']}")
        
        self._save_player_data()
        self.running = False
        time.sleep(2)
    
    def run(self):
        """Main game loop"""
        try:
            while self.running:
                if self.current_screen == "main_menu":
                    self.show_main_menu()
                time.sleep(0.1)  # Prevent excessive CPU usage
        except KeyboardInterrupt:
            self.quit_game()
        except Exception as e:
            print(f"\nError: {e}")
            print("Game crashed. Emergency systems remain active.")

def main():
    """Main entry point"""
    try:
        game = DOSInterface()
        game.run()
    except Exception as e:
        print(f"Failed to start game interface: {e}")
        print("Emergency communication system is still running.")
        sys.exit(1)

if __name__ == "__main__":
    main()

