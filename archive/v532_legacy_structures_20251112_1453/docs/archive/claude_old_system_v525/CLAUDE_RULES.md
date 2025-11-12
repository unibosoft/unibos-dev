# CLAUDE_RULES.md - Detaylı Kurallar ve Prosedürler

> **📋 NOT**: Bu dosya detaylı kuralları içerir. Temel kurallar için [CLAUDE_CORE.md](./CLAUDE_CORE.md) dosyasına bakın.

## 🚨 KRİTİK KURALLAR - HER ZAMAN ÖNCELİKLİ

### ⏰ ZORUNLU: İSTANBUL/AVRUPA SAAT DİLİMİ (UTC+3)
- **TÜM TARİH/SAAT DAMGALARI**: Istanbul/Europe timezone (UTC+3) ZORUNLU
- **YANLIŞ**: UTC, GMT, veya diğer saat dilimleri ❌
- **DOĞRU**: Istanbul saati (UTC+3) ✅
- **FORMATLAMA**: 
  - Tarih: `YYYY-MM-DD`
  - Saat: `HH:MM:SS +03:00`
  - Build: `YYYYMMDD_HHMM` (24 saat formatı)
  - Örnek: `2025-07-17 18:08:00 +03:00`
  - Build Örnek: `20250717_1808`
- **UYGULANACAK YERLER**:
  - VERSION.json dosyaları
  - Build numaraları
  - Log dosyaları
  - Commit mesajları
  - Arşiv isimlendirmeleri
  - main.py içindeki VERSION_INFO
- **KRİTİK BUILD KURALI - ZORUNLU KONTROL**:
  ```bash
  # Claude her build oluşturmadan önce güncel saati almalı:
  date "+%Y%m%d_%H%M"  # BU KOMUTU ÇALIŞTIR VE SONUCU KULLAN!
  
  # ❌ YANLIŞ: Build saatini kendim belirlerim (16:50 gibi)
  # ❌ YANLIŞ: Geçmiş bir saatten devam ederim
  # ❌ YANLIŞ: Tahmini saat kullanırım
  # ✅ DOĞRU: date komutu çıktısını kullanırım
  
  # ÖRNEK:
  # Sistem saati 16:14 ise build: 20250717_1614 olmalı
  # Sistem saati 18:30 ise build: 20250717_1830 olmalı
  ```
  
- **CLAUDE İÇİN MUTLAK KURAL**:
  ```python
  # HER VERSİYON GÜNCELLEMESİNDE:
  # 1. Önce sistem saatini kontrol et
  import subprocess
  result = subprocess.run(['date', '+%Y%m%d_%H%M'], 
                         capture_output=True, text=True)
  current_build = result.stdout.strip()
  print(f"Sistem saati build: {current_build}")
  
  # 2. Bu değeri VERSION.json'da kullan
  version_data['build_number'] = current_build
  
  # 3. main.py VERSION_INFO'da kullan  
  VERSION_INFO['build'] = current_build
  
  # ASLA BAŞKA BİR SAAT KULLANMA!
  ```
- **Python'da Zorunlu Kullanım**:
  ```python
  from datetime import datetime
  from zoneinfo import ZoneInfo
  
  # YANLIŞ ❌
  now = datetime.now()
  
  # DOĞRU ✅
  now = datetime.now(ZoneInfo('Europe/Istanbul'))
  ```
- **CLAUDE İÇİN ZORUNLU KONTROL**:
  ```python
  # Her versiyon güncellemesinde önce kontrol et:
  import subprocess
  # MUTLAKA TZ='Europe/Istanbul' ile çalıştır!
  current_time = subprocess.run(['bash', '-c', "TZ='Europe/Istanbul' date '+%Y%m%d_%H%M'"], 
                               capture_output=True, text=True).stdout.strip()
  print(f"Güncel Istanbul saati: {current_time}")
  # Bu değeri VERSION.json ve main.py'de kullan
  ```
- **🚨 MUTLAK KURAL - HER VERSİYON GÜNCELLEMESİNDE**:
  ```bash
  # ÖNCE BU KOMUTU ÇALIŞTIR:
  TZ='Europe/Istanbul' date "+%Y%m%d_%H%M"
  
  # ÇIKAN DEĞERİ KULLAN! ASLA TAHMİN ETME!
  # Örnek: Eğer çıktı 20250718_1754 ise
  # VERSION.json: "build_number": "20250718_1754"
  # main.py: "build": "20250718_1754"
  ```

### 📋 ZORUNLU: COMMUNICATION LOG YÖNETİMİ - MUTLAK KURAL ⚠️

**🚨 DİKKAT**: BU KURAL ASLA ATLANMAMALI! HER VERSİYON GÜNCELLEMESİNDE ZORUNLUDUR!

- **HER VERSİYON GÜNCELLEMESİNDE ZORUNLU**:
  1. Mevcut communication log'ları kontrol et
  2. Yeni log oluştur veya güncelle
  3. 3'ten fazla log varsa en eskileri sil
  4. VERSION.json ve main.py güncellemeden ÖNCE log yaz

- **MAKSİMUM LOG SAYISI**: Sadece SON 3 LOG tutulur
- **LOG FORMAT**: `CLAUDE_COMMUNICATION_LOG_vXXX_to_vYYY_YYYYMMDD_HHMM.md`
- **ZORUNLU İÇERİK**:
  ```markdown
  # CLAUDE COMMUNICATION LOG
  
  ## Oturum Bilgileri
  - **Başlangıç Versiyonu**: vXXX
  - **Bitiş Versiyonu**: vYYY
  - **Tarih**: YYYY-MM-DD
  - **Başlangıç Saati**: HH:MM:SS +03:00 (Istanbul)
  - **Bitiş Saati**: HH:MM:SS +03:00 (Istanbul)
  - **Claude Modeli**: [Model adı]
  
  ## Yapılan İşlemler
  - İşlem listesi
  
  ## Kullanıcı Geri Bildirimleri
  - Kullanıcı mesajları
  
  ## Çözülen Sorunlar
  - ✅ Çözülen sorun listesi
  
  ## Devam Eden Sorunlar
  - ⚠️ Çözülmemiş sorun listesi
  
  ## Teknik Notlar
  - Önemli teknik detaylar
  ```

