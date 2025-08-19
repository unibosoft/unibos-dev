"""
Birlikteyiz - Emergency Communication Network
Created for unibosoft v042
"""

import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils.colors import Colors
from core.utils.logger import Logger
from core.database.manager import DatabaseManager


class BirlikteyizMain:
    """Main class for emergency communication network"""
    
    # LoRa specifications
    LORA_SPECS = {
        'frequency': '868 MHz (EU) / 915 MHz (US)',
        'max_range': '15 km (açık alan)',
        'urban_range': '2-5 km',
        'data_rate': '0.3 - 50 kbps',
        'power': '14-20 dBm',
        'channels': 8
    }
    
    # Emergency types
    EMERGENCY_TYPES = {
        '1': {'name': 'Deprem', 'icon': '🏚️', 'priority': 'critical'},
        '2': {'name': 'Yangın', 'icon': '🔥', 'priority': 'critical'},
        '3': {'name': 'Sel', 'icon': '🌊', 'priority': 'high'},
        '4': {'name': 'Tıbbi Acil', 'icon': '🏥', 'priority': 'high'},
        '5': {'name': 'Kayıp Kişi', 'icon': '👤', 'priority': 'medium'},
        '6': {'name': 'Elektrik Kesintisi', 'icon': '⚡', 'priority': 'low'},
        '7': {'name': 'Su Kesintisi', 'icon': '💧', 'priority': 'low'},
        '8': {'name': 'Genel Yardım', 'icon': '🆘', 'priority': 'medium'}
    }
    
    def __init__(self):
        self.colors = Colors()
        self.logger = Logger("Birlikteyiz")
        self.db = DatabaseManager()
        self.running = True
        self.network_nodes = []
        self.messages = []
        self.lora_connected = False
        
        # Load or create user profile
        self.user = self._load_user_profile()
        
        # Initialize mock network
        self._initialize_network()
    
    def _load_user_profile(self) -> Dict:
        """Load or create user profile"""
        username = os.environ.get('USER', 'vatandas')
        user = self.db.get_user(username)
        
        if not user:
            user_id = self.db.create_user(username, settings={
                "birlikteyiz": {
                    "call_sign": f"BRK{random.randint(1000, 9999)}",
                    "location": {"lat": 37.0347, "lon": 27.3944},  # Bitez coordinates
                    "emergency_contacts": [],
                    "device_id": f"LORA_{int(time.time())}"
                }
            })
            user = self.db.get_user(username)
        
        return user
    
    def _initialize_network(self):
        """Initialize mock network nodes"""
        # Create some mock nodes in the area
        node_names = [
            "Bodrum Merkez", "Bitez Sahil", "Konacık", "Gümbet",
            "Turgutreis", "Yalıkavak", "Göltürkbükü", "Gündoğan"
        ]
        
        for i, name in enumerate(node_names):
            self.network_nodes.append({
                'id': f"NODE_{i+1:03d}",
                'name': name,
                'distance': random.uniform(0.5, 10),
                'signal': random.randint(50, 100),
                'active': random.choice([True, True, True, False]),  # 75% active
                'last_seen': datetime.now() - timedelta(minutes=random.randint(0, 60))
            })
        
        # Sort by distance
        self.network_nodes.sort(key=lambda x: x['distance'])
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display module header"""
        header = f"""
{self.colors.RED}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  📡 BİRLİKTEYİZ - ACİL DURUM İLETİŞİM AĞI 📡                     ║
║                                                                   ║
║  LoRa Mesh Network - Afet Anında Bağlantı                        ║
╚═══════════════════════════════════════════════════════════════════╝{self.colors.RESET}
        """
        print(header)
    
    def display_network_status(self):
        """Display network status"""
        user_settings = self.user.get('settings', {}).get('birlikteyiz', {})
        call_sign = user_settings.get('call_sign', 'UNKNOWN')
        
        print(f"\n{self.colors.GREEN}━━━ Ağ Durumu ━━━{self.colors.RESET}")
        print(f"📻 Çağrı İşareti: {self.colors.BOLD}{call_sign}{self.colors.RESET}")
        print(f"📡 LoRa Durumu: ", end='')
        
        if self.lora_connected:
            print(f"{self.colors.GREEN}● Bağlı{self.colors.RESET}")
        else:
            print(f"{self.colors.RED}● Bağlı Değil{self.colors.RESET} (Donanım bulunamadı)")
        
        active_nodes = sum(1 for node in self.network_nodes if node['active'])
        print(f"🌐 Aktif Düğümler: {active_nodes}/{len(self.network_nodes)}")
        print(f"📨 Mesaj Sayısı: {len(self.messages)}")
        
        # Show nearest nodes
        print(f"\n{self.colors.CYAN}En Yakın Düğümler:{self.colors.RESET}")
        for node in self.network_nodes[:3]:
            if node['active']:
                signal_icon = "🟢" if node['signal'] > 70 else "🟡" if node['signal'] > 40 else "🔴"
                print(f"{signal_icon} {node['name']:<15} {node['distance']:>5.1f} km "
                      f"(Sinyal: {node['signal']}%)")
    
    def display_menu(self):
        """Display main menu"""
        print(f"\n{self.colors.YELLOW}━━━ İşlemler ━━━{self.colors.RESET}")
        print(f"{self.colors.BOLD}1{self.colors.RESET} → 🆘 Acil Durum Bildir")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → 📨 Mesaj Gönder")
        print(f"{self.colors.BOLD}3{self.colors.RESET} → 📥 Gelen Mesajlar")
        print(f"{self.colors.BOLD}4{self.colors.RESET} → 🗺️  Harita Görünümü")
        print(f"{self.colors.BOLD}5{self.colors.RESET} → 🏚️ Son Depremler")
        print(f"{self.colors.BOLD}6{self.colors.RESET} → 👥 Acil Durum Kişileri")
        print(f"{self.colors.BOLD}7{self.colors.RESET} → 📡 Ağ Taraması")
        print(f"{self.colors.BOLD}8{self.colors.RESET} → ⚙️  Ayarlar")
        print(f"{self.colors.BOLD}9{self.colors.RESET} → ℹ️  Yardım")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → 🚪 Ana Menüye Dön")
        
        print(f"\n{self.colors.DIM}Seçiminizi yapın...{self.colors.RESET}")
    
    def handle_emergency_report(self):
        """Handle emergency reporting"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.RED}🆘 ACİL DURUM BİLDİRİMİ{self.colors.RESET}")
        
        print(f"\n{self.colors.YELLOW}Acil durum türünü seçin:{self.colors.RESET}")
        for key, etype in self.EMERGENCY_TYPES.items():
            print(f"{self.colors.BOLD}{key}{self.colors.RESET} → {etype['icon']} {etype['name']}")
        
        choice = input(f"\n{self.colors.DIM}Seçim: {self.colors.RESET}")
        
        if choice in self.EMERGENCY_TYPES:
            emergency = self.EMERGENCY_TYPES[choice]
            
            # Get additional info
            print(f"\n{self.colors.YELLOW}Konum bilgisi:{self.colors.RESET}")
            location = input(f"Adres/Açıklama: ")
            
            print(f"\n{self.colors.YELLOW}Ek bilgi (opsiyonel):{self.colors.RESET}")
            details = input(f"Detaylar: ")
            
            # Create emergency message
            user_settings = self.user.get('settings', {}).get('birlikteyiz', {})
            call_sign = user_settings.get('call_sign', 'UNKNOWN')
            
            message = {
                'id': f"EMRG_{int(time.time())}",
                'type': 'emergency',
                'sender': call_sign,
                'emergency_type': emergency['name'],
                'priority': emergency['priority'],
                'location': location,
                'details': details,
                'timestamp': datetime.now().isoformat(),
                'coordinates': user_settings.get('location', {})
            }
            
            # Broadcast emergency
            self._broadcast_message(message)
            
            print(f"\n{self.colors.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{self.colors.RESET}")
            print(f"{self.colors.BOLD}🚨 ACİL DURUM YAYINLANDI! 🚨{self.colors.RESET}")
            print(f"{self.colors.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{self.colors.RESET}")
            print(f"\nTür: {emergency['icon']} {emergency['name']}")
            print(f"Konum: {location}")
            print(f"Öncelik: {emergency['priority'].upper()}")
            print(f"Yayın ID: {message['id']}")
            
            # Log activity
            self.db.log_activity("birlikteyiz", f"Emergency broadcast: {emergency['name']}", self.user['id'])
            
            # Simulate responses
            time.sleep(2)
            print(f"\n{self.colors.GREEN}✓ 3 düğüm mesajı aldı{self.colors.RESET}")
            print(f"{self.colors.GREEN}✓ En yakın yardım ekibi bilgilendirildi{self.colors.RESET}")
            
        else:
            print(f"{self.colors.RED}Geçersiz seçim!{self.colors.RESET}")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_send_message(self):
        """Handle sending regular message"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📨 Mesaj Gönder{self.colors.RESET}")
        
        # Get message
        print(f"\n{self.colors.YELLOW}Mesajınız (max 160 karakter):{self.colors.RESET}")
        message_text = input()[:160]
        
        if not message_text:
            return
        
        # Create message
        user_settings = self.user.get('settings', {}).get('birlikteyiz', {})
        call_sign = user_settings.get('call_sign', 'UNKNOWN')
        
        message = {
            'id': f"MSG_{int(time.time())}",
            'type': 'regular',
            'sender': call_sign,
            'text': message_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast message
        self._broadcast_message(message)
        
        print(f"\n{self.colors.GREEN}✓ Mesaj gönderildi!{self.colors.RESET}")
        print(f"ID: {message['id']}")
        print(f"Alıcı düğümler: {sum(1 for n in self.network_nodes if n['active'])}")
        
        time.sleep(2)
    
    def _broadcast_message(self, message: Dict):
        """Broadcast message to network"""
        # Add to messages
        self.messages.append(message)
        
        # Simulate propagation delay
        time.sleep(0.5)
        
        # In real implementation, this would use LoRa hardware
        self.logger.info(f"Broadcasting message: {message['id']}")
    
    def handle_inbox(self):
        """Show received messages"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📥 Gelen Mesajlar{self.colors.RESET}")
        
        if not self.messages:
            print(f"\n{self.colors.DIM}Henüz mesaj yok.{self.colors.RESET}")
        else:
            # Show recent messages
            for msg in reversed(self.messages[-10:]):  # Last 10 messages
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
                
                if msg['type'] == 'emergency':
                    etype = msg['emergency_type']
                    icon = next(e['icon'] for e in self.EMERGENCY_TYPES.values() 
                               if e['name'] == etype)
                    print(f"\n{self.colors.RED}🚨 ACİL DURUM - {timestamp}{self.colors.RESET}")
                    print(f"Gönderen: {msg['sender']}")
                    print(f"Tür: {icon} {etype}")
                    print(f"Konum: {msg['location']}")
                    if msg.get('details'):
                        print(f"Detay: {msg['details']}")
                else:
                    print(f"\n{self.colors.GREEN}💬 MESAJ - {timestamp}{self.colors.RESET}")
                    print(f"Gönderen: {msg['sender']}")
                    print(f"Mesaj: {msg['text']}")
                
                print(f"{self.colors.DIM}ID: {msg['id']}{self.colors.RESET}")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_map_view(self):
        """Show map view"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}🗺️  Harita Görünümü - Bodrum{self.colors.RESET}")
        
        # Simple ASCII map of Bodrum
        map_art = """
                          Göltürkbükü
                               ●
                          /         \\
                    Yalıkavak      Gündoğan
                        ●              ●
                       /                \\
                 Gümüşlük            Türkbükü
                    ●                    ●
                   /                      \\
            Turgutreis    BODRUM       Torba
                ●          ★ ●            ●
                 \\        /   \\          /
                  Akyarlar   Bitez(YOU)
                      ●         ◉
                               /
                          Ortakent
                              ●
        """
        
        print(map_art)
        
        # Show legend
        print(f"\n{self.colors.YELLOW}Gösterim:{self.colors.RESET}")
        print("◉ Sizin konumunuz")
        print("★ Merkez")
        print("● Aktif düğümler")
        
        # Show active emergencies on map
        emergencies = [m for m in self.messages if m['type'] == 'emergency'][-3:]
        if emergencies:
            print(f"\n{self.colors.RED}Son Acil Durumlar:{self.colors.RESET}")
            for emrg in emergencies:
                print(f"🚨 {emrg['emergency_type']} - {emrg.get('location', 'Bilinmiyor')}")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_earthquakes(self):
        """Show recent earthquakes"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}🏚️ Son Depremler - Ege Bölgesi{self.colors.RESET}")
        
        # Mock earthquake data
        earthquakes = [
            {'mag': 3.2, 'location': 'Datça açıkları', 'depth': 12.5, 'time': '14:23', 'distance': 45},
            {'mag': 2.8, 'location': 'Kos adası', 'depth': 8.3, 'time': '12:17', 'distance': 28},
            {'mag': 4.1, 'location': 'Söke', 'depth': 15.7, 'time': '09:45', 'distance': 85},
            {'mag': 2.5, 'location': 'Bodrum körfezi', 'depth': 6.2, 'time': '07:32', 'distance': 12},
            {'mag': 3.7, 'location': 'Gökova körfezi', 'depth': 10.8, 'time': '03:21', 'distance': 35}
        ]
        
        print(f"\n{'Büyüklük':<10} {'Yer':<20} {'Derinlik':<10} {'Saat':<8} {'Uzaklık':<10}")
        print("=" * 65)
        
        for eq in earthquakes:
            # Color code by magnitude
            if eq['mag'] >= 4.0:
                color = self.colors.RED
            elif eq['mag'] >= 3.0:
                color = self.colors.YELLOW
            else:
                color = self.colors.GREEN
            
            print(f"{color}{eq['mag']:>8.1f}{self.colors.RESET}   "
                  f"{eq['location']:<20} {eq['depth']:>7.1f} km  "
                  f"{eq['time']:<8} {eq['distance']:>6} km")
        
        print(f"\n{self.colors.YELLOW}Deprem Güvenlik Hatırlatması:{self.colors.RESET}")
        print("• Çök - Kapan - Tutun")
        print("• Acil durum çantanızı hazır tutun")
        print("• Toplanma alanlarını bilin")
        print("• Birlikteyiz ağını aktif tutun")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_emergency_contacts(self):
        """Manage emergency contacts"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}👥 Acil Durum Kişileri{self.colors.RESET}")
        
        # Get contacts from database
        contacts = []
        try:
            # In real implementation, load from database
            cursor = self.db.get_connection()
            # Mock data for now
            contacts = [
                {'name': 'AFAD', 'phone': '122', 'type': 'Resmi'},
                {'name': 'İtfaiye', 'phone': '110', 'type': 'Resmi'},
                {'name': 'Ambulans', 'phone': '112', 'type': 'Resmi'},
                {'name': 'Bodrum Belediyesi', 'phone': '0252 313 1200', 'type': 'Resmi'}
            ]
        except:
            pass
        
        if contacts:
            print(f"\n{self.colors.GREEN}Kayıtlı Kişiler:{self.colors.RESET}")
            for i, contact in enumerate(contacts, 1):
                print(f"{i}. {contact['name']:<20} {contact['phone']:<15} ({contact['type']})")
        else:
            print(f"\n{self.colors.DIM}Henüz acil durum kişisi eklenmemiş.{self.colors.RESET}")
        
        print(f"\n{self.colors.BOLD}1{self.colors.RESET} → Kişi ekle")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → Kişi kaldır")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → Geri")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_network_scan(self):
        """Scan for network nodes"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📡 Ağ Taraması{self.colors.RESET}")
        
        print(f"\n{self.colors.YELLOW}LoRa ağı taranıyor...{self.colors.RESET}")
        
        # Simulate scanning animation
        for i in range(3):
            print(f"\rTaranıyor {'.' * (i + 1)}", end='', flush=True)
            time.sleep(0.5)
        
        print(f"\n\n{self.colors.GREEN}Bulunan Düğümler:{self.colors.RESET}")
        print(f"{'ID':<12} {'İsim':<20} {'Mesafe':<10} {'Sinyal':<10} {'Durum':<10}")
        print("=" * 65)
        
        # Update node status randomly
        for node in self.network_nodes:
            node['signal'] = random.randint(40, 100)
            node['active'] = random.choice([True, True, True, False])
            node['last_seen'] = datetime.now() - timedelta(minutes=random.randint(0, 30))
        
        # Display nodes
        for node in self.network_nodes:
            status = f"{self.colors.GREEN}Aktif{self.colors.RESET}" if node['active'] else f"{self.colors.RED}Pasif{self.colors.RESET}"
            signal_color = self.colors.GREEN if node['signal'] > 70 else self.colors.YELLOW if node['signal'] > 40 else self.colors.RED
            
            print(f"{node['id']:<12} {node['name']:<20} {node['distance']:>7.1f} km "
                  f"{signal_color}{node['signal']:>6}%{self.colors.RESET}   {status}")
        
        print(f"\n{self.colors.CYAN}Ağ İstatistikleri:{self.colors.RESET}")
        active_count = sum(1 for n in self.network_nodes if n['active'])
        avg_signal = sum(n['signal'] for n in self.network_nodes if n['active']) / max(active_count, 1)
        
        print(f"Toplam düğüm: {len(self.network_nodes)}")
        print(f"Aktif düğüm: {active_count}")
        print(f"Ortalama sinyal: {avg_signal:.1f}%")
        print(f"Kapsama alanı: ~{max(n['distance'] for n in self.network_nodes):.1f} km")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def show_help(self):
        """Show help"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📖 Yardım{self.colors.RESET}")
        print("=" * 60)
        
        help_text = """
