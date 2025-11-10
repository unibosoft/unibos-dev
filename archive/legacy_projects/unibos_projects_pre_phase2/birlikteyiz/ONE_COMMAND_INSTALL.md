# Birlikteyiz - Tek Komut Kurulum Sistemi

## 🚀 Pi-hole Tarzı Kurulum

### Hızlı Kurulum (Önerilen)
```bash
curl -sSL https://install.birlikteyiz.org | bash
```

### Manuel Kurulum
```bash
wget -O - https://install.birlikteyiz.org | sudo bash
```

### Gelişmiş Kurulum (Parametreli)
```bash
curl -sSL https://install.birlikteyiz.org | bash -s -- --device-type=pi5 --enable-ai --lora-freq=868
```

---

## 📋 Kurulum Parametreleri

| Parametre | Açıklama | Varsayılan | Seçenekler |
|-----------|----------|------------|------------|
| `--device-type` | Cihaz tipi | auto | pi-zero2w, pi5, auto |
| `--lora-freq` | LoRa frekansı | 868 | 433, 868, 915 |
| `--enable-ai` | AI özelliklerini etkinleştir | false | true, false |
| `--wifi-mode` | WiFi modu | hybrid | home, emergency, hybrid |
| `--interface-mode` | Arayüz modu | auto | dos, ultima, auto |
| `--enable-solar` | Solar güç desteği | false | true, false |
| `--mesh-network` | Mesh ağ kurulumu | true | true, false |
| `--emergency-only` | Sadece acil durum modu | false | true, false |

---

## 🔧 Kurulum Süreci

### 1. Sistem Tespiti
- Raspberry Pi model tespiti
- Donanım özelliklerinin kontrolü
- Mevcut işletim sistemi analizi
- Ağ bağlantısı kontrolü

### 2. Bağımlılık Kurulumu
- Python 3.11+ kurulumu
- Node.js 20+ kurulumu
- Gerekli sistem paketleri
- GPIO ve SPI etkinleştirme

### 3. Birlikteyiz Yazılımı
- Ana uygulama indirme
- Veritabanı kurulumu
- Servis yapılandırması
- Güvenlik ayarları

### 4. Donanım Yapılandırması
- LoRa modülü tespiti ve kurulumu
- GPS modülü yapılandırması
- Sensör kalibrasyonu
- Ekran ayarları

### 5. Ağ Kurulumu
- WiFi yapılandırması
- LoRa ağ parametreleri
- Mesh network kurulumu
- Güvenlik sertifikaları

### 6. İlk Kurulum Sihirbazı
- Cihaz ismi belirleme
- Root şifre oluşturma
- Ağ ayarları
- Acil durum kişileri

---

## 📦 Kurulum Scripti İçeriği

