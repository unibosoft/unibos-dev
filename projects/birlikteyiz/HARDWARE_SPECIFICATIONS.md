# Birlikteyiz - Hibrit İletişim Sistemi Donanım Spesifikasyonları

## Sistem Mimarisi

### İletişim Katmanları
1. **Ev Ağı Katmanı**: Normal durumda WiFi üzerinden internet erişimi
2. **Acil Durum Katmanı**: LoRa ile düşük hızlı mesajlaşma (1-10 kbps, 10-15km)
3. **Orta Mesafe Katmanı**: 2.4GHz ile yüksek hızlı bağlantı (5Mbps, 10-15km)
4. **Yerel Ağ Katmanı**: Mesh network oluşturma

## Cihaz Tipleri

### Tip 1: Raspberry Pi Zero 2 W (Düşük Güç, LoRa Odaklı)
**Kullanım Alanı**: Uzun süreli çalışma, acil durum iletişimi, DOS tarzı arayüz

### Tip 2: Raspberry Pi 5 8-16GB (Yüksek Performans)
**Kullanım Alanı**: Ana koordinasyon merkezi, gelişmiş arayüz, AI işleme

---

## Detaylı Parça Listesi ve Fiyatlar (Türkiye)

### 🔧 Ana İşlemci Kartları

#### Raspberry Pi Zero 2 W Konfigürasyonu
| Parça | Model | Fiyat | Tedarikçi | Link |
|-------|-------|-------|-----------|------|
| Ana Kart | Raspberry Pi Zero 2 W | ~800-1000 TL | Robotistan | https://robotistan.com |
| MicroSD | Kioxia Exceria 64GB | ~300-400 TL | Teknosa/Vatan | - |
| Güç Kaynağı | 5V 2.5A USB-C | ~150-200 TL | Robotistan | - |

#### Raspberry Pi 5 Konfigürasyonu
| Parça | Model | Fiyat | Tedarikçi | Link |
|-------|-------|-------|-----------|------|
| Ana Kart | Raspberry Pi 5 8GB | ~4000-5000 TL | Robotistan | https://robotistan.com |
| MicroSD | Kioxia Exceria Plus 64GB | ~400-500 TL | Teknosa/Vatan | - |
| Güç Kaynağı | 5V 5A USB-C (27W) | ~300-400 TL | Robotistan | - |

### 📡 LoRa İletişim Modülleri

| Parça | Model | Frekans | Menzil | Fiyat | Tedarikçi |
|-------|-------|---------|--------|-------|-----------|
| **Temel LoRa** | Ra-01H | 868/915MHz | 5-10km | ~240 TL | Robotistan |
| **Gelişmiş LoRa** | EBYTE E220-900T22D | 868/915MHz | 5km | ~374 TL | Robocombo |
| **Uzun Menzil** | EBYTE E220-400T30D | 433MHz | 10km | ~570 TL | RFMarket |
| **Yüksek Güç** | SX1276 868MHz | 868MHz | 15km | ~646 TL | F1Depo |

**Önerilen**: EBYTE E220-900T22D (maliyet/performans dengesi)

### 📶 Uzun Mesafe WiFi Cihazları

| Parça | Model | Frekans | Hız | Menzil | Fiyat | Tedarikçi |
|-------|-------|---------|-----|--------|-------|-----------|
| **Ekonomik** | Ubiquiti Loco M2 | 2.4GHz | 150Mbps | 5km | ~2400 TL | Teknosa |
| **Standart** | Ubiquiti NanoStation M2 | 2.4GHz | 150Mbps | 10km | ~4200 TL | Wi.com.tr |
| **Yüksek Güç** | Ubiquiti NanoStation M2 + Anten | 2.4GHz | 150Mbps | 15km | ~5000 TL | AKBilgisayar |

**Önerilen**: Ubiquiti Loco M2 (başlangıç için ideal)

### 🛰️ GPS ve Konum Modülleri

| Parça | Model | Hassasiyet | Fiyat | Tedarikçi |
|-------|-------|------------|-------|-----------|
| **Temel** | Ublox NEO-7M | ±3m | ~180 TL | Robotistan |
| **Gelişmiş** | Ublox NEO-8M M8N | ±2.5m | ~280 TL | Robotistan |
| **Yüksek Hassasiyet** | Ublox GY-GPSV3 NEO-8M | ±1m | ~350 TL | Komponentci |

**Önerilen**: Ublox NEO-8M M8N

### 🌡️ Sensörler