📡 LORA MESH NETWORK
• LoRa: Long Range, düşük güç tüketimli radyo teknolojisi
• Mesh: Her cihaz hem alıcı hem verici, otomatik yönlendirme
• Menzil: Açık alanda 15km, şehirde 2-5km
• İnternet gerektirmez, tamamen bağımsız

🆘 ACİL DURUM KULLANIMI
• Acil durumda hemen '1' tuşuna basın
• Konumunuzu açık şekilde belirtin
• Kısa ve net mesajlar gönderin
• Pil tasarrufu için gereksiz mesaj göndermeyin

📻 ÇAĞRI İŞARETİ
• Sizin benzersiz kimliğiniz
• Mesajlarınızda otomatik eklenir
• Değiştirilemez, sistem tarafından atanır

⚡ ÖNEMLİ BİLGİLER
• Raspberry Pi + LoRa modülü gerekli
• 868 MHz (Avrupa) lisanssız kullanım
• Acil durumlar için tasarlanmıştır
• Normal zamanda test amaçlı kullanılabilir

🔋 PİL TASARRUFU
• Gereksiz tarama yapmayın
• Mesajları kısa tutun
• Acil olmayan mesajları sınırlayın
        """
        
        print(help_text)
        print("=" * 60)
        
        # Show LoRa specs
        print(f"\n{self.colors.YELLOW}LoRa Teknik Özellikler:{self.colors.RESET}")
        for key, value in self.LORA_SPECS.items():
            print(f"• {key}: {value}")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def run(self):
        """Main module loop"""
        self.clear_screen()
        self.display_header()
        
        # Check for LoRa hardware
        try:
            # In real implementation, check for LoRa module
            import RPi.GPIO as GPIO
            self.lora_connected = True
        except:
            self.lora_connected = False
            print(f"\n{self.colors.YELLOW}⚠️  LoRa donanımı bulunamadı. Demo modunda çalışıyor.{self.colors.RESET}")
            time.sleep(2)
        
        # Log module start
        self.db.log_activity("birlikteyiz", "Module started", self.user['id'])
        
        while self.running:
            self.clear_screen()
            self.display_header()
            self.display_network_status()
            self.display_menu()
            
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
                
                # Handle choice
                if choice == '1':
                    self.handle_emergency_report()
                elif choice == '2':
                    self.handle_send_message()
                elif choice == '3':
                    self.handle_inbox()
                elif choice == '4':
                    self.handle_map_view()
                elif choice == '5':
                    self.handle_earthquakes()
                elif choice == '6':
                    self.handle_emergency_contacts()
                elif choice == '7':
                    self.handle_network_scan()
                elif choice == '8':
                    print(f"\n{self.colors.YELLOW}Ayarlar henüz uygulanmadı.{self.colors.RESET}")
                    time.sleep(2)
                elif choice == '9':
                    self.show_help()
                elif choice == '0':
                    self.running = False
                    
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self.logger.error(f"Module error: {e}")
                print(f"\n{self.colors.RED}Hata: {e}{self.colors.RESET}")
                time.sleep(2)
        
        # Log module end
        self.db.log_activity("birlikteyiz", "Module ended", self.user['id'])
        print(f"\n{self.colors.YELLOW}Birlikteyiz modülünden çıkılıyor...{self.colors.RESET}")
        time.sleep(1)


if __name__ == "__main__":
    # Test run
    app = BirlikteyizMain()
    app.run()