- **OTOMATİK KONTROL VE TEMİZLEME**:
  ```python
  # HER VERSİYON GÜNCELLEMESİNDE ÇALIŞTIR:
  import glob
  import os
  
  # 1. Mevcut log'ları kontrol et
  comm_logs = sorted(glob.glob('CLAUDE_COMMUNICATION_LOG_*.md'), reverse=True)
  print(f"Mevcut log sayısı: {len(comm_logs)}")
  
  # 2. Yeni log oluştur
  # (vXXX_to_vYYY formatında)
  
  # 3. 3'ten fazla varsa sil
  if len(comm_logs) > 3:
      for log in comm_logs[3:]:
          os.remove(log)
          print(f"Silindi: {log}")
  ```

- **🔴 UNUTMA**: Versiyon güncellemesinde log yazmayı unutursan kullanıcı uyarır!

## İletişim Formatı ve İş Akışı 🔄

### 1. İşlem Öncelik Sıralaması - YENİ KURAL 🎯
- **CLAUDE HER BAŞLADIĞINDA**: CLAUDE.md'deki Python scripti otomatik çalışır
  - Manuel terminal açılışında
  - VS Code içinde açıldığında
  - UNIBOS içinden çağrıldığında
- **SS Kontrolü ve Arşivleme**: 
  1. screenshot_manager.py ile otomatik SS tespiti
  2. Bulunan SS'ler vXXX_build_YYYYMMDD_HHMM_N.png formatında arşivlenir
  3. Ana dizin otomatik temizlenir
  4. Son 5 arşivlenen SS gösterilir
- **Fallback Mekanizması**: 
  1. screenshot_manager yoksa bash komutu ile kontrol
  2. Manuel arşivleme uyarısı verilir
- **KRİTİK**: Bu sıralama ASLA değiştirilmemeli, SS analizi her zaman öncelikli
- **ÖNEMLİ**: Basit `ls -la *.png` YANLIŞ! Çünkü büyük harfli uzantıları atlar. Daima grep ile kontrol et!

### 2. Claude Teslim Sonrası ve Arşivleme 🔧
- Claude işlemi tamamlar ve "İşlemleri tamamladım. Versiyon: vXXX Build: YYYYMMDD_HHMM" formatında bildirir
- **OTOMATİK ARŞİVLEME KOMUTLARI** (Öncelik sırasıyla):
  1. `python3 src/archive_version.py` - ÖNERİLEN, otomatik format ve hata kontrolü
  2. `bash src/version_manager.sh` - Alternatif, interaktif kontrol
  3. **YASAK**: Eski script kullanımı (archive/versions içindekiler)
- **SCRIPT BULMA**: Bulunamazsa `find . -name "archive*.py" -o -name "version*.sh" | grep -v "./archive/"`
- Kullanıcı son hali inceler

### 3. Screenshot (SS) Yönetimi 📸 - FORCED RULES v2.0
- Kullanıcı ana dizine screenshot'lar ekleyebilir
- Claude screenshot'ları okur ve anlar
- **FORCED KURAL**: Ana dizinde işlenmemiş SS görülürse HEMEN:
  - **YENİ İSİMLENDİRME FORMATI**: `unibos_vXXX_YYYYMMDD_HHMM_N.png`
  - YANLIŞ: `vXXX_build_YYYYMMDD_HHMM_N.png` ❌
  - DOĞRU: `unibos_vXXX_YYYYMMDD_HHMM_N.png` ✅
  - Örnek: `Screenshot 2025-07-15 at 18.19.52.png` → `unibos_v062_20250715_1808_1.png`
- **FORCED KLASÖR YAPISI**:
  - v001-v099 → `archive/media/screenshots/v001-099/`
  - v100-v199 → `archive/media/screenshots/v100-199/`
  - v200-v299 → `archive/media/screenshots/v200-299/`
  - **DİKKAT**: v100+ SS'ler ASLA v001-099 klasöründe olmamalı!
- **FORCED ARŞİV İSİMLENDİRME**:
  - Tüm arşiv ZIP'leri: `unibos_vXXX_YYYYMMDD_HHMM.zip`
  - Tüm arşiv klasörleri: `unibos_vXXX_YYYYMMDD_HHMM/`
  - "build" kelimesi KULLANILMAYACAK ❌
- **KRİTİK KONTROLLER**:
  1. Ana dizinde SS kontrolü: `ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'`
  2. SS taşıma: `mv` komutu (kopyalama değil!)
  3. İşlem sonrası kontrol: `ls *.png *.jpg *.jpeg 2>/dev/null || echo "✅ Ana dizin temiz"`
- **FORCED SCREENSHOT KURALLARI**:
  - HER screenshot MUTLAKA `unibos_` ile başlamalı
  - HER screenshot doğru versiyon klasöründe olmalı
  - HER screenshot işleminde bu kurallar ZORUNLU uygulanmalı
- **OTOMATİK KONTROL SCRİPTİ**: Claude her başladığında bu kontrolü yapar

### 4. Döngü Devamı
- SS'lerden yeni talimatlar varsa uygulanır
- Yeni build oluşturulur
- Döngü bu şekilde devam eder

### 5. SS Okuma Kuralları
- Tüm SS'ler detaylıca incelenmeli
- İçerikten talimatlar çıkarılmalı
- UI/UX önerileri dikkate alınmalı
- Hata mesajları varsa düzeltilmeli