| Parça | Model | Ölçüm Aralığı | Fiyat | Tedarikçi |
|-------|-------|---------------|-------|-----------|
| **Sıcaklık/Nem** | DHT22 (AM2302) | -40°C~80°C, 0-100%RH | ~150 TL | Robotistan |
| **Basınç** | BMP280 | 300-1100 hPa | ~80 TL | Robotistan |
| **Işık** | BH1750 | 1-65535 lux | ~60 TL | Direnc.net |

### 🖥️ Ekranlar

| Parça | Model | Boyut | Çözünürlük | Fiyat | Tedarikçi |
|-------|-------|-------|------------|-------|-----------|
| **Ekonomik** | 3.5" TFT LCD | 3.5" | 480x320 | ~400 TL | Robotistan |
| **Dokunmatik** | WaveShare 3.5" | 3.5" | 480x320 | ~600 TL | Robotistan |
| **Premium** | 4DPi-35 | 3.5" | 480x320 | ~800 TL | Robotistan |

**Önerilen**: WaveShare 3.5" (dokunmatik özellik için)

### 🌀 Soğutma Sistemleri

| Parça | Model | Boyut | Kontrol | Fiyat | Tedarikçi |
|-------|-------|-------|---------|-------|-----------|
| **Pi Zero için** | 30x30x7mm Fan | 30mm | 2-pin | ~80 TL | Robotistan |
| **Pi 5 için** | Orijinal Aktif Soğutucu | 30mm | PWM | ~200 TL | Robotistan |
| **RGB Fan** | RGB Soğutma Fanı | 30mm | PWM+RGB | ~250 TL | Robotistan |

### 🏠 Kasa ve Montaj

| Parça | Model | Malzeme | Boyut | Fiyat | Tedarikçi |
|-------|-------|---------|-------|-------|-----------|
| **Kasa Malzemesi** | 6mm Plywood | Kontrplak | 15x10x8cm | ~50 TL | Yapı Market |
| **Montaj Vidaları** | M2.5 Vida Seti | Metal | - | ~30 TL | Robotistan |
| **Kablolar** | Jumper Kablo Seti | - | 40 adet | ~40 TL | Robotistan |

### 🔌 Güç Yönetimi

| Parça | Model | Kapasite | Fiyat | Tedarikçi |
|-------|-------|----------|-------|-----------|
| **UPS Modülü** | PiJuice HAT | 1820mAh | ~1200 TL | Robotistan |
| **Solar Panel** | 6V 2W Solar | 2W | ~200 TL | Robotistan |
| **Powerbank** | 20000mAh USB-C | 20Ah | ~400 TL | Teknosa |

---

## 💰 Toplam Maliyet Analizi

### Ekonomik Konfigürasyon (Pi Zero 2W)
| Kategori | Fiyat |
|----------|-------|
| Ana Sistem | 1200 TL |
| LoRa İletişim | 374 TL |
| WiFi Uzun Mesafe | 2400 TL |
| GPS + Sensörler | 430 TL |
| Ekran | 400 TL |
| Soğutma | 80 TL |
| Kasa + Montaj | 120 TL |
| **TOPLAM** | **~5000 TL** |

### Premium Konfigürasyon (Pi 5)
| Kategori | Fiyat |
|----------|-------|
| Ana Sistem | 4800 TL |
| LoRa İletişim | 570 TL |
| WiFi Uzun Mesafe | 5000 TL |
| GPS + Sensörler | 580 TL |
| Ekran | 800 TL |
| Soğutma | 250 TL |
| Kasa + Montaj | 120 TL |
| UPS Sistemi | 1200 TL |
| **TOPLAM** | **~13300 TL** |

---

## 🔧 Teknik Spesifikasyonlar

### LoRa İletişim Özellikleri
- **Frekans**: 868MHz (Avrupa) / 915MHz (Amerika)
- **Güç**: 22dBm (158mW)
- **Menzil**: 5-15km (açık alan)
- **Veri Hızı**: 0.3-37.5 kbps
- **Modülasyon**: LoRa CSS
- **Hassasiyet**: -148dBm

### WiFi Uzun Mesafe Özellikleri
- **Frekans**: 2.4GHz (2400-2500MHz)
- **Güç**: 500mW (27dBm)
- **Menzil**: 5-15km (görüş hattı)
- **Veri Hızı**: 150Mbps (teorik), 5-50Mbps (gerçek)
- **Anten Kazancı**: 8-11dBi
- **Protokol**: 802.11n

### GPS Özellikleri
- **Uydu Sistemleri**: GPS, GLONASS, Galileo, BeiDou
- **Hassasiyet**: ±1-3 metre
- **Soğuk Başlatma**: <26 saniye
- **Sıcak Başlatma**: <1 saniye
- **Güç Tüketimi**: 30-60mA

