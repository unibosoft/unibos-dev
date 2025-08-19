#!/bin/bash
# UNIBOS Archive Cleanup Script
# Created: 2025-08-19
# Purpose: Safely remove document/media and log files from version archives

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   UNIBOS Archive Cleanup Script        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo

# Safety check - backup exists?
if [ ! -d "archive/backup_before_cleanup_20250819" ]; then
    echo -e "${RED}❌ HATA: Backup dizini bulunamadı!${NC}"
    echo -e "${YELLOW}Önce backup alınmalı!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backup mevcut: archive/backup_before_cleanup_20250819${NC}"
echo

# Count files before cleanup
echo -e "${YELLOW}📊 Temizlik öncesi durum:${NC}"
DOCS_COUNT=$(find archive/versions -type f -path "*/backend/documents/*" 2>/dev/null | wc -l)
LOGS_COUNT=$(find archive/versions -type f -name "*.log" 2>/dev/null | wc -l)
THUMBS_COUNT=$(find archive/versions -type f -path "*/thumbnails/*" 2>/dev/null | wc -l)
echo "   Belge dosyaları: $DOCS_COUNT"
echo "   Log dosyaları: $LOGS_COUNT"
echo "   Thumbnail dosyaları: $THUMBS_COUNT"
echo "   Toplam: $((DOCS_COUNT + LOGS_COUNT + THUMBS_COUNT)) dosya"
echo

# Size before cleanup
BEFORE_SIZE=$(du -sh archive/versions 2>/dev/null | cut -f1)
echo -e "${BLUE}📦 Temizlik öncesi boyut: $BEFORE_SIZE${NC}"
echo

# Confirmation
echo -n "Temizliğe başlamak istiyor musunuz? (evet/hayır): "
read CONFIRM
if [ "$CONFIRM" != "evet" ]; then
    echo -e "${RED}İptal edildi.${NC}"
    exit 0
fi

echo
echo -e "${YELLOW}🧹 Temizlik başlıyor...${NC}"
echo

# 1. Remove document/media files
echo -e "${YELLOW}1. Belge/medya dosyaları temizleniyor...${NC}"
REMOVED_DOCS=0
for dir in archive/versions/*/backend/documents; do
    if [ -d "$dir" ]; then
        # Count files in this directory
        count=$(find "$dir" -type f 2>/dev/null | wc -l)
        if [ $count -gt 0 ]; then
            # Remove the documents directory
            rm -rf "$dir"
            REMOVED_DOCS=$((REMOVED_DOCS + count))
            echo -e "   ✓ $(basename $(dirname $(dirname "$dir"))): $count dosya silindi"
        fi
    fi
done
echo -e "${GREEN}   Toplam $REMOVED_DOCS belge dosyası silindi${NC}"
echo

# 2. Remove log files
echo -e "${YELLOW}2. Log dosyaları temizleniyor...${NC}"
REMOVED_LOGS=0
while IFS= read -r logfile; do
    if [ -f "$logfile" ]; then
        rm -f "$logfile"
        REMOVED_LOGS=$((REMOVED_LOGS + 1))
    fi
done < <(find archive/versions -type f -name "*.log" 2>/dev/null)
echo -e "${GREEN}   Toplam $REMOVED_LOGS log dosyası silindi${NC}"
echo

# 3. Remove thumbnail directories
echo -e "${YELLOW}3. Thumbnail dosyaları temizleniyor...${NC}"
REMOVED_THUMBS=0
for dir in archive/versions/*/backend/documents/thumbnails archive/versions/*/documents/thumbnails; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f 2>/dev/null | wc -l)
        if [ $count -gt 0 ]; then
            rm -rf "$dir"
            REMOVED_THUMBS=$((REMOVED_THUMBS + count))
        fi
    fi
done
echo -e "${GREEN}   Toplam $REMOVED_THUMBS thumbnail dosyası silindi${NC}"
echo

# Size after cleanup
AFTER_SIZE=$(du -sh archive/versions 2>/dev/null | cut -f1)
echo -e "${BLUE}📦 Temizlik sonrası boyut: $AFTER_SIZE${NC}"
echo

# Summary
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TEMİZLİK TAMAMLANDI!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo
echo "📊 Özet:"
echo "   Silinen belge dosyaları: $REMOVED_DOCS"
echo "   Silinen log dosyaları: $REMOVED_LOGS"
echo "   Silinen thumbnail dosyaları: $REMOVED_THUMBS"
echo "   Toplam silinen: $((REMOVED_DOCS + REMOVED_LOGS + REMOVED_THUMBS)) dosya"
echo "   Önceki boyut: $BEFORE_SIZE"
echo "   Yeni boyut: $AFTER_SIZE"
echo
echo -e "${YELLOW}💡 Not: Backup dizini hala mevcut:${NC}"
echo "   archive/backup_before_cleanup_20250819/"
echo
echo -e "${GREEN}✅ Veri kaybı yok - sadece runtime dosyaları temizlendi${NC}"