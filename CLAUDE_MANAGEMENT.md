# CLAUDE.md Dosya Yönetim Sistemi

> **⚠️ KRİTİK**: Bu dosya CLAUDE.md dosyalarının yönetim kurallarını içerir ve performans optimizasyonu için oluşturulmuştur.

## 📋 Dosya Yönetim Kuralları

### 1. Dosya Boyutu Limitleri
- **Maksimum Boyut**: Her CLAUDE_*.md dosyası maksimum 30.000 karakter içermelidir
- **Uyarı Seviyesi**: 25.000 karakterde yeni dosyaya geçiş planlanmalı
- **Kritik Seviye**: 30.000 karakterde ZORUNLU yeni dosya oluşturulmalı

### 2. Dosya İsimlendirme Formatı
```
CLAUDE.md          # Ana orkestrasyon merkezi
CLAUDE_CORE.md     # Temel kurallar ve kritik bilgiler
CLAUDE_RULES.md    # Detaylı kurallar ve prosedürler
CLAUDE_TECH.md     # Teknik özellikler ve stack bilgileri
CLAUDE_MODULES.md  # Modül bilgileri ve açıklamaları
CLAUDE_ARCHIVE.md  # Arşiv kuralları ve yönetimi
CLAUDE_VERSION.md  # Versiyon geçmişi ve değişiklikler
CLAUDE_MANAGEMENT.md # Dosya yönetim sistemi (bu dosya)
```

### 3. Güncel Dosya Boyutları

```bash
# Son kontrol: 2025-07-16 18:20:00 +03:00
CLAUDE.md:            4.5KB  ✅ Normal
CLAUDE_CORE.md:       6.4KB  ✅ Normal  
CLAUDE_RULES.md:      8.0KB  ✅ Normal
CLAUDE_MANAGEMENT.md: 3.8KB  ✅ Normal (bu dosya)
CLAUDE_TECH.md:       4.9KB  ✅ Normal
CLAUDE_MODULES.md:    3.2KB  ✅ Normal
CLAUDE_ARCHIVE.md:    6.4KB  ✅ Normal
CLAUDE_VERSION.md:    7.4KB  ✅ Normal
```

### 4. Otomatik Kontrol Scriptleri

```bash
# Dosya boyutlarını kontrol et
for file in CLAUDE*.md; do
    size=$(wc -c < "$file")
    echo "$file: $size karakter"
done

# 25k üzeri dosyaları uyar
for file in CLAUDE*.md; do
    size=$(wc -c < "$file")
    if [ $size -gt 25000 ]; then
        echo "⚠️ UYARI: $file boyutu kritik seviyeye yaklaşıyor ($size karakter)"
    fi
done
```

### 5. Güncelleme Prosedürü

1. **Yeni Bilgi Eklerken**:
   - İlgili CLAUDE_*.md dosyasını bul
   - Dosya boyutunu kontrol et
   - 25k üzeriyse yeni dosya planla
   - İçeriği uygun dosyaya ekle

2. **Dosya Bölme Prosedürü**:
   - Dosya 30k'ya ulaştığında
   - İçeriği mantıksal bölümlere ayır
   - Yeni dosya oluştur (CLAUDE_*_2.md formatında)
   - Referansları güncelle

3. **Çapraz Referans Kuralları**:
   - Her dosyada diğer dosyalara referans vermek için:
   - `Detaylar için bkz: [CLAUDE_TECH.md](./CLAUDE_TECH.md)`
   - Broken link kontrolü zorunlu

### 6. Performans İzleme

- Claude her oturum başında dosya boyutlarını kontrol etmeli
- 25k üzeri dosyalar için uyarı vermeli
- Gerekirse içerik reorganizasyonu önermeli

### 7. Versiyon Kontrolü

- Her dosya değişikliğinde bu dosyadaki boyut tablosu güncellenmeli
- Kritik değişikliklerde tüm ilgili dosyalar senkronize edilmeli

---
*Bu dosya CLAUDE dosya sisteminin yönetim merkezidir.*
*Son güncelleme: 2025-07-16 18:20:00 +03:00*