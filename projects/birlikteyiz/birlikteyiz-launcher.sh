#!/bin/bash

# Birlikteyiz SSH Game Launcher
# Allows access to DOS-style game interface over SSH

# Colors for SSH terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m'

# Detect terminal and SSH session
detect_environment() {
    TERM_COLS=$(tput cols 2>/dev/null || echo 80)
    TERM_ROWS=$(tput lines 2>/dev/null || echo 24)
    
    if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
        IS_SSH=true
    else
        IS_SSH=false
    fi
    
    # Check if we're running as the pi user
    if [ "$USER" != "pi" ] && [ "$USER" != "root" ]; then
        echo -e "${RED}Warning: Running as user '$USER'. Some features may not work.${NC}"
    fi
}

show_welcome_banner() {
    clear
    
    if [ "$TERM_COLS" -ge 80 ]; then
        echo -e "${CYAN}"
        cat << "EOF"
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                           🐙 BIRLIKTEYIZ LAUNCHER                            ║
    ║                        Emergency Communication Platform                       ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
EOF
        echo -e "${NC}"
    else
        echo -e "${CYAN}╔${'═' * ($TERM_COLS - 2)}╗${NC}"
        echo -e "${CYAN}║${WHITE}$(printf '%*s' $(((TERM_COLS - 12) / 2)) '')BIRLIKTEYIZ$(printf '%*s' $(((TERM_COLS - 12) / 2)) '')${CYAN}║${NC}"
        echo -e "${CYAN}╚${'═' * ($TERM_COLS - 2)}╝${NC}"
    fi
    
    if [ "$IS_SSH" = true ]; then
        echo -e "${GRAY}SSH Session Active | Terminal: ${TERM_COLS}x${TERM_ROWS}${NC}"
    fi
    echo ""
}

check_system_status() {
    echo -e "${YELLOW}Checking system status...${NC}"
    
    # Check if Birlikteyiz service is running
    if systemctl is-active --quiet birlikteyiz; then
        echo -e "${GREEN}✓ Birlikteyiz service: RUNNING${NC}"
    else
        echo -e "${RED}✗ Birlikteyiz service: STOPPED${NC}"
        echo -e "${YELLOW}  Starting service...${NC}"
        sudo systemctl start birlikteyiz
    fi
    
    # Check LoRa service
    if systemctl is-active --quiet birlikteyiz-lora; then
        echo -e "${GREEN}✓ LoRa communication: ACTIVE${NC}"
    else
        echo -e "${YELLOW}⚠ LoRa communication: INACTIVE${NC}"
    fi
    
    # Check network connectivity
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo -e "${GREEN}✓ Internet connection: AVAILABLE${NC}"
    else
        echo -e "${YELLOW}⚠ Internet connection: OFFLINE (Local mode)${NC}"
    fi
    
    # Check device type
    if grep -q "Raspberry Pi Zero 2" /proc/cpuinfo; then
        DEVICE_TYPE="Pi Zero 2W"
        GAME_MODE="retro"
        echo -e "${GREEN}✓ Device: ${DEVICE_TYPE} (DOS Mode)${NC}"
    elif grep -q "Raspberry Pi 5" /proc/cpuinfo; then
        DEVICE_TYPE="Pi 5"
        GAME_MODE="ultima"
        echo -e "${GREEN}✓ Device: ${DEVICE_TYPE} (Enhanced Mode)${NC}"
    else
        DEVICE_TYPE="Unknown"
        GAME_MODE="retro"
        echo -e "${YELLOW}⚠ Device: ${DEVICE_TYPE} (Fallback Mode)${NC}"
    fi
    
    echo ""
}

