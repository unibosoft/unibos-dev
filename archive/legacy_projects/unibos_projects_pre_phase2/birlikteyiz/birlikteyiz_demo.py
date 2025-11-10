#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
birlikteyiz v017 - Acil Durum İletişim Sistemi
Yazar: Berk Hatırlı - Bitez Bodrum
Tarih: 25 Haziran 2025
"""

import os
import sys
import time
import platform
from datetime import datetime

class BirlikteyizSystem:
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
        print("║                  🚨 birlikteyiz v017                          ║")
        print("║              Acil Durum İletişim Sistemi                     ║")
        print("║                                                               ║")
        print("║              Yazar: Berk Hatırlı - Bitez Bodrum              ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        
    def show_status(self):
        """Sistem durumunu göster"""
        print("📡 Sistem Durumu:")
        print("   ✅ LoRa Modülü: Hazır")
        print("   ✅ Raspberry Pi: Bağlı")
        print("   ✅ Acil Durum Protokolü: Aktif")
        print("   ✅ Mesh Ağ: Çalışıyor")
        print()
        
    def simulate_emergency_message(self):
        """Acil durum mesajı simülasyonu"""
        print("🚨 Acil Durum Mesajı Gönderiliyor...")
        print("📍 Konum: Bitez Bodrum (37.033333, 27.383333)")
        print("⏰ Zaman:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("📡 LoRa Frekansı: 868 MHz")
        
        for i in range(3):
            print(f"   📤 Mesaj gönderiliyor... {i+1}/3")
            time.sleep(1)
            
        print("   ✅ Mesaj başarıyla gönderildi!")
        print("   📨 Yakındaki 5 cihaza ulaştı")
        print()
        
    def run(self):
        """Ana döngü"""
        self.clear_screen()
        self.show_header()
        
        print("🚧 Geliştirme Aşamasında - Demo Sürüm")
        print()
        print("Hello World - birlikteyiz sistemi aktif!")
        print()
        
        self.show_status()
        
        print("Demo Özellikleri:")
        print("1 - Acil durum mesajı gönder")
        print("2 - Sistem durumunu kontrol et")
        print("3 - Çıkış")
        print()
        
        while True:
            choice = input("Seçiminiz (1-3): ").strip()
            
            if choice == "1":
                self.simulate_emergency_message()
            elif choice == "2":
                self.show_status()
            elif choice == "3":
                print("\n👋 birlikteyiz sistemi kapatılıyor...")
                break
            else:
                print("❌ Geçersiz seçim!")

def main():
    """Ana fonksiyon"""
    try:
        system = BirlikteyizSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n👋 Sistem kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

if __name__ == "__main__":
    main()

