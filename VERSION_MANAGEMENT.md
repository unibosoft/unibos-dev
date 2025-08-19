# UNIBOS Version Management System

## 🔗 Quick Links
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) - Change tracking
- [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md) - Archive protocols

## 🎯 Unified Version Manager

UNIBOS artık tek bir optimize edilmiş versiyon yönetim scripti kullanıyor:

```bash
./unibos_version.sh
```

## ✨ Özellikler

### 1. **Quick Release** (Hızlı Yayın)
- Otomatik versiyon numarası hesaplama
- VERSION.json güncelleme
- Django dosyaları güncelleme
- Arşiv oluşturma
- Git branch, tag ve push işlemleri

### 2. **Status Check** (Durum Kontrolü)
- VERSION.json ve git tag senkronizasyonu
- Eksik versiyon tespiti
- Son versiyonları listeleme

### 3. **Manual Version** (Manuel Versiyon)
- İstediğiniz versiyon numarasını belirtme
- Özel açıklama ekleme

### 4. **Fix Version Sync** (Senkronizasyon Düzeltme)
- VERSION.json'ı git tag'leriyle hizalama
- Versiyon uyumsuzluklarını düzeltme

### 5. **Archive Only** (Sadece Arşivleme)
- Git işlemleri olmadan arşiv oluşturma
- Test ve yedekleme için

### 6. **Cleanup Old Archives** (Eski Arşiv Temizliği)
- Disk alanı yönetimi
- İstediğiniz sayıda son versiyon saklama

## 🚀 Kullanım Örnekleri

### Hızlı Yayın
```bash
./unibos_version.sh
# Seçim: 1
# Açıklama girin: Fixed navigation bug
```

### Durum Kontrolü
```bash
./unibos_version.sh
# Seçim: 2
```

### Manuel Versiyon
```bash
./unibos_version.sh
# Seçim: 3
# Versiyon: 451
# Açıklama: Major update
```

## 📁 Dosya Yapısı

```
unibos/
├── unibos_version.sh        # Ana versiyon yönetim scripti
├── src/VERSION.json         # Versiyon bilgileri
├── archive/
│   ├── versions/           # Açık arşivler
│   └── compressed/         # ZIP arşivleri
└── scripts/legacy/         # Eski scriptler (yedek)
    ├── git_version_push.sh
    ├── update_version.sh
    ├── version_manager.sh
    └── safe_version_manager.sh
```

## 🔧 Özellikler

### Otomatik İşlemler
- ✅ Versiyon numarası hesaplama
- ✅ Git tag kontrolü
- ✅ Eksik versiyon tespiti
- ✅ VERSION.json güncelleme
- ✅ Django dosyaları güncelleme
- ✅ Arşiv oluşturma (açık + ZIP)
- ✅ Git branch oluşturma
- ✅ Git tag oluşturma
- ✅ GitHub'a push

### Güvenlik Kontrolleri
- ✅ Versiyon çakışma kontrolü
- ✅ Eksik versiyon uyarısı
- ✅ Git status kontrolü
- ✅ Dosya varlık kontrolü

## 🎨 Renk Kodları

- 🔵 **Mavi**: Bilgi mesajları
- 🟢 **Yeşil**: Başarılı işlemler
- 🟡 **Sarı**: Uyarılar ve kullanıcı girdisi
- 🔴 **Kırmızı**: Hatalar
- 🟦 **Cyan**: Başlıklar

## 📊 Performans İyileştirmeleri

### Eski Sistem (4 script)
- Toplam: ~20KB kod
- 674 satır
- Tekrarlanan fonksiyonlar
- Manuel senkronizasyon

### Yeni Sistem (1 script)
- Toplam: ~8KB kod
- 330 satır
- Optimize fonksiyonlar
- Otomatik senkronizasyon
- %60 daha az kod
- %100 daha fazla özellik

## 🛠️ Gereksinimler

- Bash 4.0+
- Git 2.0+
- Python 3.8+
- rsync
- zip

## 📝 Notlar

- Eski scriptler `scripts/legacy/` klasöründe yedeklendi
- Tüm işlemler Istanbul saat dilimine göre yapılır
- Arşivler otomatik olarak tarih damgası alır
- Git işlemleri atomiktir (ya hepsi ya hiçbiri)

## 🆘 Sorun Giderme

### Versiyon Uyumsuzluğu
```bash
./unibos_version.sh
# Seçim: 4 (Fix Version Sync)
```

### Disk Alanı Sorunu
```bash
./unibos_version.sh
# Seçim: 6 (Cleanup Old Archives)
```

### Manuel Düzeltme
```bash
# VERSION.json'ı manuel düzenle
nano src/VERSION.json

# Git tag'lerini kontrol et
git tag | sort -V

# Eksik tag ekle
git tag v450
git push origin --tags
```

## 📈 İstatistikler

- Ortalama yayın süresi: 15 saniye
- Arşiv boyutu: ~50-200MB
- Git işlem süresi: 5-10 saniye
- Toplam işlem: 8 adım

## 🔄 Version Management Workflow

### Standard Release Process
1. Update DEVELOPMENT_LOG.md with changes
2. Run `./unibos_version.sh` and select Quick Release
3. System automatically:
   - Increments version number
   - Updates VERSION.json
   - Creates archive
   - Commits to git
   - Pushes with tags

### Integration with Other Systems
- **CLI Integration**: Version manager accessible from main CLI
- **Web Dashboard**: Version statistics viewable in web UI
- **Archive System**: Automatic archiving with each release
- **Git Integration**: Automatic tagging and pushing

---

**Son Güncelleme**: 2025-08-12
**Yazar**: Berk Hatırlı
**Versiyon**: 2.0