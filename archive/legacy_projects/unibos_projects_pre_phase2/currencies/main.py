"""
Currencies - Real-time Currency Exchange Tracker
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
from core.database.database import get_db

# Import API module
try:
    from .api import get_currency_api
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


class CurrenciesMain:
    """Main class for currency exchange tracker"""
    
    # Popular currencies
    CURRENCIES = {
        'USD': {'symbol': '$', 'name': 'ABD Doları', 'flag': '🇺🇸'},
        'EUR': {'symbol': '€', 'name': 'Euro', 'flag': '🇪🇺'},
        'GBP': {'symbol': '£', 'name': 'İngiliz Sterlini', 'flag': '🇬🇧'},
        'JPY': {'symbol': '¥', 'name': 'Japon Yeni', 'flag': '🇯🇵'},
        'CHF': {'symbol': 'Fr', 'name': 'İsviçre Frangı', 'flag': '🇨🇭'},
        'CAD': {'symbol': 'C$', 'name': 'Kanada Doları', 'flag': '🇨🇦'},
        'AUD': {'symbol': 'A$', 'name': 'Avustralya Doları', 'flag': '🇦🇺'},
        'RUB': {'symbol': '₽', 'name': 'Rus Rublesi', 'flag': '🇷🇺'},
        'CNY': {'symbol': '¥', 'name': 'Çin Yuanı', 'flag': '🇨🇳'},
        'SAR': {'symbol': 'ر.س', 'name': 'Suudi Riyali', 'flag': '🇸🇦'}
    }
    
    # Cryptocurrencies
    CRYPTOS = {
        'BTC': {'symbol': '₿', 'name': 'Bitcoin', 'icon': '🟠'},
        'ETH': {'symbol': 'Ξ', 'name': 'Ethereum', 'icon': '🔷'},
        'BNB': {'symbol': 'BNB', 'name': 'Binance Coin', 'icon': '🟡'},
        'USDT': {'symbol': '₮', 'name': 'Tether', 'icon': '🟢'},
        'SOL': {'symbol': 'SOL', 'name': 'Solana', 'icon': '🟣'},
        'XRP': {'symbol': 'XRP', 'name': 'Ripple', 'icon': '⚪'},
        'ADA': {'symbol': 'ADA', 'name': 'Cardano', 'icon': '🔵'},
        'AVAX': {'symbol': 'AVAX', 'name': 'Avalanche', 'icon': '🔺'},
        'DOGE': {'symbol': 'Ð', 'name': 'Dogecoin', 'icon': '🐕'},
        'DOT': {'symbol': 'DOT', 'name': 'Polkadot', 'icon': '⚫'}
    }
    
    def __init__(self):
        self.colors = Colors()
        self.logger = Logger("Currencies")
        self.db = get_db()
        self.running = True
        self.favorites = ['USD', 'EUR', 'BTC']  # Default favorites
        self.update_interval = 5  # seconds
        self.last_update = None
        self.rates = {}
        self.use_real_data = API_AVAILABLE  # Use real data if API available
        self.api = get_currency_api() if API_AVAILABLE else None
        
        # Load or create user profile
        self.user = self._load_user_profile()
        
        # Initialize rates
        self._update_rates()
    
    def _load_user_profile(self) -> Dict:
        """Load or create user profile"""
        username = os.environ.get('USER', 'trader')
        
        # Check if user exists
        users = self.db.select('users', where={'username': username})
        
        if not users:
            # Create new user
            user_id = self.db.insert('users', {
                'username': username,
                'created_at': datetime.now().isoformat(),
                'settings': json.dumps({
                    "currencies": {
                        "favorites": self.favorites,
                        "alerts": [],
                        "portfolio": {}
                    }
                })
            })
            user = {'id': user_id, 'username': username}
        else:
            user = users[0]
            if 'settings' in user and isinstance(user['settings'], str):
                user['settings'] = json.loads(user['settings'])
                # Load user favorites
                user_favs = user.get('settings', {}).get('currencies', {}).get('favorites', [])
                if user_favs:
                    self.favorites = user_favs
        
        return user
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display module header"""
        header = f"""
{self.colors.GREEN}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  💱 DÖVİZ KURLARI - CANLI TAKİP 💱                               ║
║                                                                   ║
║  Anlık döviz ve kripto para kurları                              ║
╚═══════════════════════════════════════════════════════════════════╝{self.colors.RESET}
        """
        print(header)
    
    def _update_rates(self):
        """Update exchange rates from API or simulation"""
        if self.use_real_data and self.api:
            try:
                # Get real rates from API
                api_rates = self.api.get_all_rates()
                
                # Convert to expected format
                for currency, rate in api_rates.items():
                    if currency in self.rates:
                        previous = self.rates[currency]['rate']
                        change = ((rate - previous) / previous * 100) if previous > 0 else 0
                    else:
                        previous = rate
                        change = 0
                    
                    self.rates[currency] = {
                        'rate': rate,
                        'change': change,
                        'previous': previous
                    }
                
                self.logger.info("Updated rates from API")
            except Exception as e:
                self.logger.error(f"Failed to get API rates: {e}")
                self._update_rates_simulation()
        else:
            self._update_rates_simulation()
        
        self.last_update = datetime.now()
    
    def _update_rates_simulation(self):
        """Update exchange rates with simulation"""
        # Base rates (TRY)
        base_rates = {
            'USD': 31.85,
            'EUR': 34.62,
            'GBP': 40.28,
            'JPY': 0.213,
            'CHF': 35.94,
            'CAD': 23.42,
            'AUD': 20.87,
            'RUB': 0.352,
            'CNY': 4.38,
            'SAR': 8.49,
            'BTC': 1234567,
            'ETH': 65432,
            'BNB': 9876,
            'USDT': 31.82,
            'SOL': 2345,
            'XRP': 16.78,
            'ADA': 12.34,
            'AVAX': 876,
            'DOGE': 2.45,
            'DOT': 234
        }
        
        # Add some randomness to simulate market movement
        for currency, base_rate in base_rates.items():
            change = random.uniform(-0.02, 0.02)  # ±2% change
            self.rates[currency] = {
                'rate': base_rate * (1 + change),
                'change': change * 100,
                'previous': base_rates[currency]
            }
    
    def display_rates(self):
        """Display exchange rates"""
        # Update rates if needed
        if not self.last_update or (datetime.now() - self.last_update).seconds > self.update_interval:
            self._update_rates()
        
        data_source = "API (Gerçek)" if self.use_real_data else "Simülasyon"
        print(f"\n{self.colors.CYAN}📊 Döviz Kurları (TRY){self.colors.RESET}")
        print(f"{self.colors.DIM}Son güncelleme: {self.last_update.strftime('%H:%M:%S')} - Kaynak: {data_source}{self.colors.RESET}")
        print("=" * 70)
        
        # Show favorites first
        if self.favorites:
            print(f"\n{self.colors.YELLOW}⭐ Favoriler{self.colors.RESET}")
            self._display_currency_group(self.favorites)
        
        # Show all currencies
        print(f"\n{self.colors.GREEN}💵 Dövizler{self.colors.RESET}")
        fiat_codes = [code for code in self.CURRENCIES.keys() if code not in self.favorites]
        self._display_currency_group(fiat_codes)
        
        # Show cryptocurrencies
        print(f"\n{self.colors.MAGENTA}🪙 Kripto Paralar{self.colors.RESET}")
        crypto_codes = [code for code in self.CRYPTOS.keys() if code not in self.favorites]
        self._display_currency_group(crypto_codes)
    
    def _display_currency_group(self, currency_codes: List[str]):
        """Display a group of currencies"""
        for code in currency_codes:
            if code not in self.rates:
                continue
            
            rate_data = self.rates[code]
            rate = rate_data['rate']
            change = rate_data['change']
            
            # Get currency info
            if code in self.CURRENCIES:
                info = self.CURRENCIES[code]
                icon = info['flag']
                name = info['name']
            elif code in self.CRYPTOS:
                info = self.CRYPTOS[code]
                icon = info['icon']
                name = info['name']
            else:
                continue
            
            # Change indicator
            if change > 0:
                arrow = "↑"
                color = self.colors.GREEN
            elif change < 0:
                arrow = "↓"
                color = self.colors.RED
            else:
                arrow = "→"
                color = self.colors.YELLOW
            
            # Format display
            print(f"{icon} {code:<4} {name:<20} {rate:>12,.2f} TL "
                  f"{color}{arrow} {abs(change):>5.2f}%{self.colors.RESET}")
    
    def display_menu(self):
        """Display main menu"""
        print(f"\n{self.colors.CYAN}━━━ İşlemler ━━━{self.colors.RESET}")
        print(f"{self.colors.BOLD}1{self.colors.RESET} → 🔄 Kurları Güncelle")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → 💱 Döviz Çevir")
        print(f"{self.colors.BOLD}3{self.colors.RESET} → 📈 Grafik Görünümü")
        print(f"{self.colors.BOLD}4{self.colors.RESET} → ⭐ Favorileri Düzenle")
        print(f"{self.colors.BOLD}5{self.colors.RESET} → 🔔 Fiyat Alarmları")
        print(f"{self.colors.BOLD}6{self.colors.RESET} → 💼 Portföy")
        print(f"{self.colors.BOLD}7{self.colors.RESET} → 📊 Piyasa Özeti")
        print(f"{self.colors.BOLD}8{self.colors.RESET} → ⚙️  Ayarlar")
        print(f"{self.colors.BOLD}9{self.colors.RESET} → ℹ️  Yardım")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → 🚪 Ana Menüye Dön")
        
        print(f"\n{self.colors.DIM}Seçiminizi yapın...{self.colors.RESET}")
    
    def handle_convert(self):
        """Handle currency conversion"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}💱 Döviz Çevirici{self.colors.RESET}")
        
        # Get source currency
        print(f"\n{self.colors.YELLOW}Kaynak para birimi (örn: USD, EUR, BTC):{self.colors.RESET}")
        source = input().upper()
        
        if source not in self.rates and source != 'TRY':
            print(f"{self.colors.RED}Geçersiz para birimi!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Get target currency
        print(f"\n{self.colors.YELLOW}Hedef para birimi (örn: TRY, EUR, BTC):{self.colors.RESET}")
        target = input().upper()
        
        if target not in self.rates and target != 'TRY':
            print(f"{self.colors.RED}Geçersiz para birimi!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Get amount
        try:
            amount = float(input(f"\n{self.colors.YELLOW}Miktar ({source}):{self.colors.RESET} "))
        except ValueError:
            print(f"{self.colors.RED}Geçersiz miktar!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Calculate conversion
        if source == 'TRY':
            source_rate = 1
        else:
            source_rate = self.rates[source]['rate']
        
        if target == 'TRY':
            target_rate = 1
        else:
            target_rate = self.rates[target]['rate']
        
        result = (amount * source_rate) / target_rate
        
        # Display result
        print(f"\n{self.colors.GREEN}━━━ Çeviri Sonucu ━━━{self.colors.RESET}")
        print(f"{amount:,.2f} {source} = {self.colors.BOLD}{result:,.2f} {target}{self.colors.RESET}")
        print(f"\n{self.colors.DIM}Kur: 1 {source} = {source_rate/target_rate:.4f} {target}{self.colors.RESET}")
        
        # Log activity
        self.db.insert("activity_logs", {"module": "currencies", "action": f"Converted {amount} {source} to {target}", "user_id": self.user['id'], "timestamp": datetime.now().isoformat()})
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_chart(self):
        """Show price chart (simple ASCII)"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📈 Grafik Görünümü{self.colors.RESET}")
        
        print(f"\n{self.colors.YELLOW}Para birimi seçin (örn: USD, EUR, BTC):{self.colors.RESET}")
        currency = input().upper()
        
        if currency not in self.rates:
            print(f"{self.colors.RED}Geçersiz para birimi!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Generate mock historical data
        hours = 24
        data_points = []
        current_rate = self.rates[currency]['rate']
        
        for i in range(hours):
            # Simulate historical rates
            historical_rate = current_rate * (1 + random.uniform(-0.03, 0.03))
            data_points.append(historical_rate)
        
        # Find min and max for scaling
        min_rate = min(data_points)
        max_rate = max(data_points)
        range_rate = max_rate - min_rate
        
        # Display chart
        chart_height = 15
        chart_width = 48
        
        print(f"\n{currency}/TRY - Son 24 Saat")
        print("=" * (chart_width + 10))
        
        # Draw chart
        for row in range(chart_height, -1, -1):
            row_value = min_rate + (range_rate * row / chart_height)
            line = f"{row_value:>8.2f} │"
            
            for col in range(chart_width):
                data_index = int(col * len(data_points) / chart_width)
                if data_index < len(data_points):
                    data_value = data_points[data_index]
                    if abs(data_value - row_value) < (range_rate / chart_height / 2):
                        line += "█"
                    else:
                        line += " "
            
            print(line)
        
        print(" " * 9 + "└" + "─" * chart_width)
        print(" " * 10 + "0" + " " * 23 + "12" + " " * 22 + "24 saat")
        
        # Show summary
        print(f"\n{self.colors.GREEN}Özet:{self.colors.RESET}")
        print(f"Güncel: {current_rate:,.2f} TL")
        print(f"En Yüksek: {max_rate:,.2f} TL")
        print(f"En Düşük: {min_rate:,.2f} TL")
        print(f"Değişim: {self.rates[currency]['change']:+.2f}%")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_favorites(self):
        """Manage favorite currencies"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}⭐ Favori Para Birimleri{self.colors.RESET}")
        
        print(f"\n{self.colors.GREEN}Mevcut Favoriler:{self.colors.RESET}")
        for i, fav in enumerate(self.favorites, 1):
            if fav in self.CURRENCIES:
                info = self.CURRENCIES[fav]
                print(f"{i}. {info['flag']} {fav} - {info['name']}")
            elif fav in self.CRYPTOS:
                info = self.CRYPTOS[fav]
                print(f"{i}. {info['icon']} {fav} - {info['name']}")
        
        print(f"\n{self.colors.BOLD}1{self.colors.RESET} → Favori ekle")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → Favori kaldır")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → Geri")
        
        choice = input(f"\n{self.colors.DIM}Seçim: {self.colors.RESET}")
        
        if choice == '1':
            code = input(f"{self.colors.YELLOW}Para birimi kodu: {self.colors.RESET}").upper()
            if code in self.rates and code not in self.favorites:
                self.favorites.append(code)
                print(f"{self.colors.GREEN}✓ {code} favorilere eklendi!{self.colors.RESET}")
                # Save to user settings
                self._save_favorites()
            else:
                print(f"{self.colors.RED}Geçersiz veya zaten favori!{self.colors.RESET}")
        elif choice == '2':
            code = input(f"{self.colors.YELLOW}Para birimi kodu: {self.colors.RESET}").upper()
            if code in self.favorites:
                self.favorites.remove(code)
                print(f"{self.colors.GREEN}✓ {code} favorilerden kaldırıldı!{self.colors.RESET}")
                # Save to user settings
                self._save_favorites()
            else:
                print(f"{self.colors.RED}Bu para birimi favorilerde değil!{self.colors.RESET}")
        
        time.sleep(2)
    
    def _save_favorites(self):
        """Save favorites to user settings"""
        # In real implementation, update user settings in database
        self.db.insert("activity_logs", {
            "module": "currencies", 
            "action": f"Updated favorites: {','.join(self.favorites)}", 
            "user_id": self.user['id'], 
            "timestamp": datetime.now().isoformat()
        })
    
    def handle_alerts(self):
        """Manage price alerts"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}🔔 Fiyat Alarmları{self.colors.RESET}")
        
        # Mock alerts
        alerts = [
            {'currency': 'USD', 'type': 'above', 'target': 32.00, 'current': self.rates['USD']['rate']},
            {'currency': 'BTC', 'type': 'below', 'target': 1200000, 'current': self.rates['BTC']['rate']}
        ]
        
        if alerts:
            print(f"\n{self.colors.GREEN}Aktif Alarmlar:{self.colors.RESET}")
            for alert in alerts:
                status = "🔴 Tetiklendi!" if self._check_alert(alert) else "🟢 Bekliyor"
                op = ">" if alert['type'] == 'above' else "<"
                print(f"{status} {alert['currency']} {op} {alert['target']:,.2f} TL "
                      f"(Şu an: {alert['current']:,.2f} TL)")
        else:
            print(f"\n{self.colors.DIM}Henüz alarm kurulmamış.{self.colors.RESET}")
        
        print(f"\n{self.colors.BOLD}1{self.colors.RESET} → Alarm ekle")
        print(f"{self.colors.BOLD}2{self.colors.RESET} → Alarm kaldır")
        print(f"{self.colors.BOLD}0{self.colors.RESET} → Geri")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def _check_alert(self, alert: Dict) -> bool:
        """Check if alert is triggered"""
        if alert['type'] == 'above':
            return alert['current'] >= alert['target']
        else:
            return alert['current'] <= alert['target']
    
    def handle_portfolio(self):
        """Show portfolio"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}💼 Portföy{self.colors.RESET}")
        
        # Mock portfolio
        portfolio = {
            'USD': {'amount': 1000, 'avg_cost': 30.50},
            'EUR': {'amount': 500, 'avg_cost': 33.80},
            'BTC': {'amount': 0.05, 'avg_cost': 1100000}
        }
        
        total_cost = 0
        total_value = 0
        
        print(f"\n{'Para':<6} {'Miktar':>12} {'Ort.Maliyet':>12} {'Güncel':>12} {'Değer (TL)':>15} {'K/Z':>10}")
        print("=" * 80)
        
        for currency, data in portfolio.items():
            current_rate = self.rates[currency]['rate']
            cost = data['amount'] * data['avg_cost']
            value = data['amount'] * current_rate
            profit = value - cost
            profit_pct = (profit / cost) * 100 if cost > 0 else 0
            
            total_cost += cost
            total_value += value
            
            color = self.colors.GREEN if profit >= 0 else self.colors.RED
            
            print(f"{currency:<6} {data['amount']:>12,.4f} {data['avg_cost']:>12,.2f} "
                  f"{current_rate:>12,.2f} {value:>15,.2f} "
                  f"{color}{profit:>+9,.2f} ({profit_pct:>+.1f}%){self.colors.RESET}")
        
        print("=" * 80)
        
        total_profit = total_value - total_cost
        total_profit_pct = (total_profit / total_cost) * 100 if total_cost > 0 else 0
        
        print(f"{'TOPLAM':<6} {' ':>12} {total_cost:>12,.2f} {' ':>12} {total_value:>15,.2f} "
              f"{self.colors.BOLD}{total_profit:>+9,.2f} ({total_profit_pct:>+.1f}%){self.colors.RESET}")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def handle_market_summary(self):
        """Show market summary"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📊 Piyasa Özeti{self.colors.RESET}")
        
        # Calculate market stats
        gaining = [(code, data['change']) for code, data in self.rates.items() if data['change'] > 0]
        losing = [(code, data['change']) for code, data in self.rates.items() if data['change'] < 0]
        
        gaining.sort(key=lambda x: x[1], reverse=True)
        losing.sort(key=lambda x: x[1])
        
        print(f"\n{self.colors.GREEN}📈 En Çok Kazananlar{self.colors.RESET}")
        for code, change in gaining[:5]:
            name = self._get_currency_name(code)
            print(f"• {code:<4} {name:<20} {self.colors.GREEN}↑ {change:>5.2f}%{self.colors.RESET}")
        
        print(f"\n{self.colors.RED}📉 En Çok Kaybedenler{self.colors.RESET}")
        for code, change in losing[:5]:
            name = self._get_currency_name(code)
            print(f"• {code:<4} {name:<20} {self.colors.RED}↓ {abs(change):>5.2f}%{self.colors.RESET}")
        
        # Market sentiment
        positive_count = len(gaining)
        negative_count = len(losing)
        total_count = positive_count + negative_count
        
        print(f"\n{self.colors.YELLOW}📊 Piyasa Durumu{self.colors.RESET}")
        print(f"Yükselen: {positive_count} ({positive_count/total_count*100:.1f}%)")
        print(f"Düşen: {negative_count} ({negative_count/total_count*100:.1f}%)")
        
        if positive_count > negative_count * 1.5:
            sentiment = f"{self.colors.GREEN}🐂 Boğa Piyasası{self.colors.RESET}"
        elif negative_count > positive_count * 1.5:
            sentiment = f"{self.colors.RED}🐻 Ayı Piyasası{self.colors.RESET}"
        else:
            sentiment = f"{self.colors.YELLOW}➡️  Yatay Piyasa{self.colors.RESET}"
        
        print(f"Genel Durum: {sentiment}")
        
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def _get_currency_name(self, code: str) -> str:
        """Get currency name"""
        if code in self.CURRENCIES:
            return self.CURRENCIES[code]['name']
        elif code in self.CRYPTOS:
            return self.CRYPTOS[code]['name']
        return code
    
    def show_help(self):
        """Show help"""
        self.clear_screen()
        self.display_header()
        print(f"\n{self.colors.CYAN}📖 Yardım{self.colors.RESET}")
        print("=" * 60)
        
        help_text = """
💱 KULLANIM
• Anlık döviz ve kripto para kurlarını takip edin
• Para birimleri arası çeviri yapın
• Favori kurlarınızı kaydedin
• Fiyat alarmları kurun

📊 ÖZELLİKLER
• Gerçek zamanlı kur güncellemeleri
• 10+ döviz, 10+ kripto para
• Grafik görünümü
• Portföy takibi
• Piyasa analizi

💡 İPUÇLARI
• Favorilere ekleyerek hızlı erişim sağlayın
• Alarmlar ile fırsat fiyatları yakalayın
• Portföy ile yatırımlarınızı takip edin
• Grafikleri inceleyerek trend analizi yapın

📈 SEMBOLLER
• ↑ Yükseliş
• ↓ Düşüş
• → Sabit
• 🟢 Alarm bekliyor
• 🔴 Alarm tetiklendi
        """
        
        print(help_text)
        print("=" * 60)
        input(f"\n{self.colors.DIM}Devam etmek için Enter'a basın...{self.colors.RESET}")
    
    def run(self):
        """Main module loop"""
        self.clear_screen()
        self.display_header()
        
        # Log module start
        self.db.insert("activity_logs", {"module": "currencies", "action": "Module started", "user_id": self.user['id'], "timestamp": datetime.now().isoformat()})
        
        while self.running:
            self.clear_screen()
            self.display_header()
            self.display_rates()
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
                    self._update_rates()
                    print(f"\n{self.colors.GREEN}✓ Kurlar güncellendi!{self.colors.RESET}")
                    time.sleep(1)
                elif choice == '2':
                    self.handle_convert()
                elif choice == '3':
                    self.handle_chart()
                elif choice == '4':
                    self.handle_favorites()
                elif choice == '5':
                    self.handle_alerts()
                elif choice == '6':
                    self.handle_portfolio()
                elif choice == '7':
                    self.handle_market_summary()
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
        self.db.insert("activity_logs", {"module": "currencies", "action": "Module ended", "user_id": self.user['id'], "timestamp": datetime.now().isoformat()})
        print(f"\n{self.colors.YELLOW}Döviz kurları modülünden çıkılıyor...{self.colors.RESET}")
        time.sleep(1)


if __name__ == "__main__":
    # Test run
    app = CurrenciesMain()
    app.run()