show_main_menu() {
    echo -e "${WHITE}═══ MAIN LAUNCHER MENU ═══${NC}"
    echo -e "${CYAN}[1]${NC} Start Game Interface (${GAME_MODE} mode)"
    echo -e "${CYAN}[2]${NC} Emergency Communications"
    echo -e "${CYAN}[3]${NC} System Dashboard"
    echo -e "${CYAN}[4]${NC} Network Status"
    echo -e "${CYAN}[5]${NC} System Settings"
    echo -e "${CYAN}[6]${NC} View Logs"
    echo -e "${CYAN}[7]${NC} Update System"
    echo -e "${CYAN}[Q]${NC} Quit"
    echo ""
    echo -e "${YELLOW}Select option [1-7, Q]: ${NC}"
}

start_game_interface() {
    echo -e "${GREEN}Starting game interface...${NC}"
    
    if [ "$GAME_MODE" = "retro" ]; then
        echo -e "${CYAN}Loading DOS-style interface...${NC}"
        sleep 1
        
        # Check if Python game exists
        if [ -f "/opt/birlikteyiz/src/static/dos_game.py" ]; then
            cd /opt/birlikteyiz
            python3 src/static/dos_game.py
        else
            echo -e "${RED}Game interface not found. Please reinstall Birlikteyiz.${NC}"
            read -p "Press Enter to continue..."
        fi
    else
        echo -e "${CYAN}Loading Enhanced 2D interface...${NC}"
        sleep 1
        
        # For Pi 5, we would start the Pygame interface
        echo -e "${YELLOW}Enhanced mode not yet implemented. Starting DOS mode...${NC}"
        if [ -f "/opt/birlikteyiz/src/static/dos_game.py" ]; then
            cd /opt/birlikteyiz
            python3 src/static/dos_game.py
        else
            echo -e "${RED}Game interface not found.${NC}"
            read -p "Press Enter to continue..."
        fi
    fi
}

show_emergency_comms() {
    clear
    show_welcome_banner
    
    echo -e "${RED}═══ EMERGENCY COMMUNICATIONS ═══${NC}"
    echo ""
    
    echo -e "${WHITE}Quick Actions:${NC}"
    echo -e "${RED}[S]${NC} Send SOS Signal"
    echo -e "${YELLOW}[B]${NC} Broadcast Message"
    echo -e "${GREEN}[C]${NC} Check Messages"
    echo -e "${BLUE}[N]${NC} Network Scan"
    echo -e "${GRAY}[M]${NC} Main Menu"
    echo ""
    
    # Show emergency status
    echo -e "${YELLOW}Emergency Status:${NC}"
    echo -e "${GRAY}• No active emergencies${NC}"
    echo -e "${GRAY}• 3 devices in range${NC}"
    echo -e "${GRAY}• Last contact: 5 minutes ago${NC}"
    echo ""
    
    read -n 1 -p "Select action: " choice
    echo ""
    
    case $choice in
        [Ss])
            send_sos_signal
            ;;
        [Bb])
            broadcast_message
            ;;
        [Cc])
            check_messages
            ;;
        [Nn])
            network_scan
            ;;
        [Mm])
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            sleep 1
            show_emergency_comms
            ;;
    esac
}

send_sos_signal() {
    echo ""
    echo -e "${RED}═══ SOS SIGNAL ═══${NC}"
    echo -e "${YELLOW}This will send an emergency signal to all nearby devices.${NC}"
    echo ""
    read -p "Are you sure? [y/N]: " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${RED}Sending SOS signal...${NC}"
        
        # Simulate SOS sending
        for i in {1..5}; do
            echo -n "."
            sleep 0.5
        done
        echo ""
        
        echo -e "${GREEN}SOS signal sent successfully!${NC}"
        echo -e "${GRAY}Signal broadcasted to all devices in range.${NC}"
    else
        echo -e "${GRAY}SOS cancelled.${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
    show_emergency_comms
}

