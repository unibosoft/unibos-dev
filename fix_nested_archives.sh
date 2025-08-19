#!/bin/bash

# İç İçe Arşiv Anomalisi Güvenli Temizlik Scripti
# Tarih: 2025-08-19
# Amaç: Sadece gereksiz iç içe arşivleri temizle, ana veriler korunsun

echo "🔒 İÇ İÇE ARŞİV ANOMALİSİ TEMİZLİĞİ"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Güvenlik değişkenleri
ARCHIVE_BASE="/Users/berkhatirli/Desktop/unibos/archive"
VERSIONS_DIR="$ARCHIVE_BASE/versions"
CLEANUP_LOG="/tmp/nested_archive_cleanup_$(date +%Y%m%d_%H%M%S).log"
DELETED_COUNT=0
FAILED_COUNT=0

# Başlangıç durumu
echo "📊 BAŞLANGIÇ DURUMU:" | tee -a $CLEANUP_LOG
echo "──────────────────────────────────────────────────────────────" | tee -a $CLEANUP_LOG
BEFORE_VERSION_COUNT=$(ls $VERSIONS_DIR | wc -l | tr -d ' ')
BEFORE_SIZE=$(du -sh $ARCHIVE_BASE | awk '{print $1}')
echo "Versiyon sayısı: $BEFORE_VERSION_COUNT" | tee -a $CLEANUP_LOG
echo "Arşiv boyutu: $BEFORE_SIZE" | tee -a $CLEANUP_LOG
echo "" | tee -a $CLEANUP_LOG

# Temizlenecek klasörleri bul
echo "🔍 Temizlenecek klasörler aranıyor..." | tee -a $CLEANUP_LOG
NESTED_ARCHIVES=$(find $VERSIONS_DIR -type d \( -path "*/projects/archive" -o -path "*/quarantine/projects/archive" \) 2>/dev/null)

if [ -z "$NESTED_ARCHIVES" ]; then
    echo "✅ Temizlenecek iç içe arşiv bulunamadı!" | tee -a $CLEANUP_LOG
    exit 0
fi

TOTAL_TO_CLEAN=$(echo "$NESTED_ARCHIVES" | wc -l | tr -d ' ')
echo "Bulundu: $TOTAL_TO_CLEAN iç içe arşiv" | tee -a $CLEANUP_LOG
echo "" | tee -a $CLEANUP_LOG

# Her birini güvenli şekilde sil
echo "🧹 TEMİZLİK BAŞLIYOR:" | tee -a $CLEANUP_LOG
echo "──────────────────────────────────────────────────────────────" | tee -a $CLEANUP_LOG

while IFS= read -r archive_path; do
    if [ -z "$archive_path" ]; then
        continue
    fi
    
    # Güvenlik kontrolü - sadece projects/archive veya quarantine/projects/archive olmalı
    if [[ "$archive_path" == */projects/archive ]] || [[ "$archive_path" == */quarantine/projects/archive ]]; then
        # Versiyon adını çıkar
        version_name=$(echo "$archive_path" | grep -o "unibos_v[0-9]*_[0-9]*_[0-9]*" | head -1)
        
        # Sil
        if rm -rf "$archive_path" 2>/dev/null; then
            echo "✅ Temizlendi: $version_name/$(echo "$archive_path" | rev | cut -d'/' -f1-2 | rev)" | tee -a $CLEANUP_LOG
            DELETED_COUNT=$((DELETED_COUNT + 1))
        else
            echo "❌ Silinemedi: $archive_path" | tee -a $CLEANUP_LOG
            FAILED_COUNT=$((FAILED_COUNT + 1))
        fi
    else
        echo "⚠️ Atlandı (güvenlik): $archive_path" | tee -a $CLEANUP_LOG
    fi
done <<< "$NESTED_ARCHIVES"

echo "" | tee -a $CLEANUP_LOG

# Sonuç kontrolü
echo "📊 SONUÇ:" | tee -a $CLEANUP_LOG
echo "──────────────────────────────────────────────────────────────" | tee -a $CLEANUP_LOG
AFTER_VERSION_COUNT=$(ls $VERSIONS_DIR | wc -l | tr -d ' ')
AFTER_SIZE=$(du -sh $ARCHIVE_BASE | awk '{print $1}')

echo "Temizlenen: $DELETED_COUNT klasör" | tee -a $CLEANUP_LOG
echo "Başarısız: $FAILED_COUNT klasör" | tee -a $CLEANUP_LOG
echo "" | tee -a $CLEANUP_LOG

echo "VERSİYON KONTROLÜ:" | tee -a $CLEANUP_LOG
echo "  Önceki: $BEFORE_VERSION_COUNT versiyon" | tee -a $CLEANUP_LOG
echo "  Sonraki: $AFTER_VERSION_COUNT versiyon" | tee -a $CLEANUP_LOG

if [ "$BEFORE_VERSION_COUNT" -eq "$AFTER_VERSION_COUNT" ]; then
    echo "  ✅ Tüm versiyonlar korundu!" | tee -a $CLEANUP_LOG
else
    echo "  ⚠️ VERSİYON SAYISI DEĞİŞTİ!" | tee -a $CLEANUP_LOG
fi

echo "" | tee -a $CLEANUP_LOG
echo "BOYUT:" | tee -a $CLEANUP_LOG
echo "  Önceki: $BEFORE_SIZE" | tee -a $CLEANUP_LOG
echo "  Sonraki: $AFTER_SIZE" | tee -a $CLEANUP_LOG

echo "" | tee -a $CLEANUP_LOG
echo "═══════════════════════════════════════════════════════════════" | tee -a $CLEANUP_LOG
echo "✅ TEMİZLİK TAMAMLANDI!" | tee -a $CLEANUP_LOG
echo "Log dosyası: $CLEANUP_LOG" | tee -a $CLEANUP_LOG