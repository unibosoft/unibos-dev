#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kişisel enflasyon v017 - Kişisel Enflasyon Takip Sistemi
Yazar: Berk Hatırlı - Bitez Bodrum
Tarih: 25 Haziran 2025
"""

import os
import sys
import json
import platform
from datetime import datetime, timedelta

class PersonalInflationTracker:
    def __init__(self):
        self.version = "v017"
        self.author = "Berk Hatırlı"
        self.location = "Bitez Bodrum"
        self.data_file = "inflation_data.json"
        self.load_data()
        
    def clear_screen(self):
        """Ekranı temizle"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    def show_header(self):
        """Başlık göster"""
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║               📊 kişisel enflasyon v017                       ║")
        print("║              Kişisel Enflasyon Takip Sistemi                 ║")
        print("║                                                               ║")
        print("║              Yazar: Berk Hatırlı - Bitez Bodrum              ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        
    def load_data(self):
        """Veri dosyasını yükle"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    "basket": {},
                    "prices": [],
                    "created": datetime.now().isoformat()
                }
        except Exception:
            self.data = {
                "basket": {},
                "prices": [],
                "created": datetime.now().isoformat()
            }
            
    def save_data(self):
        """Veri dosyasını kaydet"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Veri kaydedilemedi: {e}")
            
    def show_demo_data(self):
        """Demo verilerini göster"""
        print("📊 Demo Enflasyon Verileri:")
        print()
        
        # Örnek sepet
        demo_basket = {
            "Ekmek (1 adet)": [2.5, 2.8, 3.0],
            "Süt (1 litre)": [8.0, 8.5, 9.2],
            "Yumurta (10 adet)": [15.0, 16.5, 18.0],
            "Benzin (1 litre)": [25.0, 28.0, 32.0],
            "Elektrik (kWh)": [1.2, 1.4, 1.6]
        }
        
        print("🛒 Kişisel Harcama Sepeti:")
        for item, prices in demo_basket.items():
            current_price = prices[-1]
            old_price = prices[0]
            change = ((current_price - old_price) / old_price) * 100
            
            if change > 0:
                trend = "📈"
                color = "🔴"
            else:
                trend = "📉"
                color = "🟢"
                
            print(f"   {item:<20} {old_price:>6.2f}₺ → {current_price:>6.2f}₺ {color} {change:+5.1f}% {trend}")
            
        print()
        
        # Genel enflasyon
        total_old = sum(prices[0] for prices in demo_basket.values())
        total_new = sum(prices[-1] for prices in demo_basket.values())
        inflation_rate = ((total_new - total_old) / total_old) * 100
        
        print(f"💰 Toplam Sepet Değeri:")
        print(f"   Önceki: {total_old:>8.2f}₺")
        print(f"   Şimdiki: {total_new:>8.2f}₺")
        print(f"   📊 Kişisel Enflasyon: {inflation_rate:+5.1f}%")
        print()
        
    def run(self):
        """Ana döngü"""
        self.clear_screen()
        self.show_header()
        
        print("🚧 Geliştirme Aşamasında - Demo Sürüm")
        print()
        print("Hello World - kişisel enflasyon sistemi aktif!")
        print()
        
        self.show_demo_data()
        
        print("Demo Özellikleri:")
        print("1 - Sepet analizi görüntüle")
        print("2 - Enflasyon grafiği (metin)")
        print("3 - Çıkış")
        print()
        
        while True:
            choice = input("Seçiminiz (1-3): ").strip()
            
            if choice == "1":
                self.show_demo_data()
            elif choice == "2":
                self.show_inflation_chart()
            elif choice == "3":
                print("\n👋 Enflasyon takip sistemi kapatılıyor...")
                break
            else:
                print("❌ Geçersiz seçim!")
                
    def show_inflation_chart(self):
        """Basit metin grafiği göster"""
        print("\n📈 Enflasyon Trendi (Son 6 Ay):")
        months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran"]
        rates = [12.5, 14.2, 16.8, 18.1, 19.7, 21.3]
        
        for i, (month, rate) in enumerate(zip(months, rates)):
            bar = "█" * int(rate / 2)
            print(f"   {month:<8} {rate:>5.1f}% {bar}")
            
        print()

def main():
    """Ana fonksiyon"""
    try:
        tracker = PersonalInflationTracker()
        tracker.run()
    except KeyboardInterrupt:
        print("\n\n👋 Sistem kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

if __name__ == "__main__":
    main()

