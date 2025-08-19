#!/bin/bash
# recaria Linux Kurulum Scripti
# "ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria!"

echo "🥕 recaria v003 - Linux Kurulum Scripti"
echo "💫 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria!"
echo

# Platform kontrolü
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Bu script sadece Linux için tasarlanmıştır!"
    exit 1
fi

# Distribution detection
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
else
    DISTRO="unknown"
fi

echo "🔍 Platform: Linux $DISTRO $VERSION"

# Architecture detection
ARCH=$(uname -m)
echo "🔧 Architecture: $ARCH"

# Raspberry Pi detection
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "🥧 Raspberry Pi tespit edildi!"
    IS_RPI=true
else
    IS_RPI=false
fi

# Package manager detection
if command -v apt &> /dev/null; then
    PKG_MANAGER="apt"
    UPDATE_CMD="sudo apt update"
    INSTALL_CMD="sudo apt install -y"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
    UPDATE_CMD="sudo yum update"
    INSTALL_CMD="sudo yum install -y"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
    UPDATE_CMD="sudo pacman -Sy"
    INSTALL_CMD="sudo pacman -S --noconfirm"
else
    echo "❌ Desteklenen paket yöneticisi bulunamadı!"
    exit 1
fi

echo "📦 Paket yöneticisi: $PKG_MANAGER"

# System update
echo "🔄 Sistem güncelleniyor..."
$UPDATE_CMD

# Python3 kurulumu
if ! command -v python3 &> /dev/null; then
    echo "🐍 Python3 kuruluyor..."
    case $PKG_MANAGER in
        "apt")
            $INSTALL_CMD python3 python3-pip python3-dev
            ;;
        "yum")
            $INSTALL_CMD python3 python3-pip python3-devel
            ;;
        "pacman")
            $INSTALL_CMD python python-pip
            ;;
    esac
else
    echo "✅ Python3 mevcut: $(python3 --version)"
fi

# Pip kontrolü
if ! command -v pip3 &> /dev/null; then
    echo "📦 pip3 kuruluyor..."
    case $PKG_MANAGER in
        "apt")
            $INSTALL_CMD python3-pip
            ;;
        "yum")
            $INSTALL_CMD python3-pip
            ;;
        "pacman")
            $INSTALL_CMD python-pip
            ;;
    esac
else
    echo "✅ pip3 mevcut"
fi

# Gerekli sistem kütüphaneleri
echo "📚 Sistem kütüphaneleri kuruluyor..."
case $PKG_MANAGER in
    "apt")
        $INSTALL_CMD curl wget git ncurses-dev
        ;;
    "yum")
        $INSTALL_CMD curl wget git ncurses-devel
        ;;
    "pacman")
        $INSTALL_CMD curl wget git ncurses
        ;;
esac

# Python kütüphaneleri
echo "🐍 Python kütüphaneleri kuruluyor..."
pip3 install --user requests

# Raspberry Pi özel ayarları
if [[ "$IS_RPI" == true ]]; then
    echo "🥧 Raspberry Pi optimizasyonları uygulanıyor..."
    
    # GPU memory split (opsiyonel)
    if command -v raspi-config &> /dev/null; then
        echo "🎮 GPU bellek ayarları optimize ediliyor..."
        # sudo raspi-config nonint do_memory_split 64
    fi
    
    # I2C ve SPI aktifleştir (sensörler için)
    if [[ -f /boot/config.txt ]]; then
        if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
            echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
        fi
        if ! grep -q "dtparam=spi=on" /boot/config.txt; then
            echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
        fi
    fi
fi

# Kurulum dizini oluştur
INSTALL_DIR="$HOME/.recaria"
mkdir -p "$INSTALL_DIR"

# recaria dosyalarını kopyala
echo "📁 recaria dosyaları kopyalanıyor..."
cp recaria_terminal.py "$INSTALL_DIR/"

# Executable script oluştur
cat > "$INSTALL_DIR/recaria" << 'EOF'
#!/bin/bash
cd "$HOME/.recaria"
python3 recaria_terminal.py "$@"
EOF

chmod +x "$INSTALL_DIR/recaria"

# PATH'e ekle
SHELL_RC=""
if [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
elif [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [[ -n "$SHELL_RC" ]]; then
    if ! grep -q "/.recaria" "$SHELL_RC" 2>/dev/null; then
        echo "🔧 PATH'e recaria ekleniyor..."
        echo 'export PATH="$HOME/.recaria:$PATH"' >> "$SHELL_RC"
        echo "⚠️  Yeni terminal açın veya 'source $SHELL_RC' çalıştırın"
    fi
fi

# Desktop entry oluştur (GUI varsa)
if [[ -n "$DISPLAY" ]] || [[ -n "$WAYLAND_DISPLAY" ]]; then
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    
    cat > "$DESKTOP_DIR/recaria.desktop" << EOF
[Desktop Entry]
Name=recaria
Comment=ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria!
Exec=$HOME/.recaria/recaria
Icon=applications-games
Terminal=true
Type=Application
Categories=Game;
EOF
    
    echo "🖥️  Desktop entry oluşturuldu"
fi

# Systemd service oluştur (opsiyonel)
if command -v systemctl &> /dev/null; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    
    cat > "$SERVICE_DIR/recaria.service" << EOF
[Unit]
Description=recaria Game Service
After=network.target

[Service]
Type=simple
ExecStart=$HOME/.recaria/recaria --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
    
    echo "🔧 Systemd service oluşturuldu (systemctl --user enable recaria)"
fi

echo
echo "✅ recaria v003 başarıyla kuruldu!"
echo
echo "🎮 Oyunu başlatmak için:"
echo "   recaria"
echo
echo "📍 Kurulum dizini: $INSTALL_DIR"
echo "💫 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria!"
echo

# Test çalıştırması
echo "🧪 Test çalıştırması yapılıyor..."
cd "$INSTALL_DIR"
python3 recaria_terminal.py --version 2>/dev/null || echo "⚠️  Test başarısız, manuel kontrol gerekli"

echo
echo "🎉 Kurulum tamamlandı! Yeni terminal açıp 'recaria' yazarak oyunu başlatabilirsiniz."

# Raspberry Pi özel mesajı
if [[ "$IS_RPI" == true ]]; then
    echo
    echo "🥧 Raspberry Pi Özel Notlar:"
    echo "   - GPIO pinleri oyun kontrolü için kullanılabilir"
    echo "   - I2C ve SPI sensör desteği aktifleştirildi"
    echo "   - Yeniden başlatma önerilir: sudo reboot"
fi

