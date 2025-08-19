# CLAUDE_VERSION.md - Güncel Durum ve Değişiklikler

> **📊 NOT**: Bu dosya güncel versiyon bilgilerini içerir. Ana yönetim için [CLAUDE.md](./CLAUDE.md) dosyasına bakın.

## Güncel Durum

- **Versiyon**: v180
- **Tarih**: 2025-07-17 22:39:00 +03:00
- **Son Değişiklikler (v180)**:
  - 🔧 **Tab Switch Fixed**: Section değişiminde tüm sidebar yeniden çiziliyor
  - ✨ **Complete Redraw**: draw_sidebar() ile eski highlight kesin temizleniyor
  - 🎯 **No More Ghost Highlights**: Diğer bölümdeki highlight artık kalmıyor

## Son 20 Versiyon Değişiklikleri

### v180 - 2025-07-17 22:39:00 +03:00
- 🔧 **Tab Switch Fixed**: Section değişiminde tüm sidebar yeniden çiziliyor
- ✨ **Complete Redraw**: draw_sidebar() ile eski highlight kesin temizleniyor
- 🎯 **No More Ghost Highlights**: Diğer bölümdeki highlight artık kalmıyor
- 📋 **Simple Solution**: Tab handler'da direkt sidebar redraw
- 👻 **Ghost Highlight Bug**: "Diğer bölümdeki son öğe yanar şekilde kalıyor" sorunu çözüldü

### v179 - 2025-07-17 22:31:00 +03:00 🏆 MILESTONE
- 🏆 **MILESTONE VERSION**: Kullanıcı onaylı stabil navigasyon
- ✨ **Section Switch Fix**: Tab ile geçişte eski highlight temizleniyor
- 🎯 **Perfect Navigation**: Hiç olmadığı kadar iyi çalışıyor (kullanıcı onayı)
- 📋 **Recovery Point**: İleride sorun yaşanırsa bu versiyondan kurtarma
- 👍 **User Approved**: "Hiç olmadığı kadar iyi çalışıyor" - Berk Hatırlı

### v178 - 2025-07-17 22:19:00 +03:00 ✅ STABLE
- 🎯 **Sidebar Navigation Fixed**: Admin tools pozisyonu sabitlendi
- ✅ **UI Stability**: Footer tekrarlama sorunu çözüldü
- 📋 **Draw Functions**: Sidebar ve footer çizim fonksiyonları iyileştirildi
- 🔧 **Menu State**: tools_start_y pozisyonu state'de saklanıyor
- 🧹 **Screen Clear**: Terminal tam temizleme eklendi

### v177 - 2025-07-17 16:14:00 +03:00
- 🕒 **Istanbul Timezone Enforcement**: Build saati artık doğru sistem saatinden alınıyor
- ✅ **System Time Check**: `date` komutu zorunlu kontrol haline getirildi
- 📋 **CLAUDE_RULES.md Updated**: Saat kontrolü mutlak kural olarak detaylandırıldı
- 🔍 **get_current_istanbul_time()**: Zorunlu saat kontrol fonksiyonu eklendi
- ❌ **Build Time Fix**: 18:08 yerine doğru saat 16:14 kullanıldı

### v176 - 2025-07-17 18:08:00 +03:00 (HATALI SAAT)
- 🔍 **Kronik Sorun Tespiti**: Claude her oturumda otomatik kronik sorun taraması yapacak
- 🕒 **Istanbul Saat Dilimi Zorunlu**: Tüm tarih/saat damgaları UTC+3 kullanacak
- 📋 **Communication Log Yönetimi**: Maksimum 3 log tutulacak, otomatik temizlik
- 🎯 **Menu Navigation Fix**: Arrow key ve state senkronizasyon sorunu kesin çözüldü
- 🔧 **State Management**: selected_module/tool ile menu_state.selected_index senkronize
- ⚡ **Performance**: get_single_key() timeout 0.001'e düşürüldü

### v175 - 2025-07-17 16:25:00 +03:00
- 🔧 **Menu State Sync**: current_section yerel değişkeni kaldırıldı
- ✅ **Unified Navigation**: Tüm navigasyon menu_state.current_section ile
- 🎯 **Tab Switch Fix**: Tab tuşu section değişimi düzeltildi

### v174 - 2025-07-17 14:15:00 +03:00
- 🎯 **Sidebar Fix**: Tools section position dinamik hesaplama
- 🔧 **Arrow Key Order**: ESC kontrolü arrow key'lerden sonra
- ✅ **Dynamic Layout**: Modül sayısına göre tools pozisyonu