### 6. Arşivlenen SS'lerin Analizi - YENİ KURAL
- **ZORUNLU**: Her arşivlenen screenshot mutlaka okunmalı ve analiz edilmeli
- **İçerik Anlama**: SS'deki tüm görsel öğeler, metinler, hatalar incelenmeli
- **Görev İlişkilendirme**: SS'den çıkarılan bilgiler yeni görevlerle ilişkilendirilmeli
- **Otomatik Todo**: SS'den tespit edilen sorunlar/iyileştirmeler TodoWrite ile kaydedilmeli
- **Örnek Akış**:
  1. SS arşivlenir: `archive/media/screenshots/v061-current/vXXX_build_YYYYMMDD_HHMM_N.png`
  2. Hemen Read tool ile SS okunur
  3. İçerik analiz edilir (UI sorunları, hatalar, eksikler)
  4. Tespit edilen konular TodoWrite ile görev olarak eklenir
  5. Kullanıcıya SS'den çıkarılan gözlemler bildirilir
- **KRİTİK**: Bu adım atlanırsa kullanıcının görsel geri bildirimleri kaybolur

### 7. Claude Saat Kontrolü ve Versiyon Güncellemesi - MUTLAK KURAL ⏰

**ZORUNLU**: Claude her versiyon güncellemesinde sistem saatini kullanmalı:

```python
# Claude her versiyon güncellemesinde bu kontrolü yapar
def get_current_istanbul_time():
    """Güncel Istanbul saatini al - ASLA tahmin etme!"""
    import subprocess
    from datetime import datetime
    
    # Build numarası için
    build_result = subprocess.run(['date', '+%Y%m%d_%H%M'], 
                                 capture_output=True, text=True)
    build_number = build_result.stdout.strip()
    
    # Tarih/saat için
    date_result = subprocess.run(['date', '+%Y-%m-%d %H:%M:%S'], 
                                capture_output=True, text=True)
    date_time = date_result.stdout.strip() + " +03:00"
    
    print(f"🕒 Sistem saati kontrol ediliyor...")
    print(f"   Build: {build_number}")
    print(f"   Tarih: {date_time}")
    
    return build_number, date_time

# KULLANIM:
# build, date_time = get_current_istanbul_time()
# VERSION.json ve main.py'de bu değerleri kullan
```

**HATA ÖRNEĞİ**: Kullanıcı "saat 16:13" dediğinde, sen "18:08" yazmışsın!
**DOĞRU YAKLAŞIM**: Daima `date` komutu çıktısını kullan.

### 8. Claude Başlangıç Karşılaması, Screenshot ve Communication Log Kontrolü - GÜNCELLENDİ 📋
- **ZORUNLU**: Claude her oturum başında otomatik kontroller yapmalı
- **OTOMATİK AKIŞ**:
  1. CLAUDE dosyaları yüklenir
  2. Screenshot kontrolü OTOMATİK yapılır: `ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'`
  3. **YENİ**: Communication Log'lar okunur ve analiz edilir:
     ```bash
     # Son 3 communication log'u bul ve oku
     for log in $(ls -t CLAUDE_COMMUNICATION_LOG_*.md | head -3); do
         echo "📄 Reading: $log"
         # Log içeriğinden önemli bilgileri çıkar:
         # - Son versiyon numarası
         # - Çözülmemiş sorunlar
         # - Kullanıcı geri bildirimleri
         # - Yarım kalan görevler
     done
     ```
  4. **Log Analiz Kuralları**:
     - En son log'dan başlangıç versiyonu tespit edilir
     - "Çözülmemiş", "devam ediyor", "TODO" kelimeleri aranır
     - Kullanıcı şikayetleri ve önerileri not edilir
     - Önceki oturumda yarım kalan görevler TodoWrite'a eklenir
  5. SS varsa: Read tool ile okunur, analiz edilir, arşivlenir
  6. SS yoksa: Son arşivlenen SS'ler kontrol edilir
  7. Mevcut versiyon kontrol edilir
  8. Türkçe karşılama mesajı verilir
  9. **Önemli Bilgiler Özeti**: Log'lardan ve SS'lerden çıkarılan bilgiler özetlenir
- **FORMAT**: "Projeyi okudum ve geliştirme yapmaya hazırım, talimatlarınızı bekliyorum."
- **KRİTİK**: Screenshot kontrolü KULLANICI ONAYI BEKLENMEDEN yapılmalı
- **UYGULAMA**: Bu işlemler oturum başında otomatik olarak gerçekleştirilmeli
- **ÖNEMLİ**: Bu karşılama diğer dillere çevrilmemeli, her zaman Türkçe olmalı

### 7.1 Communication Log Okuma Kuralı - YENİ 📋
- **ZORUNLU**: Claude işlem yapmaya başlamadan önce son 3 communication log'u okumalı
- **AMAÇ**: Güncel durumu ve son yapılan işlemleri tam anlamıyla anlamak
- **UYGULAMA**:
  1. İşlem yapmaya başlamadan önce CLAUDE_COMMUNICATION_*.log dosyalarını kontrol et
  2. En son 3 log dosyasını Read tool ile oku
  3. Yapılan işlemleri, sorunları ve çözümleri anla
  4. Mevcut durumu ve context'i kavra
  5. Kullanıcının son isteklerini ve tamamlanan görevleri gözden geçir
- **FORMAT**: `ls -t CLAUDE_COMMUNICATION_*.log | head -3` ile son 3 logu bul ve oku
- **KRİTİK**: Bu okuma işlemi her yeni görev öncesi yapılmalı
- **FAYDA**: Gereksiz tekrarları önler, context kaybını engeller, daha tutarlı çözümler sağlar

### 8. Screenshot Analiz Kuralı - YENİ 📸

**ZORUNLU**: Ana dizine eklenen her screenshot mutlaka arşivlendikten sonra içeriği analiz edilmelidir.

