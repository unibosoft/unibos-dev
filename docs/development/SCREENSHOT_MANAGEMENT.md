# 📸 SCREENSHOT MANAGEMENT PROTOCOL

> **Amaç:** Screenshot'ların otomatik tespiti, işlenmesi ve arşivlenmesi için standart prosedürler.
> **Ref:** [CLAUDE_SESSION_PROTOCOL.md](CLAUDE_SESSION_PROTOCOL.md) - Oturum protokolü

---

## 🎯 GENEL PRENSİPLER

### Screenshot Neden Önemli?

Berk sıklıkla:
- Hata ekranları
- UI değişiklik talepleri
- Tasarım önerileri
- Bug raporları

...için screenshot paylaşır. Bu screenshot'ları **derhal tespit edip işlemek** kritiktir.

### Temel Kurallar

1. **Her oturum başında screenshot kontrolü ZORUNLU**
2. **Screenshot varsa ÖNCE onu işle, sonra diğer tasklara geç**
3. **Istanbul timezone kullan (Europe/Istanbul, UTC+3)**
4. **İşlendikten sonra arşivle ve temizle**
5. **DEVELOPMENT_LOG.md'ye kaydet**

---

## 🔍 SCREENSHOT TESPİTİ (Detection)

### Oturum Başında Otomatik Tespit

```bash
# Ana dizinde screenshot ara
ls -la *.png Screenshot*.png 2>/dev/null

# Muhtemel dosya isimleri:
# - Screenshot*.png
# - screenshot*.png
# - Screen Shot*.png
# - SS_*.png
# - [Tarih]*.png
```

