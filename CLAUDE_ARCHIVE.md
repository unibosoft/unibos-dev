# CLAUDE_ARCHIVE.md - Arşiv Yönetimi ve Kurallar

> **📂 NOT**: Bu dosya arşiv yönetim kurallarını içerir. Ana yönetim için [CLAUDE.md](./CLAUDE.md) dosyasına bakın.

## 📂 Arşiv Yönetimi

### Arşiv Organizasyon Kuralları

1. **Dizin Yapısı**
   - `archive/` dizini tüm geçmiş versiyonları ve medya dosyalarını içerir
   - Düzenli ve hiyerarşik yapı korunmalıdır
   - Her kategori için ayrı alt dizin kullanılır

2. **Versiyon Arşivleme**
   - Açık versiyonlar: `archive/versions/` (sadece versiyon klasörleri)
   - **Klasör İsimlendirme Kuralı**: `unibosoft_vXXX_YYYYMMDD_HHMM` formatı
     - Örnek: `unibosoft_v062_20250715_1808`
     - **KRİTİK**: Tüm versiyon klasörleri aynı formatta olmalı
   - Gereksiz duplikasyonlar ve eski dosyalar temizlenir

3. **Medya Dosyaları**
   - Ekran görüntüleri versiyon aralıklarına göre gruplandırılır
   - Diyagramlar ayrı klasörde saklanır
   - Dosya isimlendirme formatı: `vXXX_build_YYYYMMDD_HHMM_N.png`
   - **KRİTİK**: Ana dizindeki tüm screenshot'lar MUTLAKA arşivlenmelidir
   - Screenshot'lar asla ana dizinde bırakılmamalıdır

4. **Dokümantasyon Merkezi**
   - Tüm güncel dokümantasyon ana dizinde: CLAUDE*.md, README.md, LLM_COMPREHENSIVE_GUIDE.md
   - Eski dokümantasyon kaldırıldı (bilgi kaybı olmadan ana dosyalara entegre edildi)

5. **Raporlar**
   - LLM etkileşim raporları: `archive/reports/llm-reports/`
   - Performans testleri: `archive/reports/performance/`
   - Güvenlik denetimleri: `archive/reports/security/`

6. **Temizlik Kuralları**
   - __MACOSX klasörleri silinir
   - Duplike ZIP dosyaları temizlenir
   - Boş klasörler kaldırılır
   - `archive/versions/` altında SADECE versiyon klasörleri bulunur
   - **Versiyon klasör isimleri standart formatta**: `unibosoft_vXXX_YYYYMMDD_HHMM`
   - README.md ile kullanım rehberi sağlanır

