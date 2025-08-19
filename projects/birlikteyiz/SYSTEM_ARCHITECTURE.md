# Birlikteyiz - Açık Kaynak Acil Durum İletişim Sistemi

**Proje Adı:** Birlikteyiz Emergency Communication Platform  
**Versiyon:** v1.0.0-alpha  
**Geliştirici:** Unicorn Bodrum Technologies  
**Lisans:** MIT Open Source License  
**Tarih:** 24 Haziran 2025  

## Proje Özeti

Birlikteyiz, afet ve acil durumlarda kritik iletişim altyapısını sağlamak üzere tasarlanmış açık kaynak kodlu, tamamen yerel çalışan bir acil durum iletişim platformudur. Sistem, Raspberry Pi tabanlı donanım üzerinde çalışarak LoRa uzun mesafe iletişimi ve 2.4GHz düşük hızlı veri aktarımı ile geniş coğrafi alanları kapsayan dayanıklı bir iletişim ağı oluşturur.

Platform, geleneksel iletişim altyapısının çöktüğü durumlarda bile çalışmaya devam edebilecek şekilde tasarlanmış olup, mesh ağ topolojisi kullanarak otomatik yönlendirme ve yedeklilik sağlar. Her cihaz hem istemci hem de röle görevi görerek ağın dayanıklılığını artırır ve tek nokta arızalarına karşı koruma sağlar.

## Sistem Mimarisi

### Genel Sistem Tasarımı

Birlikteyiz sistemi, dağıtık ve merkezi olmayan bir mimari kullanarak maksimum dayanıklılık ve güvenilirlik sağlar. Her cihaz özerk olarak çalışabilir ve diğer cihazlarla otomatik olarak ağ oluşturabilir. Sistem üç ana katmandan oluşur:

**Fiziksel Katman (Physical Layer):** Raspberry Pi donanımı, LoRa modülleri, GPS sensörleri, çevresel sensörler ve güç yönetimi sistemlerini içerir. Bu katman, sistemin temel donanım altyapısını oluşturur ve çevresel koşullara dayanıklı tasarım prensipleriyle geliştirilmiştir.

**Ağ Katmanı (Network Layer):** LoRa tabanlı uzun mesafe iletişimi ve 2.4GHz düşük hızlı veri aktarımını yöneten protokol yığınını içerir. Bu katman, mesh ağ topolojisi, otomatik yönlendirme algoritmaları ve ağ keşif protokollerini implement eder.

**Uygulama Katmanı (Application Layer):** Kullanıcı arayüzü, mesaj yönetimi, konum takibi ve acil durum koordinasyon özelliklerini sağlar. Bu katman, web tabanlı arayüz ve yerel API servisleri aracılığıyla kullanıcı etkileşimini yönetir.

### Donanım Mimarisi

Sistem iki farklı donanım konfigürasyonunu destekler, her biri farklı kullanım senaryolarına optimize edilmiştir:

**Kompakt Konfigürasyon (Raspberry Pi Zero 2 W):** Taşınabilirlik ve düşük güç tüketimi öncelikli senaryolar için tasarlanmıştır. Bu konfigürasyon, kişisel acil durum kitleri, araç içi sistemler ve geçici kurulumlar için idealdir. 64GB depolama kapasitesi ile temel iletişim ve konum takibi özelliklerini sağlar.

**Gelişmiş Konfigürasyon (Raspberry Pi 5):** Sabit kurulumlar ve merkezi koordinasyon noktaları için tasarlanmıştır. Yüksek işlem gücü ve genişletilmiş bellek kapasitesi ile gelişmiş ağ yönetimi, veri analizi ve çoklu protokol desteği sağlar. Bu konfigürasyon, toplum merkezleri, okul binaları ve kritik altyapı noktalarında kullanım için uygundur.

### Yazılım Mimarisi

Yazılım mimarisi, modüler ve ölçeklenebilir tasarım prensipleriyle geliştirilmiştir. Ana bileşenler şunlardır:

**Core Communication Engine:** LoRa ve 2.4GHz iletişim protokollerini yöneten temel motor. Bu bileşen, düşük seviye donanım kontrolü, protokol yığını yönetimi ve ağ optimizasyonu işlevlerini gerçekleştirir.

**Mesh Network Manager:** Ağ topolojisi yönetimi, otomatik yönlendirme ve ağ keşif işlevlerini sağlar. Bu bileşen, dinamik ağ yapılandırması, yük dengeleme ve arıza toleransı özelliklerini implement eder.