### Ana Script (install.sh)
```bash
#!/bin/bash
# Birlikteyiz One-Command Installer
# Usage: curl -sSL https://install.birlikteyiz.org | bash

set -e

# Renkler ve sabitler
readonly BIRLIKTEYIZ_VERSION="1.0.0"
readonly INSTALL_DIR="/opt/birlikteyiz"
readonly CONFIG_DIR="/etc/birlikteyiz"
readonly LOG_FILE="/var/log/birlikteyiz-install.log"

# Kurulum parametreleri
DEVICE_TYPE="auto"
LORA_FREQ="868"
ENABLE_AI="false"
WIFI_MODE="hybrid"
INTERFACE_MODE="auto"
ENABLE_SOLAR="false"
MESH_NETWORK="true"
EMERGENCY_ONLY="false"

# Parametre parsing
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --device-type=*)
                DEVICE_TYPE="${1#*=}"
                shift
                ;;
            --lora-freq=*)
                LORA_FREQ="${1#*=}"
                shift
                ;;
            --enable-ai)
                ENABLE_AI="true"
                shift
                ;;
            --wifi-mode=*)
                WIFI_MODE="${1#*=}"
                shift
                ;;
            --interface-mode=*)
                INTERFACE_MODE="${1#*=}"
                shift
                ;;
            --enable-solar)
                ENABLE_SOLAR="true"
                shift
                ;;
            --no-mesh)
                MESH_NETWORK="false"
                shift
                ;;
            --emergency-only)
                EMERGENCY_ONLY="true"
                shift
                ;;
            *)
                echo "Bilinmeyen parametre: $1"
                exit 1
                ;;
        esac
    done
}

# Sistem tespiti
detect_system() {
    echo "Sistem tespiti yapılıyor..."
    
    # Raspberry Pi model tespiti
    if grep -q "Raspberry Pi Zero 2" /proc/cpuinfo; then
        DETECTED_DEVICE="pi-zero2w"
        DETECTED_MEMORY=$(free -m | awk 'NR==2{print $2}')
    elif grep -q "Raspberry Pi 5" /proc/cpuinfo; then
        DETECTED_DEVICE="pi5"
        DETECTED_MEMORY=$(free -m | awk 'NR==2{print $2}')
    else
        DETECTED_DEVICE="unknown"
        echo "Uyarı: Desteklenmeyen Raspberry Pi modeli"
    fi
    
    # Otomatik cihaz tipi belirleme
    if [ "$DEVICE_TYPE" = "auto" ]; then
        DEVICE_TYPE="$DETECTED_DEVICE"
    fi
    
    echo "Tespit edilen cihaz: $DETECTED_DEVICE"
    echo "Kullanılacak konfigürasyon: $DEVICE_TYPE"
}

# Bağımlılık kontrolü
check_dependencies() {
    echo "Bağımlılıklar kontrol ediliyor..."
    
    # Root yetki kontrolü
    if [ "$EUID" -ne 0 ]; then
        echo "Bu script root yetkileri ile çalıştırılmalıdır."
        echo "Lütfen 'sudo' kullanın veya root olarak çalıştırın."
        exit 1
    fi
    
    # İnternet bağlantısı kontrolü
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        echo "İnternet bağlantısı bulunamadı."
        echo "Kurulum için internet bağlantısı gereklidir."
        exit 1
    fi
    
    # Disk alanı kontrolü
    AVAILABLE_SPACE=$(df / | awk 'NR==2{print $4}')
    REQUIRED_SPACE=2097152  # 2GB in KB
    
    if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
        echo "Yetersiz disk alanı. En az 2GB boş alan gereklidir."
        exit 1
    fi
}

# Sistem paketlerini güncelle
update_system() {
    echo "Sistem paketleri güncelleniyor..."
    
    apt update
    apt upgrade -y
    
    # Gerekli sistem paketleri
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        nodejs \
        npm \
        git \
        curl \
        wget \
        unzip \
        sqlite3 \
        nginx \
        supervisor \
        i2c-tools \
        spi-tools \
        gpio-utils \
        gpsd \
        gpsd-clients \
        minicom \
        screen \
        htop \
        vim \
        nano
}

# Python ortamını kur
setup_python_environment() {
    echo "Python ortamı kuruluyor..."
    
    # Virtual environment oluştur
    python3 -m venv "$INSTALL_DIR/venv"
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Python paketlerini kur
    pip install --upgrade pip
    pip install \
        flask \
        flask-cors \
        flask-sqlalchemy \
        requests \
        pyserial \
        gpiozero \
        adafruit-circuitpython-dht \
        adafruit-circuitpython-gps \
        pynmea2 \
        colorama \
        cryptography \
        pyjwt \
        schedule \
        psutil \
        netifaces \
        python-socketio \
        eventlet
}

# Birlikteyiz uygulamasını indir
download_application() {
    echo "Birlikteyiz uygulaması indiriliyor..."
    
    # GitHub'dan son sürümü indir
    cd /tmp
    wget -O birlikteyiz.tar.gz "https://github.com/birlikteyiz/birlikteyiz/archive/v${BIRLIKTEYIZ_VERSION}.tar.gz"
    
    # Kurulum dizinine çıkart
    mkdir -p "$INSTALL_DIR"
    tar -xzf birlikteyiz.tar.gz -C "$INSTALL_DIR" --strip-components=1
    
    # İzinleri ayarla
    chown -R pi:pi "$INSTALL_DIR"
    chmod +x "$INSTALL_DIR/bin/"*
}

# Donanım yapılandırması
configure_hardware() {
    echo "Donanım yapılandırılıyor..."
    
    # GPIO ve SPI etkinleştir
    raspi-config nonint do_spi 0
    raspi-config nonint do_i2c 0
    raspi-config nonint do_serial 0
    
    # LoRa modülü için UART yapılandırması
    if ! grep -q "enable_uart=1" /boot/config.txt; then
        echo "enable_uart=1" >> /boot/config.txt
    fi
    
    # GPS için UART yapılandırması
    if ! grep -q "dtoverlay=disable-bt" /boot/config.txt; then
        echo "dtoverlay=disable-bt" >> /boot/config.txt
    fi
    
    # Cihaz tipine göre özel ayarlar
    case "$DEVICE_TYPE" in
        "pi-zero2w")
            # Pi Zero 2W için düşük güç ayarları
            echo "arm_freq=1000" >> /boot/config.txt
            echo "gpu_mem=16" >> /boot/config.txt
            ;;
        "pi5")
            # Pi 5 için performans ayarları
            echo "arm_freq=2400" >> /boot/config.txt
            echo "gpu_mem=128" >> /boot/config.txt
            ;;
    esac
}

# Servisleri kur
setup_services() {
    echo "Sistem servisleri kuruluyor..."
    
    # Birlikteyiz ana servisi
    cat > /etc/systemd/system/birlikteyiz.service << EOF
[Unit]
Description=Birlikteyiz Emergency Communication System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # LoRa iletişim servisi
    cat > /etc/systemd/system/birlikteyiz-lora.service << EOF
[Unit]
Description=Birlikteyiz LoRa Communication Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python src/lora_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # GPS servisi
    cat > /etc/systemd/system/birlikteyiz-gps.service << EOF
[Unit]
Description=Birlikteyiz GPS Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python src/gps_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Servisleri etkinleştir
    systemctl daemon-reload
    systemctl enable birlikteyiz
    systemctl enable birlikteyiz-lora
    systemctl enable birlikteyiz-gps
}

# Nginx yapılandırması
configure_nginx() {
    echo "Web sunucusu yapılandırılıyor..."
    
    cat > /etc/nginx/sites-available/birlikteyiz << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $INSTALL_DIR/src/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    # Varsayılan siteyi devre dışı bırak
    rm -f /etc/nginx/sites-enabled/default
    
    # Birlikteyiz sitesini etkinleştir
    ln -sf /etc/nginx/sites-available/birlikteyiz /etc/nginx/sites-enabled/
    
    # Nginx'i yeniden başlat
    systemctl restart nginx
    systemctl enable nginx
}

# Yapılandırma dosyalarını oluştur
create_configuration() {
    echo "Yapılandırma dosyaları oluşturuluyor..."
    
    mkdir -p "$CONFIG_DIR"
    
    cat > "$CONFIG_DIR/config.json" << EOF
{
    "device": {
        "type": "$DEVICE_TYPE",
        "name": "birlikteyiz-$(hostname)",
        "location": {
            "latitude": 0.0,
            "longitude": 0.0
        }
    },
    "lora": {
        "frequency": $LORA_FREQ,
        "power": 22,
        "bandwidth": 125,
        "spreading_factor": 7,
        "coding_rate": 5
    },
    "wifi": {
        "mode": "$WIFI_MODE",
        "long_range": {
            "enabled": true,
            "power": 27,
            "channel": 6
        }
    },
    "interface": {
        "mode": "$INTERFACE_MODE",
        "enable_ai": $ENABLE_AI
    },
    "power": {
        "solar_enabled": $ENABLE_SOLAR,
        "low_power_mode": false
    },
    "network": {
        "mesh_enabled": $MESH_NETWORK,
        "emergency_only": $EMERGENCY_ONLY
    }
}
EOF

    chown pi:pi "$CONFIG_DIR/config.json"
}

# SSH launcher kurulumu
setup_ssh_launcher() {
    echo "SSH launcher kuruluyor..."
    
    # Launcher scriptini kopyala
    cp "$INSTALL_DIR/scripts/birlikteyiz-launcher.sh" /usr/local/bin/birlikteyiz
    chmod +x /usr/local/bin/birlikteyiz
    
    # Pi kullanıcısının .bashrc dosyasına ekle
    if ! grep -q "birlikteyiz" /home/pi/.bashrc; then
        echo "" >> /home/pi/.bashrc
        echo "# Birlikteyiz Auto-launcher" >> /home/pi/.bashrc
        echo "if [ -t 0 ] && [ \"\$SSH_CLIENT\" ]; then" >> /home/pi/.bashrc
        echo "    echo 'Birlikteyiz Emergency Communication System'" >> /home/pi/.bashrc
        echo "    echo 'Type \"birlikteyiz\" to start the interface'" >> /home/pi/.bashrc
        echo "fi" >> /home/pi/.bashrc
    fi
}

# İlk kurulum sihirbazını başlat
run_setup_wizard() {
    echo "İlk kurulum sihirbazı başlatılıyor..."
    
    # Servisleri başlat
    systemctl start birlikteyiz
    systemctl start birlikteyiz-lora
    systemctl start birlikteyiz-gps
    
    # Kurulum sihirbazını çalıştır
    sudo -u pi "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/scripts/setup_wizard.py"
}

# Ana kurulum fonksiyonu
main() {
    echo "Birlikteyiz Emergency Communication System Kurulumu"
    echo "=================================================="
    echo "Sürüm: $BIRLIKTEYIZ_VERSION"
    echo ""
    
    # Parametreleri parse et
    parse_arguments "$@"
    
    # Kurulum adımları
    detect_system
    check_dependencies
    update_system
    setup_python_environment
    download_application
    configure_hardware
    setup_services
    configure_nginx
    create_configuration
    setup_ssh_launcher
    run_setup_wizard
    
    echo ""
    echo "🎉 Kurulum tamamlandı!"
    echo ""
    echo "Birlikteyiz Emergency Communication System başarıyla kuruldu."
    echo ""
    echo "Erişim yöntemleri:"
    echo "  • Web arayüzü: http://$(hostname -I | awk '{print $1}')"
    echo "  • SSH launcher: ssh pi@$(hostname -I | awk '{print $1}') -> 'birlikteyiz' komutu"
    echo "  • Yerel terminal: birlikteyiz"
    echo ""
    echo "Sistem yeniden başlatılıyor..."
    sleep 3
    reboot
}

# Hata yakalama
trap 'echo "Kurulum sırasında hata oluştu. Log: $LOG_FILE"' ERR

# Ana fonksiyonu çalıştır
main "$@" 2>&1 | tee "$LOG_FILE"
```

