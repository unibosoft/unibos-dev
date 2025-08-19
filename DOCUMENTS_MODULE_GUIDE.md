# 📄 UNIBOS Documents Module - Kullanım Kılavuzu

## 🚀 Başlangıç

### Modülü Çalıştırma
```bash
cd /Users/berkhatirli/Desktop/unibos
python3 src/main.py
```

### Documents Modülüne Erişim
1. Ana menüde arrow keys ile **"📄 documents"** seçin
2. **Enter** veya **sağ ok (→)** tuşuna basın
3. Content alanında documents menüsü açılacak

## 📋 Menü Seçenekleri

### 1. 📁 Browse Documents
**Ne yapar:** Tüm belgeleri listeler ve yönetir
- Belge dizini: `~/Documents/unibos_documents/`
- Dosya boyutu, değiştirilme tarihi gösterir
- İlk 20 dosyayı listeler
- Dosya tiplerine göre ikonlar (PDF 📕, Image 🖼️, Word 📝, Excel 📊)

**Kullanım:**
- Menüde **1** tuşuna basın veya arrow ile seçip Enter
- Belgeler otomatik listelenir
- Herhangi bir tuşa basarak geri dönün

### 2. 🔍 Search Documents
**Ne yapar:** Belgelerde tam metin araması yapar
- Dosya adlarında arama
- Metin dosyalarının içeriğinde arama (.txt, .md, .json, .csv)
- İlk 10 sonucu gösterir

**Kullanım:**
- Menüde **2** tuşuna basın
- Arama terimini girin (örn: "fatura", "2024")
- Sonuçlar otomatik gösterilir

### 3. 📤 Upload Documents
**Ne yapar:** Yeni belge yükler
- Herhangi bir dosyayı documents klasörüne kopyalar
- Tam dosya yolu destekler (~/ kısayolu çalışır)

**Kullanım:**
- Menüde **3** tuşuna basın
- Dosya yolunu girin (örn: `~/Desktop/belge.pdf`)
- Dosya otomatik kopyalanır

### 4. 📸 OCR Scanner
**Ne yapar:** Görüntülerden metin çıkarır (OCR)
- PNG, JPG, JPEG, TIFF, BMP destekler
- Türkçe ve İngilizce metin tanıma
- Çıkarılan metni .txt dosyasına kaydeder

**Gereksinimler:**
```bash
pip install pytesseract pillow
brew install tesseract  # macOS
# veya
sudo apt-get install tesseract-ocr  # Linux
```

**Kullanım:**
- Menüde **4** tuşuna basın
- Görüntü dosya yolunu girin
- OCR işlemi otomatik başlar
- Metin aynı dizinde .txt olarak kaydedilir

### 5. 🧾 Invoice Processor
**Ne yapar:** Faturaları AI ile işler
- PDF ve görüntü dosyaları destekler
- Gönderen, alıcı, tarih, fatura no çıkarır
- %77.8 doğruluk oranı
- Tamamen ücretsiz (lokal LLM)

**Kullanım:**
- Menüde **5** tuşuna basın
- Input dizini belirleyin
- Output dizini belirleyin
- **3** ile dosyaları tarayın
- **4** ile işlemeyi başlatın

**Çıktı formatı:**
```
gönderen_alıcı_YYYYMMDD_HHMM_faturano.pdf
```

### 6. 🏷️ Tag Manager
**Ne yapar:** Belgelere etiket ekler ve yönetir
- Belgelere çoklu etiket ekleme
- Etiket istatistikleri
- Etikete göre belge arama

**Kullanım:**
- Menüde **6** tuşuna basın
- **1** - Belgeye etiket ekle
- **2** - Etiket kaldır
- **3** - Etikete göre belge ara

**Etiketler nerede saklanır:**
`~/Documents/unibos_documents/.tags.json`

### 7. 📊 Analytics
**Ne yapar:** Belge istatistikleri ve analizleri
- Toplam belge sayısı ve boyutu
- Dosya tipi dağılımı
- Son aktiviteler
- Disk kullanımı

**Gösterilen bilgiler:**
- Toplam belge sayısı
- Toplam/ortalama boyut
- Dosya tipi yüzdeleri (grafik ile)
- Son 5 değişiklik
- Disk kullanım oranı