#### Screenshot Analiz Protokolü:
1. **Arşivleme Sonrası**:
   ```bash
   # Arşivlenen screenshot'ı oku
   Read archive/media/screenshots/vXXX-XXX/unibos_vXXX_YYYYMMDD_HHMM_N.png
   ```

2. **İçerik Analizi**:
   - UI durumu ve görünen hatalar
   - Kullanıcının ne yapmaya çalıştığı
   - Eksik veya hatalı görünen özellikler
   - İyileştirme önerileri

3. **Analiz Sonucu**:
   - Tespit edilen sorunlar için çözüm öner
   - UI/UX iyileştirmeleri belirle
   - Kullanıcı deneyimini geliştir

4. **Arşiv Screenshot Kontrolü - YENİ**:
   - Ana dizinde screenshot bulunamazsa, güncel versiyon için arşivlenmiş screenshot'ları mutlaka kontrol et
   - Komut: `find archive/media/screenshots -name "*vXXX*" -type f | sort -r | head -5`
   - Bulunan arşiv screenshot'ları Read tool ile incelenmeli
   - Bu sayede kullanıcının rapor ettiği sorunlar yakalanır

**ÖRNEK**: v161_20250717_0438_1.png analizi:
- Claude tools menüsü açık
- Update suggestions seçilmiş ama görsel ilerleme yok
- Çözüm: Progress bar ve spinner eklendi (v162)

### 9. Claude Tool Giriş/Çıkış Öneri Sistemi 🎯

#### Öneri Algoritması
1. **Proje Felsefesine Uygun Öneriler**:
   - Lowercase UI standardı geliştirmeleri
   - Modül entegrasyonları ve iyileştirmeleri
   - Performans optimizasyonları
   - Güvenlik güncellemeleri
   - Kullanıcı deneyimi geliştirmeleri

2. **Öneri Kaynak Havuzu**:
   - %70 Güncel TODO'lar ve bilinen sorunlar
   - %20 Eski versiyonlardan (v001-v119) kayıp özellik/bilgi taraması
   - %10 Proaktif yenilik önerileri

3. **Öneri Öncelik Sıralaması**:
   - 🔴 Kritik: Güvenlik, veri kaybı riski olan konular
   - 🟠 Yüksek: Kullanıcı deneyimini doğrudan etkileyen konular
   - 🟡 Orta: Performans ve optimizasyon konuları
   - 🟢 Düşük: Estetik ve minor iyileştirmeler

#### Claude Tool Giriş Protokolü
```
═══════════════════════════════════════════════════════
          🦄 UNIBOS GELİŞTİRME ÖNERİLERİ v120
═══════════════════════════════════════════════════════

🎯 Güncel Öneriler (Öncelik Sırasıyla):

1. [🔴 Kritik] Blink modülü konum gizlilik ayarları güncellenmeli
2. [🟠 Yüksek] Currencies modülünde API hata yönetimi iyileştirilmeli  
3. [🟡 Orta] Recaria harita cache sistemi optimize edilmeli
4. [🟢 Düşük] Terminal arayüzünde renk kontrastları artırılmalı
5. [🟢 Düşük] v042'den kayıp parallel system özellikleri geri getirilmeli

═══════════════════════════════════════════════════════
Model Seçimi: [opus/sonnet/haiku]
═══════════════════════════════════════════════════════
```

#### Claude Tool Çıkış Protokolü
1. **Uygulanan Önerileri Kontrol Et**:
   - Hangi öneriler uygulandı?
   - Hangileri kısmen uygulandı?
   - Hangileri uygulanmadı?

2. **Öneri Listesini Güncelle**:
   - Uygulananları listeden çıkar
   - Yeni önerileri ekle (aynı algoritma ile)
   - Öncelikleri yeniden hesapla

3. **Çıkış Raporu**:
```
═══════════════════════════════════════════════════════
          🦄 UNIBOS OTURUM SONU RAPORU
═══════════════════════════════════════════════════════

✅ Uygulanan Öneriler:
- [🟠] Currencies modülünde API hata yönetimi iyileştirildi

📋 Güncellenen Öneri Listesi:
1. [🔴 Kritik] Blink modülü konum gizlilik ayarları güncellenmeli
2. [🟡 Orta] Recaria harita cache sistemi optimize edilmeli  
3. [🟢 Düşük] Terminal arayüzünde renk kontrastları artırılmalı
4. [🟢 Düşük] v042'den kayıp parallel system özellikleri geri getirilmeli
5. [🟢 Düşük] YENİ: Birlikteyiz LoRa mesaj şifreleme eklenebilir

═══════════════════════════════════════════════════════
```

#### Eski Versiyon Tarama Kuralları
- Her 5 oturumda bir v001-v020 arası taranır
- Her 3 oturumda bir v021-v050 arası taranır  
- Her oturumda v051-güncel arası kontrol edilir
- Kayıp özellikler tespit edilirse öneri listesine eklenir

## Versiyon Teslim Kuralları 🚀 - MUTLAK KURAL - ASLA UNUTMA!

**🚨 CLAUDE İÇİN ZORUNLU HATIRLATMA**: BU KURALLARI HER VERSİYON GÜNCELLEMESİNDE UYGULA!

**KRİTİK**: Her versiyon/build tesliminde aşağıdaki adımlar MUTLAKA uygulanmalıdır:

### 1. Ana Dizinde Güncel Versiyon - KRİTİK KURAL
- **En son hali daima ana dizinde bulunmalı**
- Tüm değişiklikler tamamlanmış olmalı
- CLAUDE*.md dosyaları güncel olmalı
- VERSION.json ana dizinde en güncel versiyonu göstermeli
- src/main.py içindeki versiyon bilgileri senkronize olmalı
- **KONTROL**: `./launch.sh` ile başlatılan yazılım en güncel versiyonu göstermeli
- **ASLA**: Arşiv versiyonu ana dizinde olmamalı
- **DOĞRULAMA**: VERSION.json'daki versiyon ile archive/versions/'daki en son klasör versiyonu aynı olmalı