**Pozitif Tespit:** Dosya varsa → [İşleme Workflow](#-screenshot-i̇şleme-workflow) başlat

**Negatif Tespit:** Dosya yoksa → Normal oturuma devam et

### Tespit Sonrası Kullanıcıya Bildirim

```
Merhaba Berk! 👋

✅ Projeyi taradım ve hazırım.
📸 Screenshot: VAR - Screenshot_2025-11-09_14-30-45.png (işleme hazır)
⏰ Istanbul: 2025-11-09 14:30:45 +0300
🔧 Git status: Clean
📌 Version: v531

Screenshot'ı işleyebilirim ya da başka bir task verebilirsin. Ne yapmamı istersin?
```

---

## 🔄 SCREENSHOT İŞLEME WORKFLOW

### Adım 1: Screenshot İnceleme

```bash
# Screenshot'ı oku ve analiz et
# (Claude Code Read tool ile görsel içeriği görebilir)
```

**Analiz Et:**
- Ne gösteriyor? (Hata, UI, tasarım, vb.)
- Hangi modül/sayfa ile ilgili?
- Acil mi, yoksa planlı geliştirme mi?

### Adım 2: Kullanıcıya Ön Rapor

```
📸 Screenshot Analizi:

🔍 İçerik: [Kısa açıklama]
📍 İlgili Modül: [Modül adı]
⚠️ Öncelik: [Yüksek/Normal/Düşük]

🎯 Önerilen Aksiyon:
- [Aksiyon 1]
- [Aksiyon 2]

Devam edeyim mi?
```

### Adım 3: İşlem Gerçekleştirme

Kullanıcı onayı sonrası:
- Hata düzeltme
- UI değişikliği
- Kod review
- Tasarım implementasyonu
- ...vb.

### Adım 4: Arşivleme

İşlem tamamlandıktan sonra:

```bash
# Istanbul timezone ile timestamp oluştur
TIMESTAMP=$(TZ='Europe/Istanbul' date '+%Y%m%d_%H%M%S')

# Arşiv dizini oluştur (yoksa)
mkdir -p archive/media/screenshots/

# Screenshot'ı yeniden adlandır ve taşı
mv [orijinal_dosya_adi].png "archive/media/screenshots/screenshot_${TIMESTAMP}.png"

# Örnek:
# mv Screenshot_2025-11-09_14-30-45.png archive/media/screenshots/screenshot_20251109_143045.png
```

**Dosya İsimlendirme Kuralı:**
```
screenshot_YYYYMMDD_HHMMSS.png

Örnek: screenshot_20251109_143045.png
```

### Adım 5: Development Log Kaydı

```bash
./tools/scripts/add_dev_log.sh \
  "[Kategori]" \
  "[Başlık]" \
  "Screenshot analizi: [özet]. İşlem: [yapılan]. Sonuç: [sonuç]." \
  "Screenshot arşivlendi: screenshot_${TIMESTAMP}.png"
```

**Örnek:**

```bash
./tools/scripts/add_dev_log.sh \
  "Bug Fix" \
  "Doküman detay sayfası crash hatası düzeltildi" \
  "Screenshot analizi: Document detail sayfasında null reference hatası. İşlem: apps/web/backend/apps/documents/views.py:245'te null check eklendi. Sonuç: Hata giderildi, testler geçti." \
  "Screenshot arşivlendi: screenshot_20251109_143045.png"
```

### Adım 6: Kullanıcıya Sonuç Raporu

```
✅ Screenshot İşlendi!

📋 Özet:
- İşlem: [Yapılan]
- Dosyalar: [Değiştirilen dosyalar]
- Commit: [Commit hash veya "Henüz commit edilmedi"]

📸 Arşiv: screenshot_20251109_143045.png
📝 Log: DEVELOPMENT_LOG.md güncellendi

🔜 Sonraki Adım:
[Öneri varsa]
```

---

## 📂 ARŞİV YAPISI

### Dizin Yapısı

```
archive/
  └── media/
      └── screenshots/
          ├── screenshot_20251109_143045.png
          ├── screenshot_20251109_150230.png
          ├── screenshot_20251108_091512.png
          └── ...
```

### Arşiv Kuralları

1. **Konum:** `archive/media/screenshots/`
2. **Format:** `screenshot_YYYYMMDD_HHMMSS.png`
3. **Timezone:** Istanbul (Europe/Istanbul, UTC+3)
4. **Retention:** Sınırsız (manuel temizleme gerekebilir)

### .archiveignore ve .gitignore

Screenshot'lar `.archiveignore` ve `.gitignore` tarafından **HARIÇ TUTULUYOR**:

**Neden?**
- Version archive'lerini şişirmemek için
- Git repository boyutunu küçük tutmak için
- Screenshot'lar geliştirme arşivi, kaynak kod değil

**Mevcut Kurallar:**
```bash
# .archiveignore ve .gitignore'da:
/archive/media/screenshots/
```

---

## 🚨 ÖZEL DURUMLAR

### Durum 1: Çoklu Screenshot

Birden fazla screenshot varsa:

```bash
# Tüm screenshot'ları listele
ls -la *.png Screenshot*.png Screen*.png 2>/dev/null

# Her birini sırayla işle
# İsimlendirme: screenshot_YYYYMMDD_HHMMSS_01.png, _02.png, vb.
```

**Kullanıcıya bildir:**
```
📸 Çoklu Screenshot Tespit Edildi!

Bulunan: 3 dosya
- Screenshot_A.png
- Screenshot_B.png
- Screenshot_C.png

Hepsini sırayla mı işleyelim, yoksa hangisini önceliklendirelim?
```

### Durum 2: Screenshot Bulunamadı (False Positive)

Eğer kullanıcı "screenshot'ı işle" dedi ama dosya yoksa:

```
⚠️ Screenshot Bulunamadı!

Ana dizinde screenshot dosyası tespit edemedim.

📁 Kontrol edilen konumlar:
- *.png
- Screenshot*.png
- Screen Shot*.png

Screenshot başka bir konumda mı? Tam yolu verebilir misin?
```

### Durum 3: Bozuk/Okunamaz Screenshot

```
❌ Screenshot Okunamıyor!

Dosya var ancak içeriği okunamıyor (bozuk dosya?).

🔧 Öneriler:
- Dosyayı yeniden kaydet ve paylaş
- Farklı format dene (PNG, JPG)
- Manuel olarak ne gösterdiğini açıkla
```

### Durum 4: Screenshot'a Bağlı Olmayan Task

Eğer kullanıcı screenshot dışında bir task verirse:

```
📸 Not: Screenshot tespit edildi ancak işlenmedi.

Mevcut task: [User'ın istediği]

Screenshot'ı şimdi işlemek ister misin, yoksa bu task'i bitirdikten sonra mı?
```

---

## ✅ CHECKLIST: Screenshot İşleme

### Tespit Aşaması
- [ ] Oturum başında `ls -la *.png Screenshot*.png` çalıştırdım
- [ ] Screenshot bulundu → Kullanıcıya bildirdim
- [ ] Screenshot yok → Normal oturuma devam ettim

### İşlem Aşaması
- [ ] Screenshot'ı Read tool ile okudum
- [ ] İçeriği analiz ettim
- [ ] Kullanıcıya ön rapor verdim
- [ ] Kullanıcı onayını aldım
- [ ] İlgili işlemi gerçekleştirdim

### Arşivleme Aşaması
- [ ] Istanbul timezone ile timestamp oluşturdum
- [ ] `archive/media/screenshots/` dizinini kontrol ettim/oluşturdum
- [ ] Screenshot'ı `screenshot_YYYYMMDD_HHMMSS.png` formatında yeniden adlandırdım
- [ ] Arşiv dizinine taşıdım
- [ ] DEVELOPMENT_LOG.md güncelledim
- [ ] Kullanıcıya sonuç raporu verdim

---

## 🔗 İLGİLİ DOSYALAR

- **[CLAUDE_SESSION_PROTOCOL.md](CLAUDE_SESSION_PROTOCOL.md)** ← Oturum protokolü
- **[CODE_QUALITY_STANDARDS.md](CODE_QUALITY_STANDARDS.md)** ← Kod standartları
- **[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)** ← Geliştirme logu
- **[RULES.md](../../RULES.md)** ← Ana kurallar

---

## 📝 ÖRNEKLER

### Örnek 1: Hata Screenshot'ı

**Tespit:**
```bash
$ ls -la *.png
Screenshot_Error_2025-11-09.png
```

**Analiz:**
```
📸 Screenshot Analizi:

🔍 İçerik: Django 500 error - Document detail sayfası
📍 İlgili Modül: apps/web/backend/apps/documents/views.py
⚠️ Öncelik: Yüksek (Production hatası)

🎯 Önerilen Aksiyon:
- views.py:245'te null reference kontrolü ekle
- Test yaz ve çalıştır
- Fix commit et

Devam edeyim mi?
```

**İşlem:**
- Kod düzeltildi
- Test yazıldı
- Commit yapıldı

**Arşivleme:**
```bash
TIMESTAMP=$(TZ='Europe/Istanbul' date '+%Y%m%d_%H%M%S')
# 20251109_143045

mv Screenshot_Error_2025-11-09.png \
   "archive/media/screenshots/screenshot_${TIMESTAMP}.png"
```

**Log:**
```bash
./tools/scripts/add_dev_log.sh \
  "Bug Fix" \
  "Document detail null reference hatası" \
  "Screenshot analizi: 500 error null reference. Fix: views.py:245 null check. Test: passed." \
  "Screenshot arşivlendi: screenshot_20251109_143045.png"
```

### Örnek 2: UI Değişiklik Talebi

**Tespit:**
```bash
$ ls -la Screen*.png
Screen Shot 2025-11-09 at 15.30.45.png
```

**Analiz:**
```
📸 Screenshot Analizi:

🔍 İçerik: Doküman listesi - header tasarımı değişiklik önerisi
📍 İlgili Modül: templates/documents/document_list.html
⚠️ Öncelik: Normal (UI iyileştirme)

🎯 Önerilen Aksiyon:
- Header'a search bar ekle
- Filtre butonlarını sağ tarafa taşı
- CSS düzenlemesi yap

Devam edeyim mi?
```

**İşlem:**
- Template güncellendi
- CSS eklendi
- Preview gönderildi

**Arşivleme ve Log:** *(yukarıdaki ile aynı prosedür)*

---

## 📊 METRİKLER VE TAKİP

### İstatistikler

```bash
# Screenshot arşivinde kaç dosya var?
ls -1 archive/media/screenshots/ | wc -l

# En son screenshot ne zaman?
ls -lt archive/media/screenshots/ | head -2

# Bu ayki screenshot'lar
ls -1 archive/media/screenshots/screenshot_202511* | wc -l
```

### Periyodik Temizlik

**Önerilmiyor** ancak gerekirse:

```bash
# 6 aydan eski screenshot'ları silmek için:
find archive/media/screenshots/ -name "screenshot_*.png" -mtime +180 -delete
```

**Not:** Kullanıcıya danış önce!

---

## 📝 Son Güncelleme

**Tarih:** 2025-11-09
**Değişiklik:** İlk oluşturma - Screenshot yönetim protokolü standardize edildi
**Neden:** Screenshot tespit, işleme ve arşivleme sürecinin otomasyonu

---

**⬆️ Üst Dosya:** [CLAUDE_SESSION_PROTOCOL.md](CLAUDE_SESSION_PROTOCOL.md)
