#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
currencies v017 - Döviz Kurları Sistemi
Yazar: Berk Hatırlı - Bitez Bodrum
Tarih: 25 Haziran 2025
"""

import os
import sys
import json
import platform
import time
from datetime import datetime

class CurrencyTracker:
    def __init__(self):
        self.version = "v017"
        self.author = "Berk Hatırlı"
        self.location = "Bitez Bodrum"
        
    def clear_screen(self):
        """Ekranı temizle"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    def show_header(self):
        """Başlık göster"""
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║                 💱 currencies v017                            ║")
        print("║                Döviz Kurları Sistemi                         ║")
        print("║                                                               ║")
        print("║              Yazar: Berk Hatırlı - Bitez Bodrum              ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        
    def show_demo_rates(self):
        """Demo döviz kurlarını göster"""
        print("💱 Demo Döviz Kurları:")
        print(f"⏰ Güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Demo kurlar
        currencies = {
            "USD": {"name": "Amerikan Doları", "buy": 32.15, "sell": 32.25, "change": +0.12},
            "EUR": {"name": "Euro", "buy": 34.80, "sell": 34.92, "change": -0.08},
            "GBP": {"name": "İngiliz Sterlini", "buy": 40.25, "sell": 40.40, "change": +0.25},
            "CHF": {"name": "İsviçre Frangı", "buy": 35.60, "sell": 35.75, "change": +0.05},
            "JPY": {"name": "Japon Yeni", "buy": 0.22, "sell": 0.23, "change": -0.01},
            "CAD": {"name": "Kanada Doları", "buy": 23.80, "sell": 23.90, "change": +0.15},
            "AUD": {"name": "Avustralya Doları", "buy": 21.45, "sell": 21.55, "change": -0.03},
            "SEK": {"name": "İsveç Kronu", "buy": 3.05, "sell": 3.08, "change": +0.02}
        }
        
        print("┌─────┬─────────────────────┬─────────┬─────────┬─────────┐")
        print("│ Kod │ Para Birimi         │ Alış    │ Satış   │ Değişim │")
        print("├─────┼─────────────────────┼─────────┼─────────┼─────────┤")
        
        for code, data in currencies.items():
            change_str = f"{data['change']:+.2f}"
            if data['change'] > 0:
                trend = "📈"
            elif data['change'] < 0:
                trend = "📉"
            else:
                trend = "➡️"
                
            print(f"│ {code:<3} │ {data['name']:<19} │ {data['buy']:>7.2f} │ {data['sell']:>7.2f} │ {change_str:>5} {trend} │")
            
        print("└─────┴─────────────────────┴─────────┴─────────┴─────────┘")
        print()
        
    def show_crypto_rates(self):
        """Demo kripto para kurlarını göster"""
        print("₿ Demo Kripto Para Kurları:")
        print()
        
        cryptos = {
            "BTC": {"name": "Bitcoin", "price": 1850000, "change": +2.5},
            "ETH": {"name": "Ethereum", "price": 120000, "change": -1.2},
            "BNB": {"name": "Binance Coin", "price": 15000, "change": +0.8},
            "ADA": {"name": "Cardano", "price": 12.50, "change": +3.2},
            "DOT": {"name": "Polkadot", "price": 180, "change": -0.5},
            "AVAX": {"name": "Avalanche", "price": 850, "change": +1.8}
        }
        
        print("┌──────┬─────────────────┬─────────────┬─────────┐")
        print("│ Kod  │ Kripto Para     │ Fiyat (₺)   │ Değişim │")
        print("├──────┼─────────────────┼─────────────┼─────────┤")
        
        for code, data in cryptos.items():
            change_str = f"{data['change']:+.1f}%"
            if data['change'] > 0:
                trend = "🟢"
            elif data['change'] < 0:
                trend = "🔴"
            else:
                trend = "⚪"
                
            print(f"│ {code:<4} │ {data['name']:<15} │ {data['price']:>11,.2f} │ {change_str:>5} {trend} │")
            
        print("└──────┴─────────────────┴─────────────┴─────────┘")
        print()
        
    def simulate_live_update(self):
        """Canlı güncelleme simülasyonu"""
        print("📡 Canlı kurlar güncelleniyor...")
        
        for i in range(5):
            print(f"   📊 Veri alınıyor... {i+1}/5")
            time.sleep(0.5)
            
        print("   ✅ Kurlar başarıyla güncellendi!")
        print("   🕐 Son güncelleme:", datetime.now().strftime('%H:%M:%S'))
        print()
        
    def run(self):
        """Ana döngü"""
        self.clear_screen()
        self.show_header()
        
        print("🚧 Geliştirme Aşamasında - Demo Sürüm")
        print()
        print("Hello World - currencies sistemi aktif!")
        print()
        
        self.show_demo_rates()
        
        print("Demo Özellikleri:")
        print("1 - Döviz kurları görüntüle")
        print("2 - Kripto para kurları")
        print("3 - Canlı güncelleme")
        print("4 - Çıkış")
        print()
        
        while True:
            choice = input("Seçiminiz (1-4): ").strip()
            
            if choice == "1":
                self.show_demo_rates()
            elif choice == "2":
                self.show_crypto_rates()
            elif choice == "3":
                self.simulate_live_update()
                self.show_demo_rates()
            elif choice == "4":
                print("\n👋 Döviz kurları sistemi kapatılıyor...")
                break
            else:
                print("❌ Geçersiz seçim!")

def main():
    """Ana fonksiyon"""
    try:
        tracker = CurrencyTracker()
        tracker.run()
    except KeyboardInterrupt:
        print("\n\n👋 Sistem kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

if __name__ == "__main__":
    main()