**Emergency Coordination System:** Acil durum mesajları, konum takibi ve kaynak koordinasyonu işlevlerini yönetir. Bu sistem, öncelikli mesaj yönlendirme, otomatik konum bildirimi ve acil durum protokollerini destekler.

**Local Web Interface:** Kullanıcı etkileşimi için web tabanlı arayüz sağlar. Bu arayüz, responsive tasarım ile farklı cihaz türlerinde optimal kullanım deneyimi sunar ve offline çalışma kapasitesine sahiptir.

## Teknik Gereksinimler

### Donanım Gereksinimleri

**Temel Bileşenler:**
- Raspberry Pi Zero 2 W veya Raspberry Pi 5
- Kioxia Exceria veya Exceria Plus microSD kart (64GB minimum)
- LoRa modülü (SX1276/SX1278 tabanlı)
- 2.4GHz uzun mesafe iletişim modülü
- GPS modülü (u-blox NEO-8M veya eşdeğeri)
- Sıcaklık ve nem sensörü (DHT22 veya SHT30)
- LCD/OLED ekran (3.5" - 7" arası)
- Güç yönetimi sistemi
- Soğutma fanı (termal kontrollü)

**Kasa ve Montaj:**
- 6mm plywood kasa malzemesi
- IP65 koruma seviyesi
- Anten montaj noktaları
- Kablo geçiş sistemleri
- Termal yönetim tasarımı

### Yazılım Gereksinimleri

**İşletim Sistemi:** Raspberry Pi OS Lite (Debian tabanlı)
**Programlama Dilleri:** Python 3.9+, JavaScript, HTML5/CSS3
**Veritabanı:** SQLite (yerel depolama)
**Web Framework:** Flask (hafif ve hızlı)
**İletişim Kütüphaneleri:** 
- LoRa: RadioHead, CircuitPython
- 2.4GHz: Custom protocol implementation
- GPS: gpsd, pynmea2
- Sensörler: Adafruit CircuitPython libraries

### Ağ Gereksinimleri

**LoRa İletişimi:**
- Frekans: 868MHz (Avrupa) / 915MHz (Amerika)
- Menzil: 10-15km (açık alan)
- Veri hızı: 0.3-50 kbps
- Güç: 100mW maksimum

**2.4GHz İletişimi:**
- Frekans: 2.4GHz ISM bandı
- Menzil: 10-15km (yüksek kazançlı anten ile)
- Veri hızı: 5 Mbps hedef
- Protokol: Custom mesh protocol

## Özellik Gereksinimleri

### Temel İletişim Özellikleri

**Mesajlaşma Sistemi:** Platform, metin tabanlı mesajlaşma sistemi ile acil durum iletişimini destekler. Mesajlar otomatik olarak önceliklendirilir ve kritik acil durum mesajları normal iletişimden önce iletilir. Sistem, mesaj şifreleme ve kimlik doğrulama özellikleri ile güvenli iletişim sağlar.

**Konum Takibi:** GPS tabanlı otomatik konum bildirimi sistemi, acil durumlarda kişilerin konumlarını otomatik olarak paylaşır. Konum bilgileri sadece acil durum modunda aktif olur ve kullanıcı onayı ile çalışır. Sistem, konum geçmişi tutmaz ve gizlilik odaklı tasarım prensiplerini benimser.

**Grup İletişimi:** Önceden tanımlanmış gruplar arasında toplu mesajlaşma ve koordinasyon imkanı sağlar. Aile grupları, mahalle grupları ve acil müdahale ekipleri için özel kanallar oluşturulabilir.

### Acil Durum Özellikleri

**SOS Sistemi:** Tek tuşla acil durum sinyali gönderme özelliği, kritik durumlarda hızlı yardım çağrısı imkanı sağlar. SOS sinyali, otomatik konum bilgisi ile birlikte tüm yakın cihazlara yayınlanır.

**Kaynak Koordinasyonu:** Su, yiyecek, tıbbi malzeme gibi kritik kaynakların durumu ve ihtiyaçları koordine edilebilir. Sistem, kaynak haritası oluşturarak en yakın yardım noktalarını gösterir.

**Durum Bildirimi:** Kişisel durum bildirimi (güvende, yardıma ihtiyacı var, yaralı) sistemi ile genel durum değerlendirmesi yapılabilir.

