#!/bin/bash
# Recaria GitHub Entegrasyon Scripti
# v047-beta - 2025-06-23
# Unicorn Bodrum Technologies

# Renk kodları
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${BLUE}== Recaria GitHub Entegrasyon Scripti               ==${NC}"
echo -e "${BLUE}== v047-beta                                        ==${NC}"
echo -e "${BLUE}=======================================================${NC}"

# Proje dizini
PROJECT_DIR="/home/ubuntu/unicorn_bodrum_technologies/recaria"
cd $PROJECT_DIR

# Git repo kontrolü
if [ -d ".git" ]; then
    echo -e "${YELLOW}Git deposu zaten mevcut, güncelleniyor...${NC}"
    git pull
else
    echo -e "${YELLOW}Git deposu oluşturuluyor...${NC}"
    git init
    git remote add origin git@github.com:berkhatirli/recaria.git
fi

# Değişiklikleri ekle
echo -e "${YELLOW}Değişiklikler ekleniyor...${NC}"
git add .

# Commit oluştur
echo -e "${YELLOW}Commit oluşturuluyor...${NC}"
git commit -m "Recaria v047-beta güncellemesi - 20250623_2219"

# GitHub'a gönder
echo -e "${YELLOW}GitHub'a gönderiliyor...${NC}"
git push -u origin master

echo -e "${GREEN}GitHub entegrasyonu tamamlandı!${NC}"