broadcast_message() {
    echo ""
    echo -e "${YELLOW}═══ BROADCAST MESSAGE ═══${NC}"
    echo ""
    read -p "Enter message: " message
    
    if [ -n "$message" ]; then
        echo -e "${GREEN}Broadcasting message...${NC}"
        echo -e "${GRAY}Message: \"$message\"${NC}"
        
        # Simulate message sending
        sleep 2
        echo -e "${GREEN}Message sent to all devices in range.${NC}"
    else
        echo -e "${RED}No message entered.${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
    show_emergency_comms
}

check_messages() {
    echo ""
    echo -e "${GREEN}═══ RECENT MESSAGES ═══${NC}"
    echo ""
    
    # Simulate message list
    echo -e "${GRAY}[15:30] dolphin: System test - all OK${NC}"
    echo -e "${GRAY}[15:25] eagle: Weather update - storm approaching${NC}"
    echo -e "${GRAY}[15:20] mountain: Low battery warning${NC}"
    echo -e "${GRAY}[15:15] System: Network scan complete${NC}"
    echo ""
    
    read -p "Press Enter to continue..."
    show_emergency_comms
}

network_scan() {
    echo ""
    echo -e "${BLUE}═══ NETWORK SCAN ═══${NC}"
    echo -e "${YELLOW}Scanning for nearby devices...${NC}"
    
    # Simulate network scan
    for i in {1..10}; do
        echo -n "."
        sleep 0.3
    done
    echo ""
    echo ""
    
    echo -e "${GREEN}Devices found:${NC}"
    echo -e "${WHITE}• dolphin${NC} - Pi Zero 2W - 2.3km - Signal: -52dBm"
    echo -e "${WHITE}• eagle${NC} - Pi 5 - 5.1km - Signal: -68dBm"
    echo -e "${GRAY}• mountain${NC} - Pi Zero 2W - Offline (last seen: 2h ago)"
    echo ""
    
    read -p "Press Enter to continue..."
    show_emergency_comms
}

show_system_dashboard() {
    clear
    show_welcome_banner
    
    echo -e "${WHITE}═══ SYSTEM DASHBOARD ═══${NC}"
    echo ""
    
    # System information
    echo -e "${CYAN}System Information:${NC}"
    echo -e "${GRAY}• Uptime: $(uptime -p)${NC}"
    echo -e "${GRAY}• CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%${NC}"
    echo -e "${GRAY}• Memory: $(free -h | awk 'NR==2{printf "%.1f/%.1fGB (%.0f%%)", $3/1024/1024, $2/1024/1024, $3*100/$2}')${NC}"
    echo -e "${GRAY}• Disk: $(df -h / | awk 'NR==2{printf "%s/%s (%s)", $3, $2, $5}')${NC}"
    echo -e "${GRAY}• Temperature: $(vcgencmd measure_temp 2>/dev/null | cut -d'=' -f2 || echo 'N/A')${NC}"
    echo ""
    
    # Network status
    echo -e "${CYAN}Network Status:${NC}"
    echo -e "${GRAY}• WiFi: $(iwgetid -r 2>/dev/null || echo 'Not connected')${NC}"
    echo -e "${GRAY}• IP Address: $(hostname -I | awk '{print $1}')${NC}"
    echo -e "${GRAY}• LoRa: $(systemctl is-active birlikteyiz-lora)${NC}"
    echo ""
    
    read -p "Press Enter to continue..."
}

