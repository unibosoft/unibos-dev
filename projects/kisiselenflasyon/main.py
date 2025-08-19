"""
Kişisel Enflasyon Hesaplayıcı
Created for unibosoft v042
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils.colors import Colors
from core.utils.logger import Logger
from core.database.database import get_db


class KisiselEnflasyonMain:
    """Personal inflation calculator main class"""
    
    def __init__(self):
        self.colors = Colors()
        self.logger = Logger("KisiselEnflasyon")
        self.db = get_db()
        self.running = True
        self.current_basket = []
        
        # Load or create user profile
        self.user = self._load_user_profile()
    
    def _load_user_profile(self) -> Dict:
        """Load or create user profile"""
        username = os.environ.get('USER', 'kullanici')
        
        # Check if user exists
        users = self.db.select('users', where={'username': username})
        
        if not users:
            # Create new user
            user_id = self.db.insert('users', {
                'username': username,
                'created_at': datetime.now().isoformat(),
                'settings': json.dumps({
                    "kisiselenflasyon": {
                        "basket": [],
                        "price_alerts": [],
                        "favorite_products": []
                    }
                })
            })
            user = {'id': user_id, 'username': username}
        else:
            user = users[0]
            if 'settings' in user and isinstance(user['settings'], str):
                user['settings'] = json.loads(user['settings'])
        
        return user
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display module header"""
        header = f"""
{self.colors.YELLOW}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  💰 KİŞİSEL ENFLASYON HESAPLAYICI 💰                             ║
║                                                                   ║
║  Gerçek enflasyonunuzu hesaplayın                                ║
╚═══════════════════════════════════════════════════════════════════╝{self.colors.RESET}
        """
        print(header)
    
    def display_menu(self):
        """Display main menu"""
        print(f"\n{self.colors.GREEN}━━━ Ana Menü ━━━{self.colors.RESET}")
        print(f"{self.colors.BOLD}1{self.colors.RESET} → 🛒 Ürün Ekle (Barkod/İsim)")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → 📊 Sepet Analizi")
        print(f"{self.colors.BOLD}3{self.colors.RESET} → 📈 Enflasyon Raporu")
        print(f"{self.colors.BOLD}4{self.colors.RESET} → 🔍 Ürün Ara")
        print(f"{self.colors.BOLD}5{self.colors.RESET} → ⭐ Favori Ürünler")
        print(f"{self.colors.BOLD}6{self.colors.RESET} → 🔔 Fiyat Alarmları")
        print(f"{self.colors.BOLD}7{self.colors.RESET} → 📋 Geçmiş Alışverişler")
        print(f"{self.colors.BOLD}8{self.colors.RESET} → ⚙️  Ayarlar")
        print(f"{self.colors.BOLD}9{self.colors.RESET} → ℹ️  Yardım")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → 🚪 Ana Menüye Dön")
        
        print(f"\n{self.colors.DIM}Seçiminizi yapın...{self.colors.RESET}")
    
    def handle_add_product(self):
        """Add product to basket"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}🛒 Ürün Ekleme{self.colors.RESET}")
        
        # Get input method
        print(f"\n{self.colors.BOLD}1{self.colors.RESET} → Barkod ile ekle")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → İsim ile ekle")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → Geri")
        
        choice = input(f"\n{self.colors.DIM}Seçim: {self.colors.RESET}")
        
        if choice == '1':
            self._add_by_barcode()
        elif choice == '2':
            self._add_by_name()
    
    def _add_by_barcode(self):
        """Add product by barcode"""
        barcode = input(f"\n{self.colors.YELLOW}Barkod: {self.colors.RESET}")
        
        if not barcode:
            return
        
        # Check if product exists
        products = self.db.select('products', where={'barcode': barcode})
        product = products[0] if products else None
        
        if not product:
            # New product
            print(f"\n{self.colors.YELLOW}Yeni ürün kaydı oluşturuluyor...{self.colors.RESET}")
            name = input(f"Ürün adı: ")
            brand = input(f"Marka (opsiyonel): ")
            category = input(f"Kategori (opsiyonel): ")
            unit = input(f"Birim (adet/kg/lt): ") or "adet"
            
            if name:
                product_id = self.db.insert('products', {
                    'barcode': barcode,
                    'name': name,
                    'brand': brand,
                    'category': category,
                    'unit': unit
                })
                product = {'id': product_id, 'barcode': barcode, 'name': name, 'brand': brand, 'category': category, 'unit': unit}
            else:
                print(f"{self.colors.RED}Ürün adı gerekli!{self.colors.RESET}")
                time.sleep(2)
                return
        
        # Get price
        try:
            price = float(input(f"\n{self.colors.YELLOW}Fiyat (TL): {self.colors.RESET}"))
            quantity = float(input(f"Miktar ({product['unit']}): ") or "1")
            store = input(f"Mağaza (opsiyonel): ")
            
            # Add to database
            self.db.insert('price_history', {
                'product_id': product['id'],
                'price': price,
                'store': store or 'Genel',
                'recorded_at': datetime.now().isoformat()
            })
            
            # Add to current basket
            self.current_basket.append({
                'product': product,
                'price': price,
                'quantity': quantity,
                'store': store,
                'date': datetime.now().isoformat()
            })
            
            print(f"\n{self.colors.GREEN}✓ {product['name']} sepete eklendi!{self.colors.RESET}")
            
            # Log activity
            self.db.insert("activity_logs", {"module": "kisiselenflasyon", "action": f"Added product: {product['name']}", "user_id": self.user['id'], "timestamp": datetime.now().isoformat()})
            
        except ValueError:
            print(f"{self.colors.RED}Geçersiz fiyat!{self.colors.RESET}")
        
        time.sleep(2)
    
    def _add_by_name(self):
        """Add product by name search"""
        query = input(f"\n{self.colors.YELLOW}Ürün adı: {self.colors.RESET}")
        
        if not query:
            return
        
        # Search products
        products = self.db.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? OR brand LIKE ? OR category LIKE ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        if not products:
            print(f"\n{self.colors.YELLOW}Ürün bulunamadı. Yeni ürün oluşturulsun mu?{self.colors.RESET}")
            if input(f"(E/h): ").lower() == 'e':
                barcode = input(f"Barkod (opsiyonel): ") or f"MANUAL_{int(time.time())}"
                brand = input(f"Marka (opsiyonel): ")
                category = input(f"Kategori (opsiyonel): ")
                unit = input(f"Birim (adet/kg/lt): ") or "adet"
                
                product_id = self.db.insert('products', {
                    'barcode': barcode,
                    'name': query,
                    'brand': brand,
                    'category': category,
                    'unit': unit
                })
                products = self.db.select('products', where={'barcode': barcode})
        
        if products:
            # Show search results
            print(f"\n{self.colors.CYAN}Bulunan Ürünler:{self.colors.RESET}")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product['name']} {self.colors.DIM}({product.get('brand', 'Markasız')}){self.colors.RESET}")
            
            try:
                selection = int(input(f"\nSeçim (1-{len(products)}): ")) - 1
                if 0 <= selection < len(products):
                    selected_product = products[selection]
                    
                    # Get price
                    price = float(input(f"\n{self.colors.YELLOW}Fiyat (TL): {self.colors.RESET}"))
                    quantity = float(input(f"Miktar ({selected_product['unit']}): ") or "1")
                    store = input(f"Mağaza (opsiyonel): ")
                    
                    # Add to database
                    self.db.insert('price_history', {
                        'product_id': selected_product['id'],
                        'price': price,
                        'store': store or 'Genel',
                        'recorded_at': datetime.now().isoformat()
                    })
                    
                    # Add to current basket
                    self.current_basket.append({
                        'product': selected_product,
                        'price': price,
                        'quantity': quantity,
                        'store': store,
                        'date': datetime.now().isoformat()
                    })
                    
                    print(f"\n{self.colors.GREEN}✓ {selected_product['name']} sepete eklendi!{self.colors.RESET}")
                    
            except (ValueError, IndexError):
                print(f"{self.colors.RED}Geçersiz seçim!{self.colors.RESET}")
        
        time.sleep(2)
    
    def handle_basket_analysis(self):
        """Analyze current basket"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📊 Sepet Analizi{self.colors.RESET}")
        
        if not self.current_basket:
            print(f"\n{self.colors.DIM}Sepet boş!{self.colors.RESET}")
            input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
            return
        
        # Calculate totals
        total = sum(item['price'] * item['quantity'] for item in self.current_basket)
        
        # Group by category
        categories = {}
        for item in self.current_basket:
            category = item['product'].get('category', 'Diğer')
            if category not in categories:
                categories[category] = {'count': 0, 'total': 0}
            categories[category]['count'] += item['quantity']
            categories[category]['total'] += item['price'] * item['quantity']
        
        # Display basket
        print(f"\n{self.colors.GREEN}Sepetinizdeki Ürünler:{self.colors.RESET}")
        print("=" * 60)
        
        for i, item in enumerate(self.current_basket, 1):
            product = item['product']
            subtotal = item['price'] * item['quantity']
            print(f"{i}. {product['name']:<30} {item['quantity']:>6.1f} {product['unit']:<5} "
                  f"{item['price']:>8.2f} TL = {subtotal:>10.2f} TL")
        
        print("=" * 60)
        print(f"{self.colors.BOLD}TOPLAM:{self.colors.RESET} {total:>51.2f} TL")
        
        # Category breakdown
        print(f"\n{self.colors.YELLOW}Kategori Dağılımı:{self.colors.RESET}")
        for category, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
            percentage = (data['total'] / total) * 100
            print(f"• {category:<20} {data['total']:>10.2f} TL ({percentage:>5.1f}%)")
        
        # Compare with previous shopping
        self._show_price_comparison()
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def _show_price_comparison(self):
        """Show price comparison with history"""
        print(f"\n{self.colors.CYAN}Fiyat Karşılaştırması:{self.colors.RESET}")
        
        for item in self.current_basket[:5]:  # Show top 5 items
            product = item['product']
            current_price = item['price']
            
            # Get price history
            history = self.db.execute("""
                SELECT * FROM price_history 
                WHERE product_id = ?
                ORDER BY recorded_at DESC
                LIMIT 10
            """, (product['id'],))
            
            if len(history) > 1:
                # Calculate average and change
                prices = [h['price'] for h in history[1:]]  # Exclude current
                avg_price = statistics.mean(prices)
                price_change = ((current_price - avg_price) / avg_price) * 100
                
                arrow = "↑" if price_change > 0 else "↓" if price_change < 0 else "→"
                color = self.colors.RED if price_change > 10 else self.colors.GREEN if price_change < -5 else self.colors.YELLOW
                
                print(f"• {product['name']:<25} {current_price:>8.2f} TL "
                      f"{color}{arrow} {abs(price_change):>5.1f}%{self.colors.RESET} "
                      f"(Ort: {avg_price:.2f} TL)")
    
    def handle_inflation_report(self):
        """Generate inflation report"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📈 Kişisel Enflasyon Raporu{self.colors.RESET}")
        
        # Get user's purchase history
        # In real implementation, we'd query user's historical purchases
        
        print(f"\n{self.colors.YELLOW}Dönem Seçin:{self.colors.RESET}")
        print(f"{self.colors.BOLD}1{self.colors.RESET} → Son 1 ay")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → Son 3 ay")
        print(f"{self.colors.BOLD}3{self.colors.RESET} → Son 6 ay")
        print(f"{self.colors.BOLD}4{self.colors.RESET} → Son 1 yıl")
        
        period_choice = input(f"\n{self.colors.DIM}Seçim: {self.colors.RESET}")
        
        days = {'1': 30, '2': 90, '3': 180, '4': 365}.get(period_choice, 30)
        
        # Mock data for demonstration
        inflation_data = self._calculate_inflation(days)
        
        # Display report
        print(f"\n{self.colors.GREEN}━━━ Enflasyon Özeti ━━━{self.colors.RESET}")
        print(f"Dönem: Son {days} gün")
        print(f"Kişisel Enflasyon: {self.colors.BOLD}{inflation_data['personal']:.1f}%{self.colors.RESET}")
        print(f"Resmi Enflasyon (TÜFE): {inflation_data['official']:.1f}%")
        print(f"Fark: {inflation_data['difference']:+.1f} puan")
        
        # Category breakdown
        print(f"\n{self.colors.YELLOW}Kategori Bazında Enflasyon:{self.colors.RESET}")
        for category, rate in inflation_data['categories'].items():
            color = self.colors.RED if rate > 50 else self.colors.YELLOW if rate > 20 else self.colors.GREEN
            print(f"• {category:<20} {color}{rate:>6.1f}%{self.colors.RESET}")
        
        # Most increased products
        print(f"\n{self.colors.RED}En Çok Artan Ürünler:{self.colors.RESET}")
        for product, increase in inflation_data['top_increases'][:5]:
            print(f"• {product:<30} +{increase:.1f}%")
        
        # Recommendations
        print(f"\n{self.colors.CYAN}Öneriler:{self.colors.RESET}")
        print("• Yüksek enflasyonlu kategorilerde alternatif ürünler deneyin")
        print("• Toplu alım yaparak tasarruf sağlayabilirsiniz")
        print("• Fiyat alarmları kurarak uygun fiyatları yakalayın")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def _calculate_inflation(self, days: int) -> Dict:
        """Calculate personal inflation (mock data for demo)"""
        import random
        
        # Mock data - in real implementation, calculate from price history
        personal_rate = random.uniform(45, 75)
        official_rate = random.uniform(40, 60)
        
        categories = {
            "Gıda": random.uniform(60, 90),
            "Temizlik": random.uniform(40, 70),
            "Kişisel Bakım": random.uniform(30, 60),
            "İçecek": random.uniform(50, 80),
            "Atıştırmalık": random.uniform(70, 100)
        }
        
        top_increases = [
            ("Ruffles Süper Boy 200gr", random.uniform(80, 120)),
            ("Coca Cola 1L", random.uniform(70, 100)),
            ("Ülker Çikolatalı Gofret", random.uniform(60, 90)),
            ("Fairy Sıvı Deterjan 650ml", random.uniform(50, 80)),
            ("Orkid Günlük Ped", random.uniform(40, 70))
        ]
        
        return {
            'personal': personal_rate,
            'official': official_rate,
            'difference': personal_rate - official_rate,
            'categories': categories,
            'top_increases': sorted(top_increases, key=lambda x: x[1], reverse=True)
        }
    
    def handle_search_product(self):
        """Search products"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}🔍 Ürün Arama{self.colors.RESET}")
        
        query = input(f"\n{self.colors.YELLOW}Arama terimi: {self.colors.RESET}")
        
        if not query:
            return
        
        products = self.db.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? OR brand LIKE ? OR category LIKE ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        if products:
            print(f"\n{self.colors.GREEN}Bulunan Ürünler ({len(products)} sonuç):{self.colors.RESET}")
            print("=" * 70)
            
            for product in products[:20]:  # Show max 20 results
                # Get latest price
                history = self.db.execute("""
                    SELECT * FROM price_history 
                    WHERE product_id = ?
                    ORDER BY recorded_at DESC
                    LIMIT 1
                """, (product['id'],))
                if history:
                    latest_price = history[0]['price']
                    price_str = f"{latest_price:.2f} TL"
                else:
                    price_str = "Fiyat bilgisi yok"
                
                print(f"• {product['name']:<35} {product.get('brand', 'Markasız'):<15} {price_str:>15}")
        else:
            print(f"\n{self.colors.YELLOW}Ürün bulunamadı.{self.colors.RESET}")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_favorites(self):
        """Manage favorite products"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}⭐ Favori Ürünler{self.colors.RESET}")
        
        # Mock favorites - in real implementation, load from user settings
        favorites = [
            {"name": "Ruffles Süper Boy 200gr", "avg_price": 45.90},
            {"name": "Coca Cola 1L", "avg_price": 22.50},
            {"name": "Ülker Çikolatalı Gofret", "avg_price": 8.75}
        ]
        
        if favorites:
            print(f"\n{self.colors.GREEN}Favorileriniz:{self.colors.RESET}")
            for i, fav in enumerate(favorites, 1):
                print(f"{i}. {fav['name']:<35} Ort. Fiyat: {fav['avg_price']:.2f} TL")
        else:
            print(f"\n{self.colors.DIM}Henüz favori ürün eklenmemiş.{self.colors.RESET}")
        
        print(f"\n{self.colors.BOLD}1{self.colors.RESET} → Favori ekle")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → Favori kaldır")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → Geri")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_price_alerts(self):
        """Manage price alerts"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}🔔 Fiyat Alarmları{self.colors.RESET}")
        
        # Mock alerts - in real implementation, load from user settings
        alerts = [
            {"product": "Ruffles Süper Boy 200gr", "target": 40.00, "current": 45.90},
            {"product": "Coca Cola 1L", "target": 20.00, "current": 22.50}
        ]
        
        if alerts:
            print(f"\n{self.colors.GREEN}Aktif Alarmlar:{self.colors.RESET}")
            for alert in alerts:
                status = "🔴" if alert['current'] > alert['target'] else "🟢"
                print(f"{status} {alert['product']:<30} "
                      f"Hedef: {alert['target']:.2f} TL, Mevcut: {alert['current']:.2f} TL")
        else:
            print(f"\n{self.colors.DIM}Henüz fiyat alarmı kurulmamış.{self.colors.RESET}")
        
        print(f"\n{self.colors.BOLD}1{self.colors.RESET} → Alarm ekle")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → Alarm kaldır")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → Geri")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def show_help(self):
        """Show help"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📖 Yardım{self.colors.RESET}")
        print("=" * 60)
        
        help_text = """