### 2. Arşivleme Script Kullanımı - YENİ KURAL 🔧
- **Python Script**: `python3 src/archive_version.py` - Otomatik arşivleme için önerilen yöntem
- **Bash Script**: `bash src/version_manager.sh` - Manuel kontrol isteyenler için
- **Script Lokasyonları**:
  - `src/archive_version.py` - Python tabanlı otomatik arşivleme
  - `src/version_manager.sh` - Bash tabanlı interaktif arşivleme
- **ASLA**: Eski versiyonlardaki script'leri kullanma (archive/versions içindekiler)
- **ÖNERİLEN**: archive_version.py kullan - hata kontrolü ve otomatik format sağlar

### 3. Versiyon Arşivi Oluşturma
- `archive/versions/` klasörüne açık klasör olarak kopyala
- Format: `unibos_vXXX_YYYYMMDD_HHMM/`
- Aynı versiyonda birden fazla build olabilir (tarih/saat ile ayrılır)
- **KRİTİK KURAL**: Arşivlenen versiyonların içinde ASLA `archive/` dizini bulunmamalı
- **YASAK**: Versiyonun kendi içinde archive klasörü olması (iç içe arşiv yaratır)
- **KONTROL**: Her arşivlemeden önce versiyonda archive/ dizini varsa silinmeli

### 5. Teslim Mesajı Formatı
```
İşlemleri tamamladım.
Versiyon: vXXX
Build: YYYYMMDD_HHMM
Yapılan işlemler: xxxx (burada son güncellemede yapılan işlemler yazsın)

📦 Arşivleme işlemi başlatılıyor...
[python3 src/archive_version.py çalıştırılır]
✅ Versiyon arşivlendi: versions klasörüne
```


### 6. CLAUDE Dosyaları Mutlaka Güncel Olmalı
- Tüm CLAUDE*.md dosyaları güncel olmalı
- Yeni kurallar eklendikçe güncellenmeli
- Versiyon teslim kuralları korunmalı

### 7. Versiyonlama Öncesi Görev Kontrolü - YENİ KURAL 📋
**ZORUNLU**: Her yeni versiyon oluşturulmadan önce:

**🚨🚨🚨 CLAUDE İÇİN MUTLAK KURAL 🚨🚨🚨**
```python
# HER VERSİYON GÜNCELLEMESİNDEN SONRA BU KONTROL YAPILMALI:
def version_update_checklist():
    """Claude her versiyon güncellemesinden sonra bu kontrolü yapar"""
    print("=== VERSİYON ARŞİVLEME KONTROL LİSTESİ ===")
    
    # 1. VERSION.json güncellendi mi?
    print("☐ src/VERSION.json güncellendi")
    
    # 2. main.py VERSION_INFO güncellendi mi?
    print("☐ src/main.py VERSION_INFO güncellendi")
    
    # 3. CHANGELOG.md eklendi mi?
    print("☐ CHANGELOG.md'ye yeni versiyon eklendi")
    
    # 4. ARŞİVLEME KOMUTU
    print("\n🚨 ŞİMDİ ARŞİVLE:")
    print("python3 src/archive_version.py")
    
    # 5. ARŞİVLEME SONRASI KONTROL
    print("\nArşivleme sonrası kontrol:")
    print("ls -la archive/versions/ | grep vXXX")
    
# UNUTMA: HER VERSİYON SONRASI BU KONTROL YAPILMALI!
```

1. **Communication Log Analizi**:
   ```bash
   # Son 3 comm log'u kontrol et
   for log in $(ls -t CLAUDE_COMMUNICATION_LOG_*.md | head -3); do
       grep -E "devam ediyor|çözülmemiş|TODO|❌|⚠️" $log
   done
   ```