show_network_status() {
    clear
    show_welcome_banner
    
    echo -e "${WHITE}═══ NETWORK STATUS ═══${NC}"
    echo ""
    
    echo -e "${CYAN}LoRa Network:${NC}"
    echo -e "${GREEN}• Status: ACTIVE${NC}"
    echo -e "${GRAY}• Frequency: 868.0 MHz${NC}"
    echo -e "${GRAY}• Power: 20 dBm${NC}"
    echo -e "${GRAY}• Range: ~10-15 km${NC}"
    echo ""
    
    echo -e "${CYAN}WiFi Network:${NC}"
    if iwgetid -r &>/dev/null; then
        echo -e "${GREEN}• Status: CONNECTED${NC}"
        echo -e "${GRAY}• SSID: $(iwgetid -r)${NC}"
        echo -e "${GRAY}• Signal: $(iwconfig wlan0 2>/dev/null | grep "Signal level" | awk '{print $4}' | cut -d'=' -f2 || echo 'N/A')${NC}"
    else
        echo -e "${YELLOW}• Status: DISCONNECTED${NC}"
    fi
    echo ""
    
    echo -e "${CYAN}Mesh Network:${NC}"
    echo -e "${GREEN}• Active Nodes: 3${NC}"
    echo -e "${GRAY}• Total Range: ~25 km${NC}"
    echo -e "${GRAY}• Last Update: $(date '+%H:%M:%S')${NC}"
    echo ""
    
    read -p "Press Enter to continue..."
}

show_system_settings() {
    clear
    show_welcome_banner
    
    echo -e "${WHITE}═══ SYSTEM SETTINGS ═══${NC}"
    echo ""
    
    echo -e "${CYAN}[1]${NC} Change Device Name"
    echo -e "${CYAN}[2]${NC} WiFi Configuration"
    echo -e "${CYAN}[3]${NC} LoRa Settings"
    echo -e "${CYAN}[4]${NC} Emergency Contacts"
    echo -e "${CYAN}[5]${NC} System Update"
    echo -e "${CYAN}[6]${NC} Factory Reset"
    echo -e "${CYAN}[M]${NC} Main Menu"
    echo ""
    
    read -n 1 -p "Select option: " choice
    echo ""
    
    case $choice in
        1)
            change_device_name
            ;;
        2)
            configure_wifi
            ;;
        3)
            configure_lora
            ;;
        4)
            configure_emergency_contacts
            ;;
        5)
            system_update
            ;;
        6)
            factory_reset
            ;;
        [Mm])
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            sleep 1
            show_system_settings
            ;;
    esac
}

change_device_name() {
    echo ""
    echo -e "${YELLOW}═══ CHANGE DEVICE NAME ═══${NC}"
    echo ""
    
    current_name=$(hostname)
    echo -e "${GRAY}Current name: $current_name${NC}"
    echo ""
    
    read -p "Enter new device name: " new_name
    
    if [ -n "$new_name" ] && [[ "$new_name" =~ ^[a-zA-Z0-9]+$ ]]; then
        echo -e "${YELLOW}Changing device name to: $new_name${NC}"
        
        # This would require root privileges
        if [ "$EUID" -eq 0 ]; then
            hostnamectl set-hostname "$new_name"
            echo -e "${GREEN}Device name changed successfully!${NC}"
            echo -e "${YELLOW}Reboot required for full effect.${NC}"
        else
            echo -e "${RED}Root privileges required to change hostname.${NC}"
            echo -e "${YELLOW}Run: sudo hostnamectl set-hostname $new_name${NC}"
        fi
    else
        echo -e "${RED}Invalid name. Use only letters and numbers.${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
    show_system_settings
}

configure_wifi() {
    echo ""
    echo -e "${YELLOW}═══ WiFi CONFIGURATION ═══${NC}"
    echo ""
    
    echo -e "${GRAY}Current WiFi status:${NC}"
    if iwgetid -r &>/dev/null; then
        echo -e "${GREEN}Connected to: $(iwgetid -r)${NC}"
    else
        echo -e "${YELLOW}Not connected${NC}"
    fi
    echo ""
    
    echo -e "${CYAN}[1]${NC} Scan for networks"
    echo -e "${CYAN}[2]${NC} Connect to network"
    echo -e "${CYAN}[3]${NC} Disconnect"
    echo -e "${CYAN}[B]${NC} Back"
    echo ""
    
    read -n 1 -p "Select option: " choice
    echo ""
    
    case $choice in
        1)
            echo -e "${YELLOW}Scanning for WiFi networks...${NC}"
            iwlist wlan0 scan 2>/dev/null | grep ESSID | cut -d'"' -f2 | head -10
            ;;
        2)
            read -p "Enter SSID: " ssid
            read -s -p "Enter password: " password
            echo ""
            echo -e "${YELLOW}Connecting to $ssid...${NC}"
            # This would require proper WiFi configuration
            echo -e "${GRAY}Use raspi-config or nmcli for WiFi setup${NC}"
            ;;
        3)
            echo -e "${YELLOW}Disconnecting from WiFi...${NC}"
            sudo ifdown wlan0 2>/dev/null || echo "Already disconnected"
            ;;
        [Bb])
            show_system_settings
            return
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    configure_wifi
}

