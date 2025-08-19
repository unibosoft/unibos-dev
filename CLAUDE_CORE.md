# CLAUDE_CORE.md - UNIBOS Temel Kurallar ve Bilgiler

> **⚠️ KRİTİK UYARI**: Bu dosya UNIBOS projesinin temel kurallarını içerir. Ana yönetim dosyası için [CLAUDE.md](./CLAUDE.md) dosyasına bakın.

## 🕐 ZAMAN DİLİMİ KURALI - KRİTİK
**TÜM ZAMAN DAMGALARI İÇİN İSTANBUL/AVRUPA (UTC+3) KULLANILMALIDIR**
- Timezone: Europe/Istanbul (UTC+3)
- Format: YYYY-MM-DD HH:MM:SS +03:00
- Asla UTC veya başka timezone kullanma
- Tüm log, versiyon, arşiv işlemlerinde bu saat dilimi geçerli

## Proje Sahibi
- **İsim**: Berk Hatırlı  
- **Konum**: Bitez, Bodrum, Muğla, Türkiye, Dünya, Güneş Sistemi, Samanyolu, Yerel Galaksi Grubu, Evren
- **Doğum**: 1986
- **Uzmanlık**: Yazılım Geliştirme, Tasarım, Üretim (CNC, Laser, 3D Print, Raspberry Pi)
- **Şirketler**: 
  - Berk Hatırlı (Şahıs şirketi - Üretim ve E-ticaret)
  - Unicorn Bodrum Teknoloji ve Perakende Ltd. Şti.
  - Unibosoft GmbH (Almanya/Berlin - Planlanan)

## Proje Genel Bakış

UNIBOS (Unicorn Bodrum Operating System), Unibosoft firmasının geliştirdiği çok amaçlı bir işletim sistemi platformudur. Ana yazılım tüm diğer uygulamaların çekirdeğini oluşturur ve şu ortamlarda çalışır:

- **CLI (Komut Satırı Arayüzü)**: Linux, macOS, Windows
- **Web Arayüzü**: Django tabanlı
- **Mobil Uygulama**: Electron ile iOS/Android desteği (planlanıyor)
- **Donanım**: Raspberry Pi Zero 2W üzerinde mesh ağ desteği

## Güncel Dizin Yapısı (v117)

**ANA DİZİN**: `/Users/berkhatirli/Desktop/unibos`
**ASLA BU DİZİNDEN ÇIKMA**: Desktop'a veya üst dizinlere geçme

```
unibos/
├── CLAUDE.md              # Ana orkestrasyon merkezi
├── CLAUDE_*.md            # 7 adet CLAUDE dosyası
├── CHANGELOG.md           # Detaylı versiyon geçmişi
├── README.md              # Kullanıcılar için genel bilgi
├── unibos.sh              # Ana başlatıcı
├── LLM_COMPREHENSIVE_GUIDE.md # LLM'ler için kapsamlı rehber
├── src/                   # Ana kaynak kodları ve TEK VERSION.json
│   ├── VERSION.json      # TEK VERSİYON DOSYASI (ana dizinde YOK)
│   ├── main.py           # Ana program
│   ├── launch.sh         # Detaylı başlatıcı
│   ├── requirements.txt  # Bağımlılıklar
│   ├── translations.py   # Çoklu dil desteği
│   ├── currencies_enhanced.py # Gelişmiş döviz modülü
│   ├── version_manager.sh # Versiyon yönetim aracı
│   ├── git_manager.py    # Git işlemleri yöneticisi
│   └── venv/             # Virtual environment
├── projects/              # Proje modülleri
│   ├── recaria/          # Evren keşif oyunu
│   ├── birlikteyiz/      # Mesh network sistemi
│   ├── currencies/       # Döviz takip modülü
│   └── kisiselenflasyon/ # Enflasyon hesaplayıcı
├── tests/                 # Test dosyaları
└── archive/               # Arşiv (düzenli yapı)
    ├── README.md          # Arşiv kullanım rehberi
    ├── versions/          # Açık klasör versiyonları
    ├── media/             # Medya dosyaları
    │   ├── screenshots/   # Ekran görüntüleri
    │   └── diagrams/      # Teknik diyagramlar
    ├── reports/           # Raporlar
    └── references/        # Dış referanslar
```

**ÖNEMLİ NOT**: VERSION.json artık SADECE src/ dizininde bulunur. Ana dizinde VERSION.json YOKTUR.

## Claude AI İçin Kritik Kurallar (İlk 15)