### v173 - 2025-07-17 14:10:00 +03:00
- 🐛 **Threading Import Fixed**: claude_cli.py'de threading import hatası düzeltildi
- 🔧 **Module Import Order**: threading modülü doğru sırada import ediliyor
- ✅ **Claude CLI Works**: Claude tools tekrar çalışıyor

### v172 - 2025-07-17 13:56:10 +03:00
- 🎯 **Arrow Key Fix**: Escape sequence timeout 50ms'ye çıkarıldı
- 🔧 **Better Detection**: select.select() timeout optimizasyonu
- ✅ **Navigation Works**: Ok tuşları artık düzgün çalışıyor

### v171 - 2025-07-17 13:39:40 +03:00
- 🚀 **Startup Navigation Fixed**: İlk 3-4 tuş basma sorunu çözüldü
- 🔧 **Multiple Buffer Flush**: Terminal buffer 3 kez temizleniyor
- ⏱️ **Startup Delay Increased**: Splash sonrası 200ms bekleme
- 🎯 **Dummy Key Reads**: İlk 3 tuş okuma atlanıyor
- 📊 **Better Escape Sequence**: select.select() ile daha iyi algılama
- 🧹 **Screen Jump Fixed**: Section switch sırasında ekran kayma düzeltildi
- ✅ **Smooth Navigation**: Tüm navigasyon sorunları giderildi
- 🔄 **No More Redraws**: update_sidebar_selection kullanımı optimize edildi

### v170 - 2025-07-17 06:35:00 +03:00
- 📦 **fcntl Import Added**: Non-blocking I/O operations için fcntl modülü eklendi
- 🔧 **Non-blocking Read**: Escape sequence'ları için non-blocking okuma implementasyonu
- ⏱️ **Debounce Mechanism**: Tuş basımları arasında 50ms minimum bekleme süresi
- 🎯 **Arrow Key Detection Fixed**: Arrow key algılama timing sorunları çözüldü
- 🧹 **Input Buffer Flushing**: Hızlı tuş basımlarında buffer temizleme eklendi
- 🔄 **Partial Escape Handling**: Kısmi escape sequence'lar için daha iyi handling

### v169 - 2025-07-17 05:44:00 +03:00
- 🔧 **load_suggestions_from_file Fixed**: Tüm 10 öneriyi yükleyen fonksiyon düzeltildi (önceden 1-5 ile sınırlıydı)
- ➕ **Added 5 More Suggestions**: CLAUDE_SUGGESTIONS.md'ye 5 yeni öneri eklendi (toplam 10)
- 📋 **All 10 Suggestions Displayed**: Claude tools menüsünde artık 10 öneri gösteriliyor
- 🔢 **Fixed Suggestion Parsing**: 6-10 numaralı önerileri desteklemek için parse düzeltildi
- ✅ **Complete 10-Item System**: Öneri sistemi tam 10 madde ile çalışıyor

### v168 - 2025-07-17 06:58:00 +03:00
- 🔢 **10 Suggestions System**: Öneri sayısı 5'ten 10'a çıkarıldı
- 🔧 **save_suggestions_to_file Fixed**: Öneri güncellemelerini düzgün işleme
- ✅ **Claude Response Validation**: Claude yanıt formatı için validasyon eklendi
- 📋 **Exact Format Requirements**: Claude için tam format gereksinimleri
- 💾 **CLAUDE_SUGGESTIONS.md Protection**: Dosyanın üzerine yazılması engellendi
- 🛡️ **Better Error Handling**: Geçersiz öneri formatları için hata yönetimi

### v167 - 2025-07-17 05:29:00 +03:00
- 🕐 **Istanbul/Europe Timezone Fixed**: Tüm zaman damgaları UTC+3 uyumlu
- 📝 **Communication Log Management**: Sadece son 3 log dosyası tutulacak
- 🔧 **CLAUDE_SUGGESTIONS.md Repaired**: Bozulan öneri dosyası düzeltildi
- 📋 **Suggestions Loading Fixed**: Claude tools önerileri yeniden görünüyor
- ✅ **Timezone Compliance**: İstanbul saat dilimi kuralına tam uyum

### v166 - 2025-07-17 18:12:00 +03:00
- 🔧 **Terminal Line Clearing Fixed**: Update suggestions display'de line clearing sorunları çözüldü
- ⏱️ **Claude Timeout Increased**: 120 saniyeden 300 saniyeye çıkarıldı
- 🧹 **Subprocess Output Clearing**: └─ satırları için line clearing eklendi
- 📸 **Archive SS Rule Added**: CLAUDE_RULES.md'ye arşiv SS kontrol kuralı eklendi
- 🎯 **Better Progress Display**: Cursor positioning iyileştirildi

