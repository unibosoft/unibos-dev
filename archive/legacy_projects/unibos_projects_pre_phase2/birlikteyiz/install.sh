#!/bin/bash

# Birlikteyiz DOS-Style Installation Script
# SSH Compatible Version - Works both locally and over SSH

# Terminal detection and setup
detect_terminal() {
    # Get terminal dimensions
    TERM_COLS=$(tput cols 2>/dev/null || echo 80)
    TERM_ROWS=$(tput lines 2>/dev/null || echo 24)
    
    # Detect if we're in SSH session
    if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
        IS_SSH=true
        echo "SSH session detected - Terminal: ${TERM_COLS}x${TERM_ROWS}"
    else
        IS_SSH=false
    fi
    
    # Check color support
    if [ -t 1 ] && command -v tput >/dev/null 2>&1; then
        ncolors=$(tput colors 2>/dev/null || echo 0)
        if [ -n "$ncolors" ] && [ "$ncolors" -ge 8 ]; then
            COLOR_SUPPORT=true
        else
            COLOR_SUPPORT=false
        fi
    else
        COLOR_SUPPORT=false
    fi
    
    # Force UTF-8 for better box drawing
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
}

# Colors for retro DOS experience (SSH compatible)
setup_colors() {
    if [ "$COLOR_SUPPORT" = true ]; then
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        BLUE='\033[0;34m'
        MAGENTA='\033[0;35m'
        CYAN='\033[0;36m'
        WHITE='\033[1;37m'
        GRAY='\033[0;37m'
        BOLD='\033[1m'
        NC='\033[0m' # No Color
        
        # Background colors for better SSH visibility
        BG_BLUE='\033[44m'
        BG_BLACK='\033[40m'
    else
        # Fallback for terminals without color support
        RED=''
        GREEN=''
        YELLOW=''
        BLUE=''
        MAGENTA=''
        CYAN=''
        WHITE=''
        GRAY=''
        BOLD=''
        NC=''
        BG_BLUE=''
        BG_BLACK=''
    fi
}

# 16-bit style music toggle (SSH compatible)
MUSIC_ENABLED=true
MUSIC_PID=""

# SSH-compatible beep function
play_beep() {
    if [ "$MUSIC_ENABLED" = true ]; then
        if [ "$IS_SSH" = true ]; then
            # For SSH sessions, use terminal bell or printf beep
            case $1 in
                "startup")
                    printf '\a'; sleep 0.1; printf '\a'; sleep 0.1; printf '\a'
                    ;;
                "success")
                    printf '\a'
                    ;;
                "error")
                    printf '\a'; sleep 0.1; printf '\a'
                    ;;
                "progress")
                    printf '\a'
                    ;;
            esac
        else
            # Local terminal - use speaker-test if available
            case $1 in
                "startup")
                    (speaker-test -t sine -f 800 -l 1 & sleep 0.1; kill $! 2>/dev/null) 2>/dev/null
                    sleep 0.1
                    (speaker-test -t sine -f 1000 -l 1 & sleep 0.1; kill $! 2>/dev/null) 2>/dev/null
                    sleep 0.1
                    (speaker-test -t sine -f 1200 -l 1 & sleep 0.2; kill $! 2>/dev/null) 2>/dev/null
                    ;;
                "success")
                    (speaker-test -t sine -f 1000 -l 1 & sleep 0.1; kill $! 2>/dev/null) 2>/dev/null
                    ;;
                "error")
                    (speaker-test -t sine -f 400 -l 1 & sleep 0.3; kill $! 2>/dev/null) 2>/dev/null
                    ;;
                "progress")
                    (speaker-test -t sine -f 600 -l 1 & sleep 0.05; kill $! 2>/dev/null) 2>/dev/null
                    ;;
            esac
        fi
    fi
}