2. **Tamamlanmamış Görev Kriterleri**:
   - "devam ediyor" işaretli görevler
   - "çözülmemiş" olarak belirtilen sorunlar
   - Kullanıcı şikayetleri (v171'de "navigasyon sorunu devam ediyordu")
   - TODO veya ⚠️ işaretli konular

3. **Görev Tamamlama Zorunluluğu**:
   - Tespit edilen tüm sorunlar çözülmeli
   - Kullanıcı geri bildirimleri ele alınmalı
   - Örnek: v171'de navigasyon sorunu tam çözülmemiş, v172'de çözüldü

4. **Versiyon Açıklaması İçermeli**:
   - Hangi önceki sorunlar çözüldü
   - Hangi yeni özellikler eklendi
   - Hangi iyileştirmeler yapıldı

### 8. Communication Log Yönetimi 📝
- **Otomatik Temizlik**: Arşivleme sırasında sadece son 3 communication log tutulur
- **Arşive Dahil**: Mevcut communication log'lar versiyonla birlikte arşivlenir
- **Format**: `CLAUDE_COMMUNICATION_LOG_YYYYMMDD_HHMM.md`
- **İçerik**: Oturum bilgileri, yapılan işlemler, kullanıcı geri bildirimleri
- **Kontrol**: `ls -la CLAUDE_COMMUNICATION_LOG_*.md | wc -l` (max 3 olmalı)

### 9. Crash Noktaları Düzenli Kontrolü - ZORUNLU
Her geliştirme oturumunda ve özellikle navigasyon/input handling değişikliklerinden sonra:

```bash
# Potansiyel crash noktalarını kontrol et
echo "=== Crash Noktaları Kontrolü ==="

# 1. None/undefined değişken kullanımları
echo "1. None/undefined checks:"
grep -n "debug_file\." src/main.py | grep -v "if debug_file" | grep -v "and debug_file"

# 2. Array bounds kontrolsüz erişimler
echo "2. Array access without bounds check:"
grep -n "\[.*\]" src/main.py | grep -v "if len(" | grep -v "and len("

# 3. Try-except eksik olan kritik bölümler
echo "3. Key handlers without try-except:"
grep -A5 -B2 "key == '\\\x1b\[" src/main.py | grep -v "try:"

# 4. Menu state initialization kontrolü
echo "4. Menu state usage without init check:"
grep -n "menu_state\." src/main.py | grep -E "(modules|tools)" | grep -v "if.*menu_state"

echo "=== Kontrol tamamlandı ==="
```

Bu kontrol özellikle şu durumlarda çalıştırılmalı:
- Arrow key veya input handling değişikliklerinde
- Menu navigasyon güncellemelerinde
- Debug mode değişikliklerinde
- Exception handling eklemelerinde

## Git Workflow

### Feature Branch Kullanımı
- Feature branch kullanımı
- Semantic versioning (vX.Y.Z)
- Commit mesajları: `[MODULE] Açıklama` formatında

### Commit İşlemleri
1. Git status kontrolü
2. Git diff ile değişiklikleri gözden geçir
3. Staged/unstaged değişiklikleri analiz et
4. Commit mesajı hazırla (1-2 cümle, "neden" odaklı)
5. Commit oluştur:
```bash
git commit -m "$(cat <<'EOF'
   Commit mesajı buraya.

   🤖 Generated with [Claude Code](https://claude.ai/code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
```

### Pull Request Oluşturma
1. Git status, diff ve log komutlarını paralel çalıştır
2. Tüm değişiklikleri analiz et (TÜM commitler)
3. PR özeti hazırla
4. gh pr create kullanarak PR oluştur

## Claude Oturum Kapanış Kuralları - ZORUNLU

Claude CLI'dan çıkış yapmadan önce:

### Talimat Kontrolü
Son oturumdaki TÜM kullanıcı talimatlarının yerine getirilip getirilmediği kontrol edilmeli

### Kontrol Listesi
1. Versiyon oluşturuldu mu? `ls -la archive/versions/unibos_vXXX*`
2. Versions klasörüne açık versiyon kopyalandı mı? `ls -la archive/versions/unibos_vXXX*/`
3. Ana dizinde screenshot kaldı mı? `ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'`
4. Versiyon senkronizasyonu doğru mu? `cat src/VERSION.json | grep version`
5. CHANGELOG.md güncellendi mi? `tail -n 20 CHANGELOG.md`
6. **GÜNCEL VERSİYON ARŞİVLENDİ Mİ?**: 
   - `ls -la archive/versions/ | grep $(cat src/VERSION.json | jq -r .version)`

### Otomatik Arşivleme - YENİ 🚀
- **archive_version.py**: Versiyon arşivleme otomasyonu
- Kullanım: `python3 src/archive_version.py`
- Komutlar:
  - `python3 src/archive_version.py` - Mevcut versiyonu arşivle
  - `python3 src/archive_version.py list` - Mevcut arşivleri listele  
  - `python3 src/archive_version.py force` - Zorla arşivle (üzerine yaz)

### Çıkış Sonrası
- Tüm işlemler tamamlandıktan sonra kullanıcıya bilgi verilerek çıkış yapılmalı
- Yeni versiyon başlatma: `./unibos.sh` ile yeni versiyon başlatılmalı
- **SONSUZ DÖNGÜ ÖNLEMİ**: Kontroller SADECE BİR KEZ yapılmalı
- **UYGULAMA**: Bu kurallar sadece kullanıcı çıkış istediğinde veya oturum sonunda uygulanır

## Dokümantasyon Kuralları

### 1. Merkezi Referans İlkesi
- Her bilginin tek bir "doğru yeri" olmalı
- Tekrar yerine referans kullanılmalı

### 2. Cross-Reference Zorunluluğu
- Dokümantasyonlar arası bağlantılar korunmalı
- Relatif path kullanılmalı: `[Link](./DOSYA.md#section)`
- Broken link olmamalı

### 3. Yeni Modül Eklendiğinde
- ÖNCE [CLAUDE_MODULES.md](./CLAUDE_MODULES.md) güncellenmeli
- Sonra diğer dokümanlarda referans verilmeli
- Teknik detaylar ilgili dokümana eklenmeli

## 📸 SCREENSHOT VE GÖREV TESLİM KURALLARI

### Screenshot Yönetimi - OTOMATİK SİSTEM
1. **Claude Tools Başlangıcı**: Claude tools açıldığında otomatik SS kontrolü yapılır
2. **screenshot_manager.py**: Tüm SS işlemleri bu modül tarafından yönetilir
3. **Otomatik Arşivleme**: 
   - Bulunan SS'ler otomatik olarak arşivlenir
   - Format: `vXXX_build_YYYYMMDD_HHMM_N.png`
   - Konum: `archive/media/screenshots/v061-current/`
4. **Manuel Kontrol**: Gerektiğinde `python3 src/screenshot_manager.py check` komutu kullanılabilir

### Görev Teslim Kontrol Listesi
1. ☑️ Screenshot kontrolü yapıldı mı?
2. ☑️ VERSION.json güncellendi mi?
3. ☑️ main.py versiyonu senkron mu?
4. ☑️ Archive dizini temiz mi?
5. ☑️ Tüm CLAUDE*.md dosyaları 30K limitinde mi?
6. ☑️ Git commit yapıldı mı? (istenmişse)

### Zorunlu Kontroller
```bash
# Her görev tesliminde bu komutları çalıştır:
ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'
grep '"version"' src/VERSION.json | head -1
du -sh CLAUDE*.md
```

## 📝 Claude İletişim Log Sistemi

### Log Dosyası Formatı - YENİ VERSİYON 
```
CLAUDE_COMMUNICATION_LOG_vXXX_to_vYYY_YYYYMMDD_HHMM.md
```
- **vXXX**: Başlangıç versiyonu
- **vYYY**: Bitiş versiyonu
- **YYYYMMDD_HHMM**: Log oluşturulma zamanı

### Log Kuralları - STRICT
1. **Maksimum 3 Log**: Ana dizinde en fazla SON 3 versiyon logu bulunur
2. **Otomatik Temizleme**: Yeni log oluşturulurken en eski log silinir (3'ten fazla varsa)
3. **Format**: CLAUDE_COMMUNICATION_LOG_vXXX_to_vYYY_YYYYMMDD_HHMM.md
4. **Silme Komutu**: `ls -t CLAUDE_COMMUNICATION_LOG_*.md | tail -n +4 | xargs rm -f`
5. **ARŞİV ZORUNLULUĞU**: Her versiyon arşivlenirken mevcut 3 log dosyası da arşive dahil edilir
6. **İçerik Zorunlu**:
   - Versiyon ve zaman bilgileri (İstanbul saati)
   - İletişim özeti
   - Kullanıcı istekleri (tam metin)
   - Yapılan işlemler
   - Test sonuçları
   - Kalan sorunlar

### Log İçeriği
- Versiyon bilgileri
- İletişim başlangıç/bitiş zamanı
- Ana konular
- Kritik sorunlar ve çözümler
- Kullanıcı istekleri
- Yapılan işlemler
- Test sonuçları
- Kalan sorunlar

### Log Arşivleme - YENİ KURAL 📁
- **ZORUNLU**: archive_version.py çalıştırıldığında tüm CLAUDE_COMMUNICATION_*.md dosyaları arşive kopyalanır
- **KONTROL**: Her arşivde mevcut 3 log dosyası bulunmalı
- **DOĞRULAMA**: `ls -la archive/versions/unibos_vXXX_*/CLAUDE_COMMUNICATION_*.md`
- **AMAÇ**: Geçmiş iletişimlerin kaybolmaması ve version history'de takip edilebilmesi

### Log Oluşturma Kuralı - YENİ 📝
- **YENİ LOG**: Her oturum sonunda yeni communication log oluşturulmalı
- **İSİMLENDİRME**: `CLAUDE_COMMUNICATION_LOG_vXXX_to_vYYY_YYYYMMDD_HHMM.md`
- **İÇERİK**: Başlangıç/bitiş versiyonları, yapılan işlemler, kullanıcı istekleri
- **OTOMATİK TEMİZLİK**: 3'ten fazla log varsa en eskiler silinir

### Log Yönetimi Script
```bash
# Güncel log'u kontrol et
ls -la CLAUDE_COMMUNICATION_*.log

# Log boyutunu kontrol et
du -sh CLAUDE_COMMUNICATION_*.log

# Son log girişini görüntüle
tail -n 20 CLAUDE_COMMUNICATION_*.log

# Arşivdeki logları kontrol et
ls -la archive/versions/unibos_v*/CLAUDE_COMMUNICATION_*.log | tail -10
```

## 📸 Screenshot Arşiv Düzeni (100'lük Gruplar)

### Yeni Dizin Yapısı
```
archive/media/screenshots/
├── v001-099/      # v001'den v099'a kadar
├── v100-199/      # v100'den v199'a kadar
├── v200-299/      # v200'den v299'a kadar
└── ...            # 100'lük gruplar halinde devam eder
```

### Screenshot İsimlendirme - ZORUNLU FORMAT
```
unibos_vXXX_build_YYYYMMDD_HHMM_N.png
```
- **unibos_** prefixi ZORUNLU
- **vXXX**: 3 haneli versiyon numarası (v001, v099, v143)
- **build_YYYYMMDD_HHMM**: İstanbul saatiyle build zamanı
- **N**: Aynı build'de birden fazla SS varsa sıra numarası

### Arşivleme Kuralları - FORCED
1. **Ana Dizin Kontrolü**: Her Claude mesajında İLK İŞ screenshot kontrolü
2. **Otomatik Arşivleme**: SS bulunursa → Oku → Analiz → İsimlendir → Arşivle
3. **100'lük Gruplar**: v001-099, v100-199, v200-299...
4. **Analiz Zorunluluğu**: Her SS'in içeriği mutlaka analiz edilmeli
5. **Veri Kaybı Yasak**: Hiçbir SS silinmez, sadece taşınır

### Screenshot Kontrol Script - HER MESAJDA ÇALIŞTIR
```bash
# 1. Ana dizin SS kontrolü (İLK İŞ!)
echo "=== Screenshot Kontrolü ==="
ss_count=$(ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$' | wc -l)
if [ $ss_count -gt 0 ]; then
    echo "⚠️ $ss_count adet screenshot bulundu!"
    ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'
else
    echo "✅ Ana dizinde screenshot yok"
fi

# 2. Screenshot arşiv durumu
echo -e "\n=== Arşiv Durumu ==="
for dir in archive/media/screenshots/v*/; do
    count=$(ls -1 "$dir"/*.png 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "$dir: $count screenshot"
    fi
done
```

### 10. Claude Tools Öneri Güncelleme Kuralı - YENİ 🔄

**ZORUNLU**: Claude tools'ta update suggestions yapıldığında ve öneriler kaydedildiğinde:

1. **Otomatik Yenileme**: save_suggestions_to_file() çağrıldığında öneriler CLAUDE_SUGGESTIONS.md'ye yazılır
2. **Menü Güncellemesi**: Güncelleme sonrası show_claude_tools_menu() yeniden çağrılarak menüdeki öneriler güncellenir
3. **Öneri Sayısı**: Claude tools menüsünde ilk 10 öneri gösterilir (önceden 5'ti)
4. **Dinamik Güncelleme**: Kullanıcı her update suggestions yaptığında menüdeki öneriler otomatik güncellenir

**Uygulama**:
- update_suggestions() fonksiyonu sonunda menü yenilenir
- save_suggestions_to_file() ile yeni öneriler dosyaya yazılır
- load_suggestions_from_file() ile güncel öneriler yüklenir
- Kullanıcı her zaman en güncel önerileri görür

### 11. Kronikleşen Sorunlar İçin Otomatik Tespit ve Araştırma Protokolü 🔍

**ZORUNLU**: Claude her oturum başında kronikleşen sorunları otomatik tespit etmeli:

#### Otomatik Kronik Sorun Tespiti - HER OTURUM BAŞINDA
**KRİTİK**: Bu kontrol CLAUDE.md'deki başlangıç scriptine eklenmiştir ve her Claude oturumunda otomatik çalışır.

```python
# Claude her oturum başında bu kontrolü yapar
def check_chronic_issues():
    """Kronikleşen sorunları tespit et ve kullanıcıya bildir"""
    import re
    from pathlib import Path
    
    # Son 3 communication log'u oku
    comm_logs = sorted(Path('.').glob('CLAUDE_COMMUNICATION_LOG_*.md'), 
                      key=lambda x: x.stat().st_mtime, reverse=True)[:3]
    
    # Sorun pattern'lerini say
    issue_patterns = {
        'menu_navigation': ['navigasyon', 'menu', 'arrow', 'tuş', 'key', 'navigate'],
        'timeout': ['timeout', 'zaman aşımı', 'claude timeout'],
        'crash': ['crash', 'çöktü', 'hata', 'error'],
        'performance': ['yavaş', 'slow', 'performans', 'performance']
    }
    
    chronic_issues = {}
    
    for log in comm_logs:
        content = log.read_text(encoding='utf-8').lower()
        for issue, patterns in issue_patterns.items():
            for pattern in patterns:
                if pattern in content and 'çözüldü' not in content:
                    chronic_issues[issue] = chronic_issues.get(issue, 0) + 1
    
    # 2'den fazla log'da geçen sorunları bildir
    for issue, count in chronic_issues.items():
        if count >= 2:
            print(f"⚠️ Kronik sorun tespit edildi: {issue} ({count} log'da mevcut)")
            if issue == 'menu_navigation':
                print("📋 Menu navigasyon sorunu kronikleşmiş. Bu sorun aşıldı mı yoksa hala devam ediyor mu?")
                print("   Lütfen test edip geri bildiriminizi paylaşınız.")
```

**ZORUNLU**: Bir sorun 3 versiyondan fazla devam ediyorsa aşağıdaki adımları uygula:

#### Araştırma Sıralaması:
1. **Communication Log Taraması**:
   ```bash
   # Son 5 comm log'da sorunla ilgili pattern ara
   grep -n "navigasyon\|arrow\|tuş\|key" CLAUDE_COMMUNICATION_LOG_*.md | tail -20
   ```

2. **Changelog Analizi**:
   ```bash
   # CHANGELOG.md'de sorunla ilgili girişleri bul
   grep -A3 -B3 "Arrow\|Navigation\|Key" CHANGELOG.md
   ```

3. **Çalışan Versiyon Tespiti**:
   ```bash
   # Arşivdeki versiyonlarda çalışan kodu ara
   for v in archive/versions/unibos_v*/; do
       echo "=== Checking $v ==="
       grep -n "def get_single_key" "$v/src/main.py" | head -5
   done
   ```

4. **Diff Analizi**:
   ```bash
   # İki versiyon arasındaki farkları kontrol et
   diff -u archive/versions/unibos_vXXX/src/main.py src/main.py | grep -C5 "pattern"
   ```

#### Dokümantasyon Araması:
- CLAUDE_VERSION.md'de "Fixed" vs "Still broken" pattern'leri
- Debug log'larından hata pattern'leri
- Screenshot'lardan görsel kanıtlar

#### Çözüm Stratejisi:
1. En son çalışan versiyonu bul
2. Mevcut kodla karşılaştır
3. Kritik farkları tespit et
4. Minimal değişiklikle düzelt
5. Test et ve dokümante et

### 12. Arşiv Boyut Kontrolü ve Güvenlik 📦

**KRİTİK**: Her arşivleme öncesi ve sonrası boyut kontrolü yapılmalı.

#### Pre-Archive Kontrolü:
```python
def check_archive_size_anomaly(self) -> bool:
    """Arşiv boyut anomalisi kontrolü"""
    # Son 5 arşivin boyutunu al
    recent_archives = sorted(self.compressed_dir.glob("*.zip"))[-5:]
    if len(recent_archives) < 2:
        return True  # Yeterli veri yok, devam et
    
    sizes = [a.stat().st_size for a in recent_archives]
    avg_size = sum(sizes) / len(sizes)
    
    # Mevcut dizin boyutu
    current_size = sum(f.stat().st_size for f in Path('.').rglob('*') 
                      if f.is_file() and 'archive' not in str(f))
    
    # %50'den fazla büyüme/küçülme varsa uyar
    if abs(current_size - avg_size) / avg_size > 0.5:
        print(f"⚠️ UYARI: Arşiv boyutu anomalisi tespit edildi!")
        print(f"   Ortalama: {avg_size/1024/1024:.1f} MB")
        print(f"   Mevcut: {current_size/1024/1024:.1f} MB")
        response = input("Devam edilsin mi? (y/N): ")
        return response.lower() == 'y'
    return True
```

#### Arşiv İçi Arşiv Kontrolü:
```bash
# Her arşivde archive/ dizini kontrolü
for zip in archive/compressed/*.zip; do
    if unzip -l "$zip" | grep -q "archive/"; then
        echo "❌ HATA: $zip içinde archive/ dizini var!"
    fi
done
```

#### Otomatik Temizlik:
- Versiyonlamadan önce `rm -rf archive/` komutu YASAK
- Sadece belirli pattern'ler temizlenebilir:
  - `__pycache__/`
  - `*.pyc`
  - `.DS_Store`
  - `node_modules/`
  - `.venv/`

---
*Teknik detaylar için [CLAUDE_TECH.md](./CLAUDE_TECH.md) dosyasına bakın.*
*Son güncelleme: 2025-07-17 18:08:00 +03:00*