### Teknik Özellikler

**Offline Çalışma:** Sistem, internet bağlantısı olmadan tamamen bağımsız çalışır. Tüm veriler yerel olarak saklanır ve ağ üzerinden senkronize edilir.

**Otomatik Ağ Keşfi:** Yeni cihazlar otomatik olarak keşfedilir ve ağa dahil edilir. Ağ topolojisi dinamik olarak güncellenir ve en optimal yönlendirme yolları hesaplanır.

**Güç Yönetimi:** Düşük güç tüketimi modları ile uzun süreli çalışma sağlanır. Kritik durumlarda sistem, temel iletişim özelliklerini koruyarak güç tasarrufu yapar.

**Çevresel Monitoring:** Sıcaklık ve nem sensörleri ile çevresel koşullar izlenir. Aşırı sıcaklık durumunda otomatik soğutma sistemi devreye girer.

## Kurulum ve Dağıtım Stratejisi

### Tek Komut Kurulum Sistemi

Pi-hole benzeri kurulum deneyimi sağlamak için geliştirilmiş otomatik kurulum sistemi, kullanıcıların teknik bilgi gerektirmeden sistemi kurabilmesini sağlar. Kurulum süreci şu adımları içerir:

```bash
curl -sSL https://install.birlikteyiz.org | bash
```

Bu komut, otomatik olarak sistem gereksinimlerini kontrol eder, gerekli paketleri indirir ve kurar, donanım konfigürasyonunu yapar ve sistemi çalışır duruma getirir.

### Cihaz İsimlendirme Sistemi

Her cihaz, kurulum sırasında benzersiz bir isim alır. İsimlendirme sistemi, kullanıcı dostu ve hatırlanabilir isimler oluşturur. Örnek isimler: "octopus", "dolphin", "eagle", "mountain", "river" gibi doğa temalı kelimeler kullanılır. Bu isimler, yerel ağ içinde benzersizlik garantisi ile atanır.

### Dağıtım Paketi

Müşteriye ulaştırılan paket şunları içerir:
- Önceden yapılandırılmış microSD kart
- Donanım kurulum kılavuzu
- Hızlı başlangıç rehberi
- Acil durum kullanım talimatları
- Teknik destek bilgileri

## Güvenlik ve Gizlilik

### Veri Güvenliği

Sistem, end-to-end şifreleme ile tüm iletişimi korur. Mesajlar, AES-256 şifreleme ile korunur ve sadece hedef alıcılar tarafından çözülebilir. Şifreleme anahtarları, yerel olarak üretilir ve merkezi bir sunucuda saklanmaz.

### Gizlilik Koruması

Konum bilgileri sadece acil durum modunda ve kullanıcı onayı ile paylaşılır. Sistem, kişisel veri toplama minimizasyonu prensibini benimser ve gereksiz veri saklamaz. Tüm veriler yerel olarak işlenir ve dış sunuculara gönderilmez.

### Ağ Güvenliği

Mesh ağ protokolü, kimlik doğrulama ve yetkilendirme mekanizmaları ile korunur. Yetkisiz cihazların ağa katılması engellenir ve ağ trafiği sürekli izlenir.

## Performans ve Ölçeklenebilirlik

### Ağ Performansı

LoRa iletişimi, 10-15km menzilde güvenilir veri aktarımı sağlar. 2.4GHz sistemi, 5Mbps veri hızı ile multimedya içerik paylaşımını destekler. Mesh ağ topolojisi, otomatik yük dengeleme ile optimal performans sağlar.

### Ölçeklenebilirlik

Sistem, binlerce cihazı destekleyebilecek şekilde tasarlanmıştır. Hiyerarşik ağ yapısı ile büyük coğrafi alanlar kapsanabilir. Her cihaz, maksimum 50 doğrudan bağlantıyı yönetebilir.

### Güvenilirlik

Sistem, %99.9 uptime hedefi ile tasarlanmıştır. Çoklu yedeklilik mekanizmaları, tek nokta arızalarına karşı koruma sağlar. Otomatik arıza tespiti ve kurtarma sistemleri, minimum kesinti süresi sağlar.

Bu sistem mimarisi, açık kaynak prensipleri ile geliştirilmiş, toplum odaklı bir acil durum iletişim platformu oluşturmayı hedefler. Modüler tasarım, gelecekteki geliştirmeler ve özelleştirmeler için esneklik sağlar.