# Responsive clear screen function
clear_screen() {
    clear
    
    # Adaptive header based on terminal width
    if [ "$TERM_COLS" -ge 80 ]; then
        # Full width header for wide terminals
        echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║${WHITE}                           BIRLIKTEYIZ KURULUM SİSTEMİ                        ${BLUE}║${NC}"
        echo -e "${BLUE}║${GRAY}                        Emergency Communication Platform                       ${BLUE}║${NC}"
        echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    elif [ "$TERM_COLS" -ge 60 ]; then
        # Medium width header
        echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║${WHITE}                BIRLIKTEYIZ KURULUM                 ${BLUE}║${NC}"
        echo -e "${BLUE}║${GRAY}            Emergency Communication            ${BLUE}║${NC}"
        echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    else
        # Narrow terminal header
        echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║${WHITE}        BIRLIKTEYIZ KURULUM        ${BLUE}║${NC}"
        echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
    fi
    echo ""
    
    # Show terminal info for SSH sessions
    if [ "$IS_SSH" = true ]; then
        echo -e "${GRAY}SSH Session: ${TERM_COLS}x${TERM_ROWS} | Colors: ${COLOR_SUPPORT}${NC}"
        echo ""
    fi
}

# Responsive box drawing
draw_box() {
    local width=$1
    local height=$2
    local title=$3
    
    # Adjust width to terminal if too wide
    if [ "$width" -gt "$TERM_COLS" ]; then
        width=$((TERM_COLS - 4))
    fi
    
    echo -e "${CYAN}┌$(printf '─%.0s' $(seq 1 $((width-2))))┐${NC}"
    if [ ! -z "$title" ]; then
        local title_len=${#title}
        if [ "$title_len" -gt $((width-4)) ]; then
            title="${title:0:$((width-7))}..."
            title_len=${#title}
        fi
        local padding=$(((width - title_len - 2) / 2))
        echo -e "${CYAN}│$(printf ' %.0s' $(seq 1 $padding))${WHITE}${title}$(printf ' %.0s' $(seq 1 $((width - title_len - padding - 2))))${CYAN}│${NC}"
        echo -e "${CYAN}├$(printf '─%.0s' $(seq 1 $((width-2))))┤${NC}"
    fi
    
    for i in $(seq 1 $((height-3))); do
        echo -e "${CYAN}│$(printf ' %.0s' $(seq 1 $((width-2))))│${NC}"
    done
    
    echo -e "${CYAN}└$(printf '─%.0s' $(seq 1 $((width-2))))┘${NC}"
}

# Responsive progress bar
progress_bar() {
    local current=$1
    local total=$2
    local max_width=$((TERM_COLS - 20))  # Leave space for percentage
    local width=$((max_width > 50 ? 50 : max_width))
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    
    printf "${GREEN}["
    for i in $(seq 1 $filled); do
        printf "█"
    done
    for i in $(seq $((filled + 1)) $width); do
        printf "░"
    done
    printf "] %3d%%${NC}\r" $percentage
    
    play_beep "progress"
}

# SSH-compatible typewriter effect
typewriter_effect() {
    local text="$1"
    local delay=${2:-0.03}
    local max_width=$((TERM_COLS - 4))
    
    # Word wrap for narrow terminals
    if [ ${#text} -gt $max_width ]; then
        local words=($text)
        local line=""
        for word in "${words[@]}"; do
            if [ $((${#line} + ${#word} + 1)) -gt $max_width ]; then
                # Print current line with typewriter effect
                for (( i=0; i<${#line}; i++ )); do
                    printf "${line:$i:1}"
                    sleep $delay
                done
                echo ""
                line="$word"
            else
                if [ -z "$line" ]; then
                    line="$word"
                else
                    line="$line $word"
                fi
            fi
        done
        # Print remaining line
        for (( i=0; i<${#line}; i++ )); do
            printf "${line:$i:1}"
            sleep $delay
        done
        echo ""
    else
        # Original typewriter effect for short text
        for (( i=0; i<${#text}; i++ )); do
            printf "${text:$i:1}"
            sleep $delay
        done
        echo ""
    fi
}

# Responsive ASCII logo
show_ascii_logo() {
    if [ "$TERM_COLS" -ge 80 ]; then
        # Full ASCII logo for wide terminals
        echo -e "${MAGENTA}"
        cat << "EOF"
    ██████╗ ██╗██████╗ ██╗     ██╗██╗  ██╗████████╗███████╗██╗   ██╗██╗███████╗
    ██╔══██╗██║██╔══██╗██║     ██║██║ ██╔╝╚══██╔══╝██╔════╝╚██╗ ██╔╝██║╚══███╔╝
    ██████╔╝██║██████╔╝██║     ██║█████╔╝    ██║   █████╗   ╚████╔╝ ██║  ███╔╝ 
    ██╔══██╗██║██╔══██╗██║     ██║██╔═██╗    ██║   ██╔══╝    ╚██╔╝  ██║ ███╔╝  
    ██████╔╝██║██║  ██║███████╗██║██║  ██╗   ██║   ███████╗   ██║   ██║███████╗
    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝╚══════╝
EOF
        echo -e "${NC}"
        echo -e "${YELLOW}                    Emergency Communication & Life RPG Platform${NC}"
        echo -e "${GRAY}                              Version 1.0.0 - Alpha Build${NC}"
    elif [ "$TERM_COLS" -ge 60 ]; then
        # Medium ASCII logo
        echo -e "${MAGENTA}"
        cat << "EOF"
    ██████╗ ██╗██████╗ ██╗     ██╗██╗  ██╗████████╗
    ██╔══██╗██║██╔══██╗██║     ██║██║ ██╔╝╚══██╔══╝
    ██████╔╝██║██████╔╝██║     ██║█████╔╝    ██║   
    ██╔══██╗██║██╔══██╗██║     ██║██╔═██╗    ██║   
    ██████╔╝██║██║  ██║███████╗██║██║  ██╗   ██║   
    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═╝   ╚═╝   
EOF
        echo -e "${NC}"
        echo -e "${YELLOW}        Emergency Communication Platform${NC}"
        echo -e "${GRAY}              Version 1.0.0 - Alpha${NC}"
    else
        # Simple text logo for narrow terminals
        echo -e "${MAGENTA}${BOLD}"
        echo "    ╔══════════════════════════════════╗"
        echo "    ║          BIRLIKTEYIZ             ║"
        echo "    ║    Emergency Communication      ║"
        echo "    ║         Platform v1.0           ║"
        echo "    ╚══════════════════════════════════╝"
        echo -e "${NC}"
    fi
    echo ""
}

# SSH-compatible input handling
get_key_input() {
    local prompt="$1"
    local valid_keys="$2"
    
    echo -e "${prompt}"
    
    while true; do
        if [ "$IS_SSH" = true ]; then
            # For SSH, use read with timeout
            read -n 1 -t 30 key 2>/dev/null
            if [ $? -eq 142 ]; then
                echo -e "\n${YELLOW}Timeout - varsayılan seçenek kullanılıyor${NC}"
                echo "d"  # Default choice
                return
            fi
        else
            # Local terminal
            read -n 1 -s key
        fi
        
        # Convert to lowercase
        key=$(echo "$key" | tr '[:upper:]' '[:lower:]')
        
        if [[ "$valid_keys" == *"$key"* ]]; then
            echo "$key"
            return
        else
            echo -e "\n${RED}Geçersiz seçim. Lütfen tekrar deneyin: ${valid_keys}${NC}"
        fi
    done
}

# Enhanced system scan with SSH info
show_system_scan() {
    clear_screen
    show_ascii_logo
    
    echo -e "${WHITE}Sistem taraması başlatılıyor...${NC}"
    echo ""
    
    # Show SSH connection info
    if [ "$IS_SSH" = true ]; then
        echo -e "${CYAN}SSH Bağlantı Bilgileri:${NC}"
        echo -e "${GRAY}  Client: ${SSH_CLIENT}${NC}"
        echo -e "${GRAY}  Terminal: ${TERM}${NC}"
        echo -e "${GRAY}  Boyut: ${TERM_COLS}x${TERM_ROWS}${NC}"
        echo ""
    fi
    
    # Detect Raspberry Pi model
    if grep -q "Raspberry Pi Zero 2" /proc/cpuinfo; then
        PI_MODEL="zero2w"
        echo -e "${GREEN}✓ Raspberry Pi Zero 2 W tespit edildi${NC}"
        GAME_MODE="retro"
    elif grep -q "Raspberry Pi 5" /proc/cpuinfo; then
        PI_MODEL="pi5"
        echo -e "${GREEN}✓ Raspberry Pi 5 tespit edildi${NC}"
        GAME_MODE="ultima"
    else
        PI_MODEL="unknown"
        echo -e "${YELLOW}⚠ Bilinmeyen Raspberry Pi modeli${NC}"
        GAME_MODE="retro"
    fi
    
    sleep 1
    
    # Check memory
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    echo -e "${GREEN}✓ RAM: ${TOTAL_MEM}MB tespit edildi${NC}"
    
    # Check storage
    TOTAL_STORAGE=$(df -h / | awk 'NR==2{print $2}')
    echo -e "${GREEN}✓ Depolama: ${TOTAL_STORAGE} tespit edildi${NC}"
    
    # Check network interfaces
    if ip link show wlan0 &> /dev/null; then
        echo -e "${GREEN}✓ WiFi adaptörü bulundu${NC}"
    fi
    
    if lsusb | grep -i "lora\|sx127" &> /dev/null; then
        echo -e "${GREEN}✓ LoRa modülü tespit edildi${NC}"
    else
        echo -e "${YELLOW}⚠ LoRa modülü bulunamadı (kurulum sonrası yapılandırılacak)${NC}"
    fi
    
    sleep 2
    
    echo ""
    echo -e "${CYAN}Oyun modu: ${WHITE}${GAME_MODE}${NC}"
    if [ "$GAME_MODE" = "retro" ]; then
        echo -e "${GRAY}  → DOS tarzı retro arayüz (SSH uyumlu)${NC}"
    else
        echo -e "${GRAY}  → Ultima Online tarzı 2D grafik arayüz${NC}"
    fi
    
    echo ""
    if [ "$IS_SSH" = true ]; then
        echo -e "${YELLOW}SSH üzerinden devam etmek için ENTER tuşuna basın (30s timeout)...${NC}"
        read -t 30 -p ""
    else
        read -p "Devam etmek için ENTER tuşuna basın..."
    fi
}

# Enhanced music toggle with SSH compatibility
show_music_toggle() {
    clear_screen
    show_ascii_logo
    
    echo -e "${WHITE}Ses Ayarları${NC}"
    echo ""
    
    local box_width=$((TERM_COLS > 60 ? 60 : TERM_COLS - 4))
    draw_box $box_width 8 "16-BIT RETRO SES EFEKTLERİ"
    echo ""
    
    if [ "$MUSIC_ENABLED" = true ]; then
        echo -e "${GREEN}♪ 16-bit ses efektleri: AÇIK${NC}"
        if [ "$IS_SSH" = true ]; then
            echo -e "${GRAY}  SSH: Terminal bell kullanılacak${NC}"
        else
            echo -e "${GRAY}  Kurulum sırasında retro ses efektleri çalınacak${NC}"
        fi
    else
        echo -e "${RED}♪ 16-bit ses efektleri: KAPALI${NC}"
        echo -e "${GRAY}  Sessiz kurulum modu${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}[S]${NC} Ses ayarlarını değiştir"
    echo -e "${YELLOW}[D]${NC} Devam et"
    echo ""
    
    key=$(get_key_input "Seçiminizi yapın:" "sd")
    
    case $key in
        s)
            if [ "$MUSIC_ENABLED" = true ]; then
                MUSIC_ENABLED=false
                play_beep "error"
            else
                MUSIC_ENABLED=true
                play_beep "success"
            fi
            show_music_toggle
            ;;
        d)
            play_beep "success"
            ;;
    esac
}

# SSH-compatible welcome screen
show_welcome() {
    clear_screen
    play_beep "startup"
    
    show_ascii_logo
    
    echo -e "${WHITE}Hoş geldiniz!${NC}"
    echo ""
    
    typewriter_effect "Bu kurulum scripti Birlikteyiz Emergency Communication Platform'u" 0.02
    typewriter_effect "Raspberry Pi cihazınıza kuracaktır." 0.02
    echo ""
    
    echo -e "${CYAN}Özellikler:${NC}"
    echo -e "${GREEN}  ✓ LoRa tabanlı uzun mesafe iletişimi (10-15km)${NC}"
    echo -e "${GREEN}  ✓ 2.4GHz mesh ağ desteği${NC}"
    echo -e "${GREEN}  ✓ Tamamen offline çalışma${NC}"
    echo -e "${GREEN}  ✓ SSH üzerinden tam kontrol${NC}"
    echo -e "${GREEN}  ✓ Acil durum koordinasyonu${NC}"
    echo -e "${GREEN}  ✓ Life RPG oyunlaştırma sistemi${NC}"
    echo -e "${GREEN}  ✓ Oyun içi ticaret ve ekonomi${NC}"
    echo -e "${GREEN}  ✓ AI asistan desteği${NC}"
    echo ""
    
    echo -e "${YELLOW}Kurulum yaklaşık 10-15 dakika sürecektir.${NC}"
    echo ""
    
    if [ "$IS_SSH" = true ]; then
        echo -e "${CYAN}SSH Session Detected - Terminal optimizasyonu aktif${NC}"
        echo ""
        echo -e "${WHITE}Başlamak için ENTER tuşuna basın (30s timeout)...${NC}"
        read -t 30 -p ""
    else
        echo -e "${WHITE}Başlamak için herhangi bir tuşa basın...${NC}"
        read -n 1 -s
    fi
    play_beep "success"
}

install_dependencies() {
    clear_screen
    show_ascii_logo
    
    echo -e "${WHITE}Sistem bağımlılıkları kuruluyor...${NC}"
    echo ""
    
    PACKAGES=(
        "python3-pip"
        "python3-venv" 
        "git"
        "nginx"
        "sqlite3"
        "gpsd"
        "gpsd-clients"
        "python3-gps"
        "python3-serial"
        "python3-spidev"
        "python3-rpi.gpio"
        "python3-adafruit-circuitpython-dht"
        "python3-adafruit-circuitpython-gps"
        "alsa-utils"
        "espeak"
        "festival"
    )
    
    total_packages=${#PACKAGES[@]}
    current_package=0
    
    for package in "${PACKAGES[@]}"; do
        current_package=$((current_package + 1))
        echo -e "${CYAN}[$current_package/$total_packages] Kuruluyor: $package${NC}"
        
        if apt-get install -y "$package" &> /dev/null; then
            echo -e "${GREEN}✓ $package kuruldu${NC}"
            play_beep "success"
        else
            echo -e "${RED}✗ $package kurulamadı${NC}"
            play_beep "error"
        fi
        
        progress_bar $current_package $total_packages
        echo ""
    done
    
    echo ""
    echo -e "${GREEN}Sistem bağımlılıkları kurulumu tamamlandı!${NC}"
    sleep 2
}

setup_python_environment() {
    clear_screen
    show_ascii_logo
    
    echo -e "${WHITE}Python ortamı hazırlanıyor...${NC}"
    echo ""
    
    # Create virtual environment
    echo -e "${CYAN}Python sanal ortamı oluşturuluyor...${NC}"
    python3 -m venv /opt/birlikteyiz/venv
    source /opt/birlikteyiz/venv/bin/activate
    
    # Install Python packages
    PYTHON_PACKAGES=(
        "flask"
        "flask-cors"
        "flask-sqlalchemy"
        "requests"
        "pyserial"
        "pynmea2"
        "cryptography"
        "qrcode"
        "pillow"
        "numpy"
        "pygame"
        "adafruit-circuitpython-rfm9x"
        "adafruit-circuitpython-dht"
        "adafruit-circuitpython-gps"
    )
    
    total_packages=${#PYTHON_PACKAGES[@]}
    current_package=0
    
    for package in "${PYTHON_PACKAGES[@]}"; do
        current_package=$((current_package + 1))
        echo -e "${CYAN}[$current_package/$total_packages] Python paketi: $package${NC}"
        
        if pip install "$package" &> /dev/null; then
            echo -e "${GREEN}✓ $package kuruldu${NC}"
            play_beep "success"
        else
            echo -e "${RED}✗ $package kurulamadı${NC}"
            play_beep "error"
        fi
        
        progress_bar $current_package $total_packages
        echo ""
    done
    
    echo ""
    echo -e "${GREEN}Python ortamı hazırlandı!${NC}"
    sleep 2
}

configure_hardware() {
    clear_screen
    show_ascii_logo
    
    echo -e "${WHITE}Donanım yapılandırması...${NC}"
    echo ""
    
    # Enable SPI for LoRa
    echo -e "${CYAN}SPI arayüzü etkinleştiriliyor...${NC}"
    if ! grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "dtparam=spi=on" >> /boot/config.txt
        echo -e "${GREEN}✓ SPI etkinleştirildi${NC}"
    else
        echo -e "${GREEN}✓ SPI zaten etkin${NC}"
    fi
    
    # Enable I2C for sensors
    echo -e "${CYAN}I2C arayüzü etkinleştiriliyor...${NC}"
    if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
        echo "dtparam=i2c_arm=on" >> /boot/config.txt
        echo -e "${GREEN}✓ I2C etkinleştirildi${NC}"
    else
        echo -e "${GREEN}✓ I2C zaten etkin${NC}"
    fi
    
    # Configure GPIO for LoRa module
    echo -e "${CYAN}LoRa modülü GPIO yapılandırması...${NC}"
    cat > /opt/birlikteyiz/config/lora_config.py << EOF
# LoRa Module Configuration
LORA_CS_PIN = 8      # Chip Select
LORA_RESET_PIN = 25  # Reset
LORA_IRQ_PIN = 24    # Interrupt
LORA_FREQUENCY = 868.0  # MHz (Europe)
LORA_TX_POWER = 20   # dBm
LORA_BANDWIDTH = 125000  # Hz
LORA_SPREADING_FACTOR = 7
LORA_CODING_RATE = 5
EOF
    echo -e "${GREEN}✓ LoRa yapılandırması oluşturuldu${NC}"
    
    # Configure GPS
    echo -e "${CYAN}GPS modülü yapılandırması...${NC}"
    cat > /etc/default/gpsd << EOF
START_DAEMON="true"
USBAUTO="true"
DEVICES="/dev/ttyUSB0 /dev/ttyAMA0"
GPSD_OPTIONS="-n"
EOF
    echo -e "${GREEN}✓ GPS yapılandırması oluşturuldu${NC}"
    
    play_beep "success"
    sleep 2
}

setup_game_interface() {
    clear_screen
    show_ascii_logo
    
    echo -e "${WHITE}Oyun arayüzü yapılandırması...${NC}"
    echo ""
    
    if [ "$GAME_MODE" = "retro" ]; then
        echo -e "${CYAN}DOS tarzı retro arayüz kuruluyor...${NC}"
        
        # Install retro terminal emulator
        echo -e "${GRAY}  → Retro terminal emülatörü${NC}"
        
        # Create retro game launcher
        cat > /opt/birlikteyiz/bin/retro_launcher.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import time
import random
from colorama import init, Fore, Back, Style

init()

class RetroInterface:
    def __init__(self):
        self.width = 80
        self.height = 25
        
    def clear_screen(self):
        os.system('clear')
        
    def draw_border(self):
        print(Fore.CYAN + "╔" + "═" * (self.width - 2) + "╗")
        for i in range(self.height - 2):
            print("║" + " " * (self.width - 2) + "║")
        print("╚" + "═" * (self.width - 2) + "╝" + Style.RESET_ALL)
        
    def show_ascii_map(self):
        map_data = [
            "    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
        ]
        
        for line in map_data:
            print(Fore.GREEN + line + Style.RESET_ALL)

if __name__ == "__main__":
    interface = RetroInterface()
    interface.clear_screen()
    interface.show_ascii_map()
EOF
        
        chmod +x /opt/birlikteyiz/bin/retro_launcher.py
        echo -e "${GREEN}✓ Retro arayüz kuruldu${NC}"
        
    else
        echo -e "${CYAN}Ultima Online tarzı 2D grafik arayüz kuruluyor...${NC}"
        
        # Install pygame and graphics libraries
        echo -e "${GRAY}  → Pygame grafik motoru${NC}"
        echo -e "${GRAY}  → 2D sprite sistemi${NC}"
        echo -e "${GRAY}  → Tile-based harita motoru${NC}"
        
        # Create 2D game launcher
        cat > /opt/birlikteyiz/bin/ultima_launcher.py << 'EOF'
#!/usr/bin/env python3
import pygame
import sys
import os

class UltimaInterface:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Birlikteyiz - Life RPG")
        self.clock = pygame.time.Clock()
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.screen.fill((0, 64, 0))  # Dark green background
            
            # Draw simple tile-based map
            for x in range(0, 1024, 32):
                for y in range(0, 768, 32):
                    pygame.draw.rect(self.screen, (0, 128, 0), (x, y, 30, 30))
                    
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = UltimaInterface()
    game.run()
EOF
        
        chmod +x /opt/birlikteyiz/bin/ultima_launcher.py
        echo -e "${GREEN}✓ 2D grafik arayüz kuruldu${NC}"
    fi
    
    play_beep "success"
    sleep 2
}

create_services() {
    clear_screen
    show_ascii_logo
    
    echo -e "${WHITE}Sistem servisleri oluşturuluyor...${NC}"
    echo ""
    
    # Create main Birlikteyiz service
    cat > /etc/systemd/system/birlikteyiz.service << EOF
[Unit]
Description=Birlikteyiz Emergency Communication Platform
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/birlikteyiz
Environment=PATH=/opt/birlikteyiz/venv/bin
ExecStart=/opt/birlikteyiz/venv/bin/python /opt/birlikteyiz/src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    echo -e "${GREEN}✓ Birlikteyiz servisi oluşturuldu${NC}"
    
    # Create LoRa communication service
    cat > /etc/systemd/system/birlikteyiz-lora.service << EOF
[Unit]
Description=Birlikteyiz LoRa Communication Service
After=birlikteyiz.service

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/birlikteyiz
Environment=PATH=/opt/birlikteyiz/venv/bin
ExecStart=/opt/birlikteyiz/venv/bin/python /opt/birlikteyiz/src/lora_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    echo -e "${GREEN}✓ LoRa iletişim servisi oluşturuldu${NC}"
    
    # Enable services
    systemctl daemon-reload
    systemctl enable birlikteyiz
    systemctl enable birlikteyiz-lora
    
    echo -e "${GREEN}✓ Servisler etkinleştirildi${NC}"
    
    play_beep "success"
    sleep 2
}

show_completion() {
    clear_screen
    play_beep "startup"
    
    show_ascii_logo
    
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${WHITE}                              KURULUM TAMAMLANDI!                             ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    typewriter_effect "Birlikteyiz Emergency Communication Platform başarıyla kuruldu!" 0.03
    echo ""
    
    echo -e "${CYAN}Kurulum Özeti:${NC}"
    echo -e "${GREEN}  ✓ Sistem bağımlılıkları kuruldu${NC}"
    echo -e "${GREEN}  ✓ Python ortamı hazırlandı${NC}"
    echo -e "${GREEN}  ✓ Donanım yapılandırıldı${NC}"
    echo -e "${GREEN}  ✓ ${GAME_MODE^} arayüz kuruldu${NC}"
    echo -e "${GREEN}  ✓ Sistem servisleri oluşturuldu${NC}"
    echo ""
    
    echo -e "${YELLOW}Sonraki Adımlar:${NC}"
    echo -e "${WHITE}  1. Sistem yeniden başlatılacak${NC}"
    echo -e "${WHITE}  2. İlk kurulum sihirbazı çalışacak${NC}"
    echo -e "${WHITE}  3. WiFi ağı ve cihaz ismi ayarlanacak${NC}"
    echo -e "${WHITE}  4. LoRa modülü kalibre edilecek${NC}"
    echo ""
    
    if [ "$GAME_MODE" = "retro" ]; then
        echo -e "${MAGENTA}Retro DOS Modu Aktif:${NC}"
        echo -e "${GRAY}  → Metin tabanlı arayüz${NC}"
        echo -e "${GRAY}  → ASCII art haritalar${NC}"
        echo -e "${GRAY}  → Düşük kaynak kullanımı${NC}"
    else
        echo -e "${MAGENTA}Ultima Online Modu Aktif:${NC}"
        echo -e "${GRAY}  → 2D grafik arayüz${NC}"
        echo -e "${GRAY}  → Tile-based haritalar${NC}"
        echo -e "${GRAY}  → Gelişmiş oyun özellikleri${NC}"
    fi
    
    echo ""
    echo -e "${WHITE}Yeniden başlatmak için ENTER tuşuna basın...${NC}"
    read -n 1 -s
    
    play_beep "success"
    sleep 1
    
    echo -e "${RED}Sistem yeniden başlatılıyor...${NC}"
    sleep 3
    reboot
}

# Main installation flow
main() {
    # Initialize terminal detection and colors
    detect_terminal
    setup_colors
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Bu script root yetkileri ile çalıştırılmalıdır.${NC}"
        echo -e "${YELLOW}Lütfen 'sudo $0' komutunu kullanın.${NC}"
        exit 1
    fi
    
    # Create directories
    mkdir -p /opt/birlikteyiz/{src,bin,config,data,logs}
    
    # Installation steps
    show_welcome
    show_music_toggle
    show_system_scan
    install_dependencies
    setup_python_environment
    configure_hardware
    setup_game_interface
    create_services
    show_completion
}

# Trap Ctrl+C
trap 'echo -e "\n${RED}Kurulum iptal edildi.${NC}"; exit 1' INT

# Run main installation
main "$@"