---

## 🌐 Ağ Mimarisi

### Normal Durum (Ev Ağı)
```
Internet ← WiFi Router ← Birlikteyiz Cihazı
                    ↓
              Yerel Mesh Ağı
```

### Acil Durum (LoRa Ağı)
```
Cihaz A ←→ LoRa ←→ Cihaz B ←→ LoRa ←→ Cihaz C
   ↓                  ↓                  ↓
GPS Konum         GPS Konum         GPS Konum
```

### Hibrit Mod (2.4GHz + LoRa)
```
Yüksek Hız: 2.4GHz WiFi (5Mbps, 10km)
Düşük Güç: LoRa (1kbps, 15km)
Yedekleme: Mesh Network
```

---

## 📦 Kurulum Paketi İçeriği

### Standart Paket
1. Önceden yüklenmiş MicroSD kart
2. Raspberry Pi + LoRa modülü
3. GPS modülü + sensörler
4. 3.5" dokunmatik ekran
5. Plywood kasa (önceden kesilmiş)
6. Tüm kablolar ve bağlantı elemanları
7. Kurulum kılavuzu
8. Hızlı başlangıç kartı

### Premium Paket Ek İçerik
9. UPS modülü (kesintisiz güç)
10. Solar panel + şarj kontrolcüsü
11. Uzun mesafe WiFi anteni
12. Weatherproof kasa seçeneği
13. Uzaktan yönetim yazılımı

---

## 🛒 Tedarikçi Bilgileri

### Ana Tedarikçiler
- **Robotistan**: https://robotistan.com (Ana elektronik parçalar)
- **Direnc.net**: https://direnc.net (Sensörler, modüller)
- **Teknosa**: https://teknosa.com (SD kartlar, güç kaynakları)
- **Wi.com.tr**: https://wi.com.tr (Ubiquiti ürünleri)
- **RFMarket**: https://rfmarket.com.tr (RF modülleri)

### Alternatif Tedarikçiler
- **Robocombo**: https://robocombo.com
- **Komponentci**: https://komponentci.net
- **F1Depo**: https://f1depo.com
- **AKBilgisayar**: https://akbilgisayar.com

---

## ⚡ Güç Tüketimi Analizi

### Pi Zero 2W Konfigürasyonu
| Bileşen | Tüketim | Açıklama |
|---------|---------|----------|
| Pi Zero 2W | 400-600mA | Normal çalışma |
| LoRa Modülü | 30-200mA | Alıcı/verici modu |
| GPS Modülü | 30-60mA | Aktif konum alma |
| Sensörler | 10-20mA | DHT22 + BMP280 |
| Ekran | 100-200mA | 3.5" LCD aktif |
| **Toplam** | **570-1080mA** | **5V'da 2.8-5.4W** |

### Pi 5 Konfigürasyonu
| Bileşen | Tüketim | Açıklama |
|---------|---------|----------|
| Pi 5 8GB | 800-2000mA | Yük durumuna göre |
| LoRa Modülü | 30-200mA | Alıcı/verici modu |
| GPS Modülü | 30-60mA | Aktif konum alma |
| Sensörler | 10-20mA | DHT22 + BMP280 |
| Ekran | 100-200mA | 3.5" LCD aktif |
| Soğutma Fanı | 50-150mA | PWM kontrollü |
| **Toplam** | **1020-2630mA** | **5V'da 5.1-13.1W** |

### Pil Ömrü Hesaplamaları
- **20000mAh Powerbank ile Pi Zero**: 18-35 saat
- **20000mAh Powerbank ile Pi 5**: 7-19 saat
- **Solar Panel (2W) ile**: Sürekli çalışma (güneşli hava)

---

## 🔒 Güvenlik Özellikleri

### Donanım Güvenliği
- TPM 2.0 desteği (Pi 5)
- Secure Boot özelliği
- Donanım şifreleme
- Tamper detection

### Yazılım Güvenliği
- End-to-end şifreleme
- AES-256 veri koruması
- RSA-2048 anahtar değişimi
- Blockchain tabanlı kimlik doğrulama

### Fiziksel Güvenlik
- Su geçirmez kasa seçeneği
- Darbe dayanıklı tasarım
- Sıcaklık koruması (-20°C ~ +60°C)
- UV dayanıklı malzemeler

Bu spesifikasyon, Türkiye'deki mevcut tedarikçilerden temin edilebilir parçalarla, hem ekonomik hem de premium konfigürasyonlarda hibrit acil iletişim sistemi oluşturmak için gerekli tüm bilgileri içermektedir.