### v165 - 2025-07-17 17:45:00 +03:00
- 📊 **Suggestion Count Increased**: Claude tools öneri sayısı 5'ten 10'a çıkarıldı
- 🔄 **Auto Refresh After Update**: Güncelleme sonrası otomatik öneri yenileme
- 💾 **Persistent Suggestions**: save_suggestions_to_file() fonksiyonu eklendi
- 📝 **Dynamic Update Rule**: CLAUDE_RULES.md'ye dinamik güncelleme kuralı

### v164 - 2025-07-17 05:20:00 +03:00
- 🔧 **Threading Import Fixed**: claude_cli.py'deki threading import hatası düzeltildi
- ✅ **Update Suggestions Working**: Öneri güncelleme özelliği düzgün çalışıyor
- 🐛 **Import Error Resolved**: Threading modülü artık sorunsuz yükleniyor

### v163 - 2025-07-17 05:10:00 +03:00
- 📊 **Step-by-Step Process Visualization**: Progress bar kaldırıldı
- ✅ **Real-time Task Status Display**: Her task için ayrı durum göstergesi
- 🎯 **Clear Progress Tracking**: Hangi adımda olduğumuz net görülüyor

### v162 - 2025-07-17 04:41:00 +03:00
- ⏳ **Progress Visualization**: Claude suggestions için spinner ve progress bar
- 📊 **Detaylı UI**: Update suggestions sırasında görsel feedback

### v161 - 2025-07-17 04:35:00 +03:00
- 🔧 **Claude Timeout Fix**: Suggestions timeout 300 saniyeye çıkarıldı
- ⏱️ **Better Error Handling**: Timeout durumunda açıklayıcı mesajlar

### v160 - 2025-07-17 04:28:00 +03:00
- 🤖 **Claude Tools Full Feature**: Tüm modlar aktif ve çalışıyor
- ✅ **Navigation Fixed**: Arrow key'ler düzgün çalışıyor

### v159 - 2025-07-17 04:20:00 +03:00
- 🎮 **v130 Style Arrow Keys**: Kanıtlanmış çözüm geri getirildi
- ⏱️ **50ms Timeout**: Optimal arrow key detection

### v158 - 2025-07-17 04:11:00 +03:00
- 🔧 **get_single_key Baştan Yazıldı**: Loop-based sequence reading
- 🎯 **Kesin Çözüm**: Arrow key'ler artık düzgün çalışıyor

### v157 - 2025-07-17 04:06:00 +03:00
- 🎯 **Arrow Key Fix**: Escape sequence detection timeout 0 yapıldı
- ⚡ **Immediate Detection**: select.select() timeout ayarları

### v156 - 2025-07-17 04:02:00 +03:00
- 🔍 **Debug Logging**: Main loop'a arrow key debug çıktısı eklendi
- 🎯 **Key Detection Trace**: /tmp/unibos_main_debug.log dosyasına key logları

### v155 - 2025-07-17 01:00:00 +03:00
- 🎮 **Arrow Key Navigation Fixed**: Timeout değerleri 0.1s'ye çıkarıldı
- 🔧 **Previous Index Management**: menu_state.previous_index düzeltildi

### v154 - 2025-07-17 00:45:00 +03:00
- ⚡ **Performance Boost**: Minimal redraw stratejisi uygulandı
- 🛡️ **Stability Fix**: ESC ile program kapanması engellendi

### v153 - 2025-07-17 00:35:00 +03:00
- 🎮 **Arrow Key Fix**: Menü navigasyonu artık arrow key'lerle çalışıyor
- 🔄 **State Management**: menu_state senkronizasyonu düzeltildi

### v152 - 2025-07-17 00:25:00 +03:00
- 🔧 **FORCED Naming Rules**: SS ve arşiv isimlendirme kuralları güncellendi
- ✅ **232 Dosya Düzenlendi**: Tüm arşiv yapısı standartlaştırıldı

### v151 - 2025-07-17 00:00:00 +03:00
- 🌍 **Full Location Display**: Splash ekranında bitez'den evren'e
- 🎮 **Arrow Key Fix**: Debug file close hatası düzeltildi

---
*Bu dosya maksimum son 20 versiyon değişikliğini içerir. Daha eski versiyonlar için arşiv klasörüne bakın.*