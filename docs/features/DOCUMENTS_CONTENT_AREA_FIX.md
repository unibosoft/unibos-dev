# Documents Module - Content Area Fix ✅

## Summary
Documents menüsü artık web forge gibi sağdaki content alanında açılıyor!

## Yapılan Değişiklikler

### 1. Content Area'da Görüntüleme ✅
- Documents menüsü artık ayrı bir ekran olarak değil, sağdaki content alanında açılıyor
- Sidebar görünür ve dimmed (soluk) kalıyor
- Web forge ile aynı davranış şekli

### 2. Görsel Düzen
```
┌─────────────────────────┬────────────────────────────────────┐
│ modules (dimmed)        │ 📄 documents                       │
│ ─────────               │ intelligent document management    │
│ 🪐 recaria              │                                    │
│ 📡 birlikteyiz          │ [1] browse documents               │
│ 📈 kişisel enflasyon    │     view and manage documents      │
│ 💰 currencies           │                                    │
│ 💸 wimm                 │ [2] search                         │
│ 📦 wims                 │     full-text document search      │
│ 📄 documents (selected) │                                    │
│                         │ [5] invoice processor              │
│                         │     process invoices with ai       │
│                         │                                    │
│                         │ ↑↓ navigate | enter select | esc  │
└─────────────────────────┴────────────────────────────────────┘
```

### 3. Navigation
- **↑↓** - Menü öğeleri arasında gezin
- **Enter** - Seçili öğeyi aç
- **1-7** - Direkt numara ile seçim
- **ESC/q** - Ana menüye dön
- **←** - Ana menüye dön

### 4. Kod Değişiklikleri

#### main.py
- `handle_documents_module()` - Content area'da menü gösterimi
- `draw_documents_menu()` - Menü çizimi
- `launch_invoice_processor()` - Invoice processor başlatma
- Navigation loop web forge gibi çalışıyor

#### Yeni Özellikler
- Sidebar dimmed kalıyor (soluk görünüyor)
- Content area'da tam kontrol
- Smooth navigation
- Temp mesajlar için alan

## Kullanım

### Documents Modülüne Erişim:
```bash
python3 src/main.py
```
1. Arrow keys ile "documents" modülüne gidin
2. Enter veya sağ ok ile açın
3. Content area'da documents menüsü görünecek

### Invoice Processor:
1. Documents menüsünde '5' tuşuna basın
2. Veya arrow keys ile "invoice processor" seçin ve Enter
3. Invoice processor tam ekran açılacak
4. İşlem bitince documents menüsüne dönecek

## Test Sonuçları
- ✅ Content area'da görüntüleme
- ✅ Sidebar dimmed ve görünür
- ✅ Navigation çalışıyor
- ✅ Invoice processor entegrasyonu
- ✅ ESC/q ile çıkış
- ✅ Web forge ile aynı davranış

## Önemli Notlar
- Documents menüsü artık tam olarak web forge gibi davranıyor
- Sidebar her zaman görünür kalıyor (dimmed)
- Content area'da tüm kontrol
- Invoice processor tam ekran açılıp kapanıyor

## Sonuç
Documents modülü başarıyla content area'ya taşındı ve web forge ile aynı şekilde çalışıyor!