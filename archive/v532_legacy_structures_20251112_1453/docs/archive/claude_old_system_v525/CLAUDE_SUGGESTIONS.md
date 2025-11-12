# CLAUDE_SUGGESTIONS.md - Geliştirme Önerileri Sistemi

> **🎯 NOT**: Bu dosya Claude'un geliştirme önerilerini ve takip sistemini içerir.

## 📊 Güncel Öneri Listesi (v120)

### Aktif Öneriler (Öncelik Sırasıyla)

1. **[🔴 Kritik] Blink modülü konum gizlilik ayarları güncellenmeli**
   - Sorun: Konum paylaşım gizlilik seviyeleri tam çalışmıyor
   - Çözüm: API endpoint'lerinde permission kontrolü ekle
   - Dosya: `projects/blink/location_manager.py`

2. **[🟠 Yüksek] Currencies modülünde API hata yönetimi iyileştirilmeli**
   - Sorun: API timeout durumlarında crash oluyor
   - Çözüm: Try-except blokları ve fallback mekanizması
   - Dosya: `projects/currencies/api.py`

3. **[🟡 Orta] Recaria harita cache sistemi optimize edilmeli**
   - Sorun: Cache boyutu kontrolsüz büyüyor
   - Çözüm: LRU cache ve boyut limiti ekle
   - Dosya: `projects/recaria/cache/recaria_cache.py`

4. **[🟢 Düşük] Terminal arayüzünde renk kontrastları artırılmalı**
   - Sorun: Bazı renk kombinasyonları okunmuyor
   - Çözüm: WCAG standartlarına uygun renk paleti
   - Dosya: `src/main.py`

5. **[🟢 Düşük] v042'den kayıp parallel system özellikleri geri getirilmeli**
   - Kayıp: Parallel task execution sistemi
   - Kaynak: `archive/versions/unibosoft_v043_*/core/parallel_system.py`
   - Hedef: `src/core/parallel/`

6. **[🟡 Orta] Birlikteyiz modülüne mesh network visualizer eklenmeli**
   - Sorun: Network topology görselleştirme eksik
   - Çözüm: ASCII art veya terminal grafik kütüphanesi ile visualizer
   - Dosya: `projects/birlikteyiz/visualizer.py`

7. **[🟢 Düşük] Currencies modülüne kripto wallet entegrasyonu**
   - Sorun: Sadece fiyat takibi var, wallet yönetimi yok
   - Çözüm: Read-only wallet address monitoring
   - Dosya: `projects/currencies/wallet.py`

8. **[🟡 Orta] Main UI'da klavye kısayolları sistemi**
   - Sorun: Her işlem için menüde gezinmek gerekiyor
   - Çözüm: Vim-style kısayollar (j/k navigasyon, / arama vb.)
   - Dosya: `src/main.py`

9. **[🟢 Düşük] Dark/Light tema geçişi**
   - Sorun: Sadece dark tema var
   - Çözüm: Terminal renk şemaları ve tema yönetimi
   - Dosya: `src/themes.py`

10. **[🟡 Orta] Screenshot manager'a OCR desteği**
    - Sorun: Screenshot içerikleri manuel okunuyor
    - Çözüm: Tesseract entegrasyonu ile otomatik metin çıkarma
    - Dosya: `src/screenshot_manager.py`

11. **[🟠 Yüksek] Git repo yönetimi ve görselleştirme özelliği eklenmeli**
   - Sorun: Aktif repo bilgisi, repo ekleme/değiştirme işlemleri için arayüz eksik
   - Çözüm: Git repo yönetici modülü ekle, aktif repo gösterimi, repo ekleme/değiştirme komutları
   - Dosya: `src/git_manager.py`

## 💡 Manuel Öneriler (Kullanıcı Ekledi)

### Kolay Uygulanabilir (1-2 saat)
*Bu bölüm kullanıcı tarafından eklenen ve hızlıca uygulanabilecek önerileri içerir*

### Orta Zorluk (3-5 saat)
*Biraz daha fazla çaba gerektiren manuel öneriler*

### Zor/Uzun Vadeli (5+ saat)
*Kapsamlı değişiklik gerektiren manuel öneriler*

## 📈 Öneri Havuzu (Bekleyen)

### Güvenlik
- JWT token refresh mekanizması eksik
- SQL injection koruması güçlendirilmeli
- XSS koruması tüm modüllere yayılmalı

### Performans
- Database query optimizasyonu (N+1 problem)
- Static dosya CDN entegrasyonu
- WebSocket bağlantı havuzu

### Kullanıcı Deneyimi
- Klavye kısayolları sistemi
- Dark/Light tema geçişi
- Çoklu dil desteği genişletilmeli

### Yeni Özellikler
- Birlikteyiz modülüne mesh network visualizer
- Recaria'ya multiplayer desteği
- Currencies'e kripto wallet entegrasyonu
- git bölümü için bir madde oluştur. önemli olarak etiketle. aktif repo, repo ekleme/değiştirme vs gibi özellikler öne (manuel ekleme)

## 📊 İstatistikler

### Öneri Uygulama Geçmişi
- v122: 1 öneri uygulandı (Claude öneri algoritması performans optimizasyonu)
- v120: 1 öneri uygulandı (Screenshot yönetimi)
- v119: 2 öneri uygulandı (Claude otomatik kontrol, Türkçe karşılama)
- v118: 3 öneri uygulandı
- Toplam: 128 öneri uygulandı

### Kaynak Dağılımı
- %68 TODO ve bilinen sorunlardan
- %22 Eski versiyon taramalarından
- %10 Proaktif yenilik önerilerinden

## 🔄 Güncelleme Protokolü

1. Her Claude oturumu başında bu dosya okunur
2. İlk 5 öneri gösterilir
3. Uygulanan öneriler işaretlenir
4. Çıkışta liste güncellenir
5. Yeni öneriler eski versiyon taramasından eklenir

## 🗓️ Tarama Zamanlaması

- **Son v001-v020 taraması**: 3 oturum önce
- **Son v021-v050 taraması**: 1 oturum önce
- **Son v051-güncel taraması**: Bu oturum

**Sonraki taramalar**:
- v001-v020: 2 oturum sonra
- v021-v050: 2 oturum sonra
- v051-güncel: Her oturum

---
*Son güncelleme: 2025-07-18 20:23:50 +03:00*