## 🎯 Analiz Kodunu Çalıştırma

### Yöntem 1: Documents Menüsünden
```bash
1. python3 src/main.py çalıştır
2. Documents modülüne gir
3. 7 tuşuna bas veya Analytics seçeneğini seç
4. Analizler otomatik gösterilir
```

### Yöntem 2: Python Script Olarak
```python
# Direkt analiz fonksiyonunu çağırma
from documents_functions import document_analytics
document_analytics()
```

### Yöntem 3: Standalone Script
```python
#!/usr/bin/env python3
import sys
sys.path.append('/Users/berkhatirli/Desktop/unibos/src')

from documents_functions import document_analytics
document_analytics()
```

## 📁 Dosya Yapısı

```
~/Documents/unibos_documents/
├── .tags.json           # Etiket veritabanı
├── *.pdf                # PDF belgeler
├── *.txt                # Metin dosyaları
├── *.jpg, *.png         # Görüntüler
└── invoice_results_*.json  # Fatura işleme sonuçları
```

## ⚙️ Özelleştirme

### Belge Dizinini Değiştirme
`documents_functions.py` dosyasında:
```python
docs_dir = Path.home() / "Documents" / "unibos_documents"
# Değiştir:
docs_dir = Path("/özel/dizin/yolu")
```

### OCR Dil Ayarları
```python
# documents_functions.py içinde
text = pytesseract.image_to_string(img, lang='eng+tur')
# Diğer diller ekle:
text = pytesseract.image_to_string(img, lang='eng+tur+deu')  # Almanca ekle
```

## 🔧 Sorun Giderme

### OCR Çalışmıyor
```bash
# Tesseract kurulu mu kontrol et
which tesseract

# Yoksa kur
brew install tesseract
pip install pytesseract pillow
```

### Belge Dizini Bulunamıyor
```bash
# Dizini manuel oluştur
mkdir -p ~/Documents/unibos_documents
```

### Invoice Processor Hata Veriyor
```bash
# Ollama kurulu mu kontrol et
ollama list

# Model indir
ollama pull llama2
```

## 🎨 Klavye Kısayolları

| Tuş | İşlev |
|-----|-------|
| **1-7** | Direkt menü seçimi |
| **↑↓** | Menüde gezinme |
| **Enter** | Seçimi onayla |
| **ESC/q** | Geri dön |
| **←** | Ana menüye dön |

## 📊 Performans

- **Browse:** Anında (< 0.1s)
- **Search:** Hızlı (< 1s for 1000 files)
- **Upload:** Dosya boyutuna bağlı
- **OCR:** 2-5 saniye/sayfa
- **Invoice:** ~1.7 saniye/fatura
- **Analytics:** Anında (< 0.5s)

## 🚀 İpuçları

1. **Toplu Upload:** Birden fazla dosya için script yazın:
```bash
for file in *.pdf; do
    echo "$file" | python3 -c "
import sys
sys.path.append('src')
from documents_functions import upload_documents
# Implement batch upload
"
done
```

2. **Otomatik Etiketleme:** Upload sonrası otomatik etiket ekleyin

3. **Periyodik Analiz:** Cron job ile günlük analiz çalıştırın:
```bash
0 9 * * * cd /Users/berkhatirli/Desktop/unibos && python3 -c "import sys; sys.path.append('src'); from documents_functions import document_analytics; document_analytics()" > daily_report.txt
```

## 📝 Notlar

- Tüm veriler lokal olarak saklanır
- Hiçbir bulut servisi kullanılmaz
- Invoice processor tamamen ücretsizdir
- OCR offline çalışır

## 🎯 Özet

Documents modülü tam fonksiyonel bir belge yönetim sistemidir:
- ✅ Belge tarama ve listeleme
- ✅ Tam metin arama
- ✅ Dosya yükleme
- ✅ OCR ile metin çıkarma
- ✅ AI destekli fatura işleme
- ✅ Etiket yönetimi
- ✅ Detaylı analizler

Tüm özellikler CLI üzerinden kolayca erişilebilir ve kullanılabilir!