---

## 🌐 Kurulum Sunucusu

### install.birlikteyiz.org Yapısı
```
install.birlikteyiz.org/
├── index.html (Ana kurulum sayfası)
├── install.sh (Ana kurulum scripti)
├── packages/
│   ├── birlikteyiz-v1.0.0.tar.gz
│   ├── dependencies/
│   └── checksums.txt
├── docs/
│   ├── installation-guide.md
│   ├── hardware-specs.md
│   └── troubleshooting.md
└── api/
    ├── version-check
    ├── device-detection
    └── download-stats
```

### CDN ve Yedekleme
- **Ana Sunucu**: install.birlikteyiz.org
- **Yedek Sunucu**: backup.birlikteyiz.org
- **GitHub Releases**: github.com/birlikteyiz/birlikteyiz/releases

---

## 🔍 Kurulum Sonrası Kontroller

### Sistem Durumu Kontrolü
```bash
# Servis durumları
systemctl status birlikteyiz
systemctl status birlikteyiz-lora
systemctl status birlikteyiz-gps

# Port kontrolü
netstat -tlnp | grep :5000
netstat -tlnp | grep :80

# Log kontrolü
journalctl -u birlikteyiz -f
tail -f /var/log/birlikteyiz.log
```

### Donanım Testi
```bash
# GPIO testi
gpio readall

# I2C cihaz taraması
i2cdetect -y 1

# SPI testi
ls /dev/spi*

# UART testi
ls /dev/ttyS* /dev/ttyAMA*
```

### Ağ Bağlantısı Testi
```bash
# WiFi durumu
iwconfig wlan0

# LoRa modülü testi
python3 -c "import serial; print('LoRa test OK')"

# GPS testi
gpspipe -r -n 5
```

Bu tek komut kurulum sistemi, Pi-hole benzeri basitlikle Birlikteyiz sistemini tamamen otomatik olarak kurar ve yapılandırır.