### 1. Bu Dosya Sistemi
- CLAUDE.md ana orkestrasyon merkezidir
- CLAUDE_*.md dosyaları 30k karakter limitine sahiptir
- Yeni özellik eklendiğinde ilgili dosya güncellenmeli

### 2. Ana Dizinde Kalma
- Asla `/Users/berkhatirli/Desktop/unibos` dışına çıkılmamalı
- Desktop'a veya üst dizinlere geçiş YASAK

### 3. Versiyon Bilgisi
- Her büyük değişiklikte versiyon güncellenmeli
- src/VERSION.json TEK versiyon kaynağı

### 4. Dizin Yapısı
- Değişikliklerde yapı güncellenmeli
- archive/ dizini git'e eklenmemeli

### 5. Test Edilebilirlik
- Tüm komutlar test edilmiş olmalı
- Linting ve type checking zorunlu

### 6. Screenshot Önceliği - EN KRİTİK KURAL
- Her yeni mesajda İLK İŞ: `ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'` kontrolü
- SS varsa: Oku → Analiz et → Kullanıcı mesajıyla değerlendir → Arşivle → Todo ekle
- Bu sıralama HİÇBİR ZAMAN atlanmamalı
- Screenshot analizi TÜM diğer işlemlerden önce gelir

### 7. Versiyon Senkronizasyonu
- src/VERSION.json ve src/main.py HEP AYNI versiyonda olmalı
- version_manager.sh sadece src/VERSION.json'u günceller

### 8. Tarih/Saat Formatı
- **Saat Dilimi**: Europe/Istanbul (UTC+3)
- **Format**: "YYYY-MM-DD HH:MM:SS +03:00"
- **Lokasyon**: Bitez, Bodrum, Muğla, Türkiye, Dünya, Güneş Sistemi, Samanyolu, Yerel Galaksi Grubu, Evren

### 9. CHANGELOG Zorunluluğu
- Her versiyon değişikliğinde CHANGELOG.md MUTLAKA güncellenmelidir

### 10. README.md Güncelleme Zorunluluğu
- Her versiyon değişikliğinde README.md'deki version badge'i güncellenmelidir

### 11. Küçük Harf UI Standardı
- TÜM kullanıcı arayüzü metinleri KESİNLİKLE küçük harfle yazılır
- Splash screen, header, menüler, hata mesajları DAHİL
- "unibos", "error:", "loading..." ✅ | "UNIBOS", "Error:", "Loading..." ❌

### 12. Git İgnore Kuralları
- archive/: Tüm arşiv dizini git'e eklenmemeli
- CLAUDE*.md: Tüm CLAUDE dosyaları repository'de gözükmemeli
- LLM_COMPREHENSIVE_GUIDE.md: LLM rehber dokümanı git'e eklenmemeli

### 13. Screenshot Yönetimi - KRİTİK KURAL
- Ana dizinde ASLA screenshot kalmamalı
- İsimlendirme: `vXXX_build_YYYYMMDD_HHMM_N.png`
- Arşivleme: `archive/media/screenshots/v061-current/` dizinine TAŞI

### 14. Arşiv Yedekleme Kuralları - ZORUNLU
- Açık arşiv: `archive/versions/unibos_vXXX_YYYYMMDD_HHMM/`
- Versions: `archive/versions/unibos_vXXX_YYYYMMDD_HHMM/`
- archive/ dizini ASLA kopyalanmamalı

### 15. Communication Log Zorunluluğu - MUTLAK KURAL ⚠️
- HER VERSİYON GÜNCELLEMESİNDE communication log ZORUNLU
- Maksimum 3 log tutulur, fazlası silinir
- Format: `CLAUDE_COMMUNICATION_LOG_vXXX_to_vYYY_YYYYMMDD_HHMM.md`
- Versiyon güncellemeden ÖNCE log yazılmalı
- Log yazmayı unutursan kullanıcı uyarır!

### 16. Temizlik Kuralları
- Eski scriptler archive/migration_scripts/ altına taşınmalı
- Ana dizinde screenshot varsa işlem TAMAMLANMAMIŞ demektir

## Felsefe ve İlkeler

"🌍 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria! 🚀✨"

- Açık kaynak öncelikli
- Kullanıcı gizliliğine saygı
- Offline-first tasarım
- Minimalist ve verimli kod
- Türkçe öncelikli, çoklu dil desteği
- Küçük harf kullanımı tercihi

---
*Detaylı kurallar için [CLAUDE_RULES.md](./CLAUDE_RULES.md) dosyasına bakın.*
*Son güncelleme: 2025-07-16 18:21:00 +03:00*