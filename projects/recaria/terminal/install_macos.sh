#!/bin/bash
# recaria macOS Kurulum Scripti
# "ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria!"

echo "🥕 recaria v003 - macOS Kurulum Scripti"
echo "💫 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria!"
echo

# Platform kontrolü
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Bu script sadece macOS için tasarlanmıştır!"
    exit 1
fi

# Architecture detection
ARCH=$(uname -m)
echo "🔍 Platform: macOS $ARCH"

# Homebrew kontrolü
if ! command -v brew &> /dev/null; then
    echo "📦 Homebrew bulunamadı, kuruluyor..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Apple Silicon için path ayarı
    if [[ "$ARCH" == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew mevcut"
fi

# Python3 kontrolü
if ! command -v python3 &> /dev/null; then
    echo "🐍 Python3 kuruluyor..."
    brew install python3
else
    echo "✅ Python3 mevcut: $(python3 --version)"
fi

# Pip kontrolü
if ! command -v pip3 &> /dev/null; then
    echo "📦 pip3 kuruluyor..."
    python3 -m ensurepip --upgrade
else
    echo "✅ pip3 mevcut"
fi

# Gerekli Python kütüphaneleri
echo "📚 Python kütüphaneleri kuruluyor..."
pip3 install --user requests

# Kurulum dizini oluştur
INSTALL_DIR="$HOME/.recaria"
mkdir -p "$INSTALL_DIR"

# recaria binary'sini kopyala
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
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bash_profile"
fi

if [[ -n "$SHELL_RC" ]]; then
    if ! grep -q "/.recaria" "$SHELL_RC" 2>/dev/null; then
        echo "🔧 PATH'e recaria ekleniyor..."
        echo 'export PATH="$HOME/.recaria:$PATH"' >> "$SHELL_RC"
        echo "⚠️  Yeni terminal açın veya 'source $SHELL_RC' çalıştırın"
    fi
fi

# Desktop shortcut oluştur (opsiyonel)
DESKTOP_DIR="$HOME/Desktop"
if [[ -d "$DESKTOP_DIR" ]]; then
    cat > "$DESKTOP_DIR/recaria.command" << EOF
#!/bin/bash
cd "\$HOME/.recaria"
python3 recaria_terminal.py
EOF
    chmod +x "$DESKTOP_DIR/recaria.command"
    echo "🖥️  Desktop kısayolu oluşturuldu"
fi

# Terminal.app için özel ayarlar
if [[ "$TERM_PROGRAM" == "Apple_Terminal" ]]; then
    echo "🍎 Apple Terminal için optimizasyonlar uygulanıyor..."
    # UTF-8 desteği
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8
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