🛒 NASIL KULLANILIR?
• Barkod veya isim ile ürün ekleyin
• Sepetinizi analiz edin
• Kişisel enflasyonunuzu hesaplayın
• Fiyat değişimlerini takip edin

📊 ÖZELLİKLER
• Ürün fiyat geçmişi
• Kategori bazlı analiz
• Kişisel enflasyon hesaplama
• Fiyat alarmları
• Favori ürünler

💡 İPUÇLARI
• Düzenli alışveriş kayıtları tutun
• Fiyat alarmları ile tasarruf edin
• Alternatif ürünleri karşılaştırın
• Toplu alım fırsatlarını değerlendirin

🔒 GİZLİLİK
• Verileriniz yerel olarak saklanır
• KVKK uyumlu veri işleme
• Kişisel bilgiler paylaşılmaz
        """
        
        print(help_text)
        print("=" * 60)
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def run(self):
        """Main module loop"""
        self.clear_screen()
        self.display_header()
        
        # Log module start
        self.db.insert("activity_logs", {"module": "kisiselenflasyon", "action": "Module started", "user_id": self.user['id'], "timestamp": datetime.now().isoformat()})
        
        while self.running:
            self.clear_screen()
            self.display_header()
            
            # Show quick stats
            if self.current_basket:
                total = sum(item['price'] * item['quantity'] for item in self.current_basket)
                print(f"\n{self.colors.DIM}Sepet: {len(self.current_basket)} ürün, "
                      f"Toplam: {total:.2f} TL{self.colors.RESET}")
            
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
                    self.handle_add_product()
                elif choice == '2':
                    self.handle_basket_analysis()
                elif choice == '3':
                    self.handle_inflation_report()
                elif choice == '4':
                    self.handle_search_product()
                elif choice == '5':
                    self.handle_favorites()
                elif choice == '6':
                    self.handle_price_alerts()
                elif choice == '7':
                    print(f"\n{self.colors.YELLOW}Geçmiş alışverişler henüz uygulanmadı.{self.colors.RESET}")
                    time.sleep(2)
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
        self.db.insert("activity_logs", {"module": "kisiselenflasyon", "action": "Module ended", "user_id": self.user['id'], "timestamp": datetime.now().isoformat()})
        print(f"\n{self.colors.YELLOW}Kişisel Enflasyon modülünden çıkılıyor...{self.colors.RESET}")
        time.sleep(1)


if __name__ == "__main__":
    # Test run
    app = KisiselEnflasyonMain()
    app.run()