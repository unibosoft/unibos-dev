#!/bin/bash
#
# UNIBOS Git Remote Setup
# üç ayrı repo için git remote yapılandırması
#

set -e  # exit on error

echo "🔧 unibos git remote yapılandırması"
echo ""

# mevcut remote'ları göster
echo "📋 mevcut remote'lar:"
git remote -v
echo ""

# yeni remote'lar ekle
echo "➕ yeni remote'lar ekleniyor..."

# dev remote (development)
if git remote | grep -q "^dev$"; then
    echo "  ⚠️  'dev' remote zaten mevcut, güncelleniyor..."
    git remote set-url dev https://github.com/unibosoft/unibos-dev.git
else
    echo "  ✅ 'dev' remote ekleniyor..."
    git remote add dev https://github.com/unibosoft/unibos-dev.git
fi

# server remote (production server)
if git remote | grep -q "^server$"; then
    echo "  ⚠️  'server' remote zaten mevcut, güncelleniyor..."
    git remote set-url server https://github.com/unibosoft/unibos-server.git
else
    echo "  ✅ 'server' remote ekleniyor..."
    git remote add server https://github.com/unibosoft/unibos-server.git
fi

# prod remote (production - genel)
if git remote | grep -q "^prod$"; then
    echo "  ✅ 'prod' remote zaten mevcut"
else
    echo "  ✅ 'prod' remote ekleniyor..."
    git remote add prod https://github.com/unibosoft/unibos.git
fi

echo ""

# eski origin'i kaldır (opsiyonel)
if git remote | grep -q "^origin$"; then
    echo "❓ eski 'origin' remote kaldırılsın mı? (evet/hayır)"
    read -r response
    if [[ "$response" =~ ^[Ee]vet$ ]] || [[ "$response" =~ ^[Yy]es$ ]]; then
        git remote remove origin
        echo "  ✅ 'origin' remote kaldırıldı"
    else
        echo "  ⏭️  'origin' remote korundu"
    fi
    echo ""
fi

# güncel remote'ları göster
echo "✅ yeni remote yapılandırması:"
git remote -v
echo ""

# fetch tüm remote'lardan
echo "📥 tüm remote'lardan fetch yapılıyor..."
git fetch --all

echo ""
echo "🎉 git remote kurulumu tamamlandı!"
echo ""
echo "kullanım:"
echo "  git push dev main       # development'a push"
echo "  git push server main    # server'a push"
echo "  git push prod main      # production'a push"
echo ""