view_logs() {
    clear
    show_welcome_banner
    
    echo -e "${WHITE}═══ SYSTEM LOGS ═══${NC}"
    echo ""
    
    echo -e "${CYAN}[1]${NC} Birlikteyiz Service Logs"
    echo -e "${CYAN}[2]${NC} LoRa Communication Logs"
    echo -e "${CYAN}[3]${NC} System Logs"
    echo -e "${CYAN}[4]${NC} Emergency Logs"
    echo -e "${CYAN}[M]${NC} Main Menu"
    echo ""
    
    read -n 1 -p "Select log type: " choice
    echo ""
    
    case $choice in
        1)
            echo -e "${YELLOW}Birlikteyiz Service Logs (last 20 lines):${NC}"
            journalctl -u birlikteyiz -n 20 --no-pager
            ;;
        2)
            echo -e "${YELLOW}LoRa Communication Logs:${NC}"
            journalctl -u birlikteyiz-lora -n 20 --no-pager
            ;;
        3)
            echo -e "${YELLOW}System Logs (last 20 lines):${NC}"
            journalctl -n 20 --no-pager
            ;;
        4)
            echo -e "${YELLOW}Emergency Logs:${NC}"
            if [ -f "/opt/birlikteyiz/logs/emergency.log" ]; then
                tail -20 /opt/birlikteyiz/logs/emergency.log
            else
                echo -e "${GRAY}No emergency logs found${NC}"
            fi
            ;;
        [Mm])
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            sleep 1
            view_logs
            return
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

update_system() {
    echo ""
    echo -e "${YELLOW}═══ SYSTEM UPDATE ═══${NC}"
    echo ""
    
    echo -e "${YELLOW}This will update Birlikteyiz to the latest version.${NC}"
    echo -e "${RED}Warning: This may take several minutes.${NC}"
    echo ""
    
    read -p "Continue with update? [y/N]: " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Starting system update...${NC}"
        
        # Simulate update process
        echo -e "${CYAN}Checking for updates...${NC}"
        sleep 2
        
        echo -e "${CYAN}Downloading updates...${NC}"
        for i in {1..20}; do
            echo -n "."
            sleep 0.2
        done
        echo ""
        
        echo -e "${CYAN}Installing updates...${NC}"
        sleep 3
        
        echo -e "${GREEN}Update completed successfully!${NC}"
        echo -e "${YELLOW}Restart recommended.${NC}"
    else
        echo -e "${GRAY}Update cancelled.${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

# Main program loop
main() {
    detect_environment
    
    while true; do
        show_welcome_banner
        check_system_status
        show_main_menu
        
        read -n 1 choice
        echo ""
        
        case $choice in
            1)
                start_game_interface
                ;;
            2)
                show_emergency_comms
                ;;
            3)
                show_system_dashboard
                ;;
            4)
                show_network_status
                ;;
            5)
                show_system_settings
                ;;
            6)
                view_logs
                ;;
            7)
                update_system
                ;;
            [Qq])
                echo -e "${GREEN}Goodbye! Emergency systems remain active.${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please try again.${NC}"
                sleep 1
                ;;
        esac
    done
}

# Run the launcher
main "$@"