7. **Arşiv Klasörü İçeriği - KRİTİK**
   - **archive/versions/**: Sadece açık versiyon klasörleri bulunmalı
     - Her klasör bir versiyonu temsil etmeli
     - İçlerinde archive/ dizini OLMAMALI
   - **KONTROL KOMUTU**: 
     ```bash
     # Archive içinde archive olup olmadığını kontrol et
     find archive/ -name "archive" -type d
     # Bu komut boş dönmeli
     ```

8. **Version Manager Script Kuralları**
   - Yeni versiyon oluştururken eski versiyondaki archive/ dizini HARİÇ tutulmalı
   - ZIP oluştururken: `--exclude="archive/"` parametresi kullanılmalı
   - Klasör kopyalarken: archive/ dizini kopyalanmamalı

## 🚨 Arşiv Silme Yasağı - EN KRİTİK KURAL

**ARŞİVLER ASLA SİLİNMEZ**

- **YASAK**: archive/versions/ içindeki hiçbir versiyon klasörü SİLİNEMEZ
- **YASAK**: Eski versiyonlar "temizlik" adı altında KALDIRILAMAZ
- **KORUMA**: Tüm geçmiş versiyonlar korunmalıdır (v001'den güncel versiyona kadar)
- **HATA**: Bu kural ihlal edilirse tüm proje geçmişi kaybedilebilir
- **BACKUP**: Arşivler projenin hafızasıdır ve MUTLAKA korunmalıdır
- **İSTİSNA**: SADECE duplike veya bozuk dosyalar kullanıcı onayı ile silinebilir
- **KONTROL**: Her oturumda arşiv bütünlüğü kontrol edilmeli: `ls -la archive/versions/ | wc -l`
- **UYARI**: "Temizlik" yaparken bile arşivlere DOKUNULMAMALI
- **KRİTİK**: Bu kural TÜM diğer kurallardan önceliklidir

## Arşiv Yedekleme Kuralları - ZORUNLU

Her versiyon değişiminde MUTLAKA uygulanmalı:

### Versions Yedekleme
`archive/versions/unibos_vXXX_YYYYMMDD_HHMM/`
- Dizin kopyası tüm proje dosyalarını içermeli
- **KRİTİK KURAL**: archive/ dizini ASLA kopyalanmamalı (iç içe arşiv önleme)
- **YASAK**: Versiyon klasörünün içinde archive/ bulunması
- HARIÇ TUTULACAKLAR: archive/, .git/, venv/, __pycache__/, *.pyc, .DS_Store
- Komut: `rsync -av --exclude='archive' --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' . "archive/versions/unibos_vXXX_YYYYMMDD_HHMM/"`

### Doğrulama Kontrolleri
Her yedekleme sonrası ZORUNLU:
- Dizin kopyası tam mı? `ls -la archive/versions/unibos_vXXX*/`
- **KRİTİK**: Archive dizini kopyalanmış mı? `find archive/versions -name "archive" -type d` (SONUÇ BOŞ OLMALI)

### Boyut Kontrolü - KRİTİK
Versiyon klasör boyutları kontrol edilmeli:
- Normal boyut aralığı: 10MB - 50MB (venv ve .git hariç)
- **UYARI SİNYALLERİ**:
  - İçinde archive/ klasörü varsa: KESİNLİKLE hatalı
  - İçinde venv/ veya node_modules/ varsa: Temizlenmeli
- **Kontrol Komutları**:
  ```bash
  # Archive klasörü kontrolü
  find archive/versions -name "archive" -type d
  # Bu komut BOŞ dönmeli, herhangi bir çıktı varsa HATA
  ```

---

## Güncel Arşiv Durumu (v121)

### Versiyonlar
- **Açık versiyonlar**: `archive/versions/`
- **Son eklenen**: unibos_v173_*

### v121 Değişiklikleri
- 📝 **Logging Sistemi**: unibos_logger.py ile merkezi log yönetimi
- 🔧 **Error Handling**: Claude CLI'ye detaylı hata yakalama eklendi
- 🎯 **Exit Protokolü**: Claude exit menüsü düzeltildi
- 📦 **Arşivleme**: Sadece versions arşivleri kullanılıyor

### Versiyon Oluşturma Kuralı - MUTLAKA UYULMALIDIR

⚠️ **KRİTİK UYARI**: Kökteki `/archive` klasörü HER ZAMAN KALMALIDIR!

🔄 **Duplikasyon Önleme Kuralı**: 
- Eğer archive içinde archive oluşacaksa (archive/versions/vXXX/archive gibi)
- Önce geçici olarak taşınır, arşivleme yapılır, sonra geri alınır
- Böylece iç içe archive klasrü oluşmaz

Her yeni versiyon oluşturulduğunda:

1. **Arşiv Klasrünü Oluştur**:
   ```bash
   mkdir -p archive/versions/unibos_vXXX_YYYYMMDD_HHMM
   ```

2. **Dosyaları Kopyala** (archive dizini HARİÇ):
   ```bash
   rsync -av --exclude='archive' --exclude='.git' --exclude='venv' \
             --exclude='src/venv' --exclude='__pycache__' \
             --exclude='*.pyc' --exclude='.DS_Store' \
             . "archive/versions/unibos_vXXX_YYYYMMDD_HHMM/"
   ```

3. **Arşiv Doğrulaması**:
   ```bash
   # Archive dizini kontrolü (BOŞ dönmeli)
   find archive/versions/unibos_vXXX_* -name "archive" -type d
   ```

4. **Doğrulama**:
   ```bash
   # Archive dizini kontrolü (BOŞ dönmeli)
   find archive/versions -name "archive" -type d
   
   # Versiyon klasörü kontrolü
   ls -la archive/versions/unibos_vXXX*/
   ```

---
*Güncel durum için [CLAUDE_VERSION.md](./CLAUDE_VERSION.md) dosyasına bakın.*
*Son güncelleme: 2025-07-16 17:50:00 +03:00*