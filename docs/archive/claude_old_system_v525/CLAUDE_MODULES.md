# CLAUDE_MODULES.md - Modül Açıklamaları ve Geliştirme

> **📦 NOT**: Bu dosya UNIBOS modüllerinin detaylı açıklamalarını içerir. Ana yönetim için [CLAUDE.md](./CLAUDE.md) dosyasına bakın.

## Ana Modüller

### 1. Recaria 🪐
- Evren keşif oyunu
- 8 noktalı navigasyon sistemi
- Django backend + Phaser.js oyun motoru
- Leaflet harita entegrasyonu
- Offline çalışma desteği

### 2. Kişisel Enflasyon 📈
- Bireysel enflasyon hesaplayıcı
- Ürün takibi ve fiyat analizi
- KVKK uyumlu veri yönetimi

### 3. Currencies 💱
- Gerçek zamanlı döviz takibi
- Kripto para desteği
- API entegrasyonu (TCMB + CoinGecko)
- Portföy yönetimi
- Grafik ve analiz araçları

### 4. Birlikteyiz 📡
- LoRa tabanlı mesh ağ sistemi
- Afet durumları için acil iletişim
- 15km menzil
- Deprem verileri harita entegrasyonu

## Teknik Özellikler

### Veritabanı Yapısı
- SQLite tabanlı merkezi veritabanı
- PostgreSQL desteği (büyük ölçekli kurulumlar için)
- Ortak veri modeli - tüm modüller paylaşımlı veritabanı kullanır
- Otomatik temizlik ve optimizasyon

### Güvenlik
- Veri hassasiyet sınıflandırması (P0-P3)
- Yerel öncelikli işleme
- SSL/TLS desteği
- Rol tabanlı erişim kontrolü

### Performans
- Python 3.8+ (3.11+ önerilir)
- Asenkron işleme desteği
- Önbellekleme mekanizmaları
- Otomatik kaynak yönetimi

## Modül Ekleme Kuralları

1. `projects/` altında yeni klasör oluştur
2. `__init__.py` ve `main.py` dosyaları ekle
3. Ana menüye entegre et
4. CLAUDE_MODULES.md'yi güncelle (bu dosya)

## Modül Geliştirme Standartları

### Zorunlu Dosyalar
- `__init__.py`: Modül tanımlamaları
- `main.py`: Ana giriş noktası
- `README.md`: Modül dokümantasyonu
- `requirements.txt`: Bağımlılıklar

### Kod Standartları
- PEP 8 uyumlu
- Type hints kullanımı
- Docstring zorunlu
- Test coverage: Minimum %80

### Hata Yönetimi
- Structured logging (JSON format)
- Error tracking ready (Sentry entegrasyonu)
- Graceful degradation
- User-friendly error messages
- Debug mode (development only)

## Test Gereksinimleri

### Test Komutları
```bash
# Linting
python -m flake8 . --exclude=venv,__pycache__,archive

# Type checking
python -m mypy . --ignore-missing-imports

# Unit tests
python -m pytest tests/
```

### Test Coverage
- Minimum %80 coverage zorunlu
- CI/CD pipeline'da otomatik kontrol
- Coverage raporu her PR'da zorunlu

## Dokümantasyon Standartları

### Docstring Formatı
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Kısa açıklama (tek satır).
    
    Detaylı açıklama (birden fazla satır olabilir).
    
    Args:
        param1: Parametre açıklaması
        param2: Diğer parametre açıklaması
        
    Returns:
        Dönüş değeri açıklaması
        
    Raises:
        Exception: Hangi durumda hangi hata fırlatılır
    """
```

### README Formatı
Her modül README.md dosyası şunları içermeli:
1. Modül açıklaması
2. Kurulum talimatları
3. Kullanım örnekleri
4. API dokümantasyonu
5. Konfigürasyon seçenekleri
6. Bilinen sorunlar ve çözümleri

---
*Arşiv yönetimi için [CLAUDE_ARCHIVE.md](./CLAUDE_ARCHIVE.md) dosyasına bakın.*
*Son güncelleme: 2025-07-16 17:49:00 +03:00*