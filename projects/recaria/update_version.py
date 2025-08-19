#!/usr/bin/env python3
"""
Recaria v047-beta Versiyon Güncelleme ve GitHub Entegrasyon Scripti
Unicorn Bodrum Technologies

Bu script, Recaria projesinin versiyon bilgilerini günceller ve GitHub'a gönderir.
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime

# Sabit değişkenler
VERSION = "v047-beta"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")
PROJECT_ROOT = "/home/ubuntu/unicorn_bodrum_technologies/recaria"
GITHUB_REPO = "git@github.com:berkhatirli/recaria.git"  # GitHub repo URL'sini buraya girin
COMMIT_MESSAGE = f"Recaria {VERSION} güncellemesi - {TIMESTAMP}"

# Renk kodları
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
ENDC = "\033[0m"

def print_header(text):
    """Başlık yazdır"""
    print(f"\n{BLUE}{'=' * 60}{ENDC}")
    print(f"{BLUE}== {text}{ENDC}")
    print(f"{BLUE}{'=' * 60}{ENDC}\n")

def print_success(text):
    """Başarı mesajı yazdır"""
    print(f"{GREEN}✓ {text}{ENDC}")

def print_warning(text):
    """Uyarı mesajı yazdır"""
    print(f"{YELLOW}⚠ {text}{ENDC}")

def print_error(text):
    """Hata mesajı yazdır"""
    print(f"{RED}✗ {text}{ENDC}")

def update_version_in_files():
    """Dosyalardaki versiyon bilgilerini güncelle"""
    print_header("Versiyon Bilgilerini Güncelleme")
    
    # settings.py dosyasını güncelle
    settings_file = os.path.join(PROJECT_ROOT, "recaria", "recaria_backend", "settings.py")
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Versiyon bilgisini güncelle
        content = content.replace("v046-beta", VERSION)
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print_success(f"settings.py dosyası güncellendi: {settings_file}")
    else:
        print_warning(f"settings.py dosyası bulunamadı: {settings_file}")
    
    # README.md dosyasını güncelle
    readme_file = os.path.join(PROJECT_ROOT, "README.md")
    if os.path.exists(readme_file):
        with open(readme_file, 'r') as f:
            content = f.read()
        
        # Versiyon bilgisini güncelle
        content = content.replace("v046-beta", VERSION)
        
        with open(readme_file, 'w') as f:
            f.write(content)
        
        print_success(f"README.md dosyası güncellendi: {readme_file}")
    else:
        print_warning(f"README.md dosyası bulunamadı: {readme_file}")
    
    # index.html dosyasını güncelle
    index_file = os.path.join(PROJECT_ROOT, "templates", "index.html")
    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            content = f.read()
        
        # Versiyon bilgisini güncelle
        content = content.replace("v046-beta", VERSION)
        
        with open(index_file, 'w') as f:
            f.write(content)
        
        print_success(f"index.html dosyası güncellendi: {index_file}")
    else:
        print_warning(f"index.html dosyası bulunamadı: {index_file}")
    
    # start_recaria.sh dosyasını güncelle
    start_script = os.path.join(PROJECT_ROOT, "start_recaria.sh")
    if os.path.exists(start_script):
        with open(start_script, 'r') as f:
            content = f.read()
        
        # Versiyon bilgisini güncelle
        content = content.replace("v046-beta", VERSION)
        
        with open(start_script, 'w') as f:
            f.write(content)
        
        print_success(f"start_recaria.sh dosyası güncellendi: {start_script}")
    else:
        print_warning(f"start_recaria.sh dosyası bulunamadı: {start_script}")
    
    # api.py dosyasını güncelle
    api_file = os.path.join(PROJECT_ROOT, "backend", "api.py")
    if os.path.exists(api_file):
        with open(api_file, 'r') as f:
            content = f.read()
        
        # Versiyon bilgisini güncelle
        content = content.replace("v046-beta", VERSION)
        content = content.replace("recaria/0.46-beta", f"recaria/{VERSION}")
        
        with open(api_file, 'w') as f:
            f.write(content)
        
        print_success(f"api.py dosyası güncellendi: {api_file}")
    else:
        print_warning(f"api.py dosyası bulunamadı: {api_file}")
    
    # Diğer dosyalardaki 'unicorn_bodrum' referanslarını temizle
    print_header("'unicorn_bodrum' Referanslarını Temizleme")
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(('.py', '.js', '.html', '.md', '.sh')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # 'unicorn_bodrum' referanslarını değiştir
                    if 'unicorn_bodrum' in content.lower():
                        content = content.replace('unicorn_bodrum_technologies/recaria', 'unicorn_bodrum_technologies/recaria')
                        content = content.replace('Recaria', 'Recaria')
                        content = content.replace('Recaria', 'Recaria')
                        content = content.replace('Unicorn Bodrum Entertainment', 'Unicorn Bodrum Entertainment')
                        content = content.replace('unicorn_bodrum', 'unicorn_bodrum')
                        
                        with open(file_path, 'w') as f:
                            f.write(content)
                        
                        print_success(f"'unicorn_bodrum' referansları temizlendi: {file_path}")
                except Exception as e:
                    print_warning(f"Dosya işlenirken hata: {file_path} - {str(e)}")

def create_version_file():
    """Versiyon bilgi dosyası oluştur"""
    print_header("Versiyon Bilgi Dosyası Oluşturma")
    
    version_info = {
        "version": VERSION,
        "build_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "build_timestamp": TIMESTAMP,
        "developer": "Unicorn Bodrum Technologies",
        "copyright": f"© {datetime.now().year} Unicorn Bodrum Teknoloji ve Perakende Limited Şirketi"
    }
    
    version_file = os.path.join(PROJECT_ROOT, "VERSION.json")
    with open(version_file, 'w') as f:
        json.dump(version_info, f, indent=2)
    
    print_success(f"Versiyon bilgi dosyası oluşturuldu: {version_file}")

def create_changelog_entry():
    """CHANGELOG.md dosyasına yeni giriş ekle"""
    print_header("CHANGELOG Güncellemesi")
    
    changelog_file = os.path.join(PROJECT_ROOT, "CHANGELOG.md")
    
    # Eğer dosya yoksa oluştur
    if not os.path.exists(changelog_file):
        with open(changelog_file, 'w') as f:
            f.write("# Recaria Değişiklik Günlüğü\n\n")
    
    # Yeni değişiklik girişi
    entry = f"""
## {VERSION} - {datetime.now().strftime("%Y-%m-%d")}

### Eklenenler
- Unicorn Bodrum Technologies yapısına geçiş
- Şirket ve alt marka referansları güncellendi
- Kullanıcı ve alt tedarikçi sözleşmeleri eklendi
- GitHub entegrasyonu eklendi

### Değişiklikler
- Proje dizin yapısı güncellendi
- Tüm 'unicorn_bodrum' referansları kaldırıldı
- Versiyon bilgileri güncellendi

### Düzeltmeler
- Sidebar ve tam ekran harita arayüzü iyileştirildi
- Rocksteady sunucu entegrasyonu güçlendirildi
- Nginx ve Gunicorn yapılandırmaları optimize edildi

"""
    
    # Dosyanın başına ekle
    with open(changelog_file, 'r') as f:
        content = f.read()
    
    with open(changelog_file, 'w') as f:
        # İlk başlığı bul ve ondan sonra ekle
        if "# Recaria Değişiklik Günlüğü" in content:
            content = content.replace("# Recaria Değişiklik Günlüğü", "# Recaria Değişiklik Günlüğü" + entry)
        else:
            content = "# Recaria Değişiklik Günlüğü\n" + entry + content
        
        f.write(content)
    
    print_success(f"CHANGELOG.md dosyası güncellendi: {changelog_file}")

def create_github_script():
    """GitHub'a gönderme scripti oluştur"""
    print_header("GitHub Entegrasyon Scripti Oluşturma")
    
    script_content = f"""#!/bin/bash
# Recaria GitHub Entegrasyon Scripti
# {VERSION} - {datetime.now().strftime("%Y-%m-%d")}
# Unicorn Bodrum Technologies

# Renk kodları
GREEN="\\033[0;32m"
YELLOW="\\033[0;33m"
RED="\\033[0;31m"
BLUE="\\033[0;34m"
NC="\\033[0m" # No Color

echo -e "${{BLUE}}=======================================================${{NC}}"
echo -e "${{BLUE}}== Recaria GitHub Entegrasyon Scripti               ==${{NC}}"
echo -e "${{BLUE}}== {VERSION}                                        ==${{NC}}"
echo -e "${{BLUE}}=======================================================${{NC}}"

# Proje dizini
PROJECT_DIR="{PROJECT_ROOT}"
cd $PROJECT_DIR

# Git repo kontrolü
if [ -d ".git" ]; then
    echo -e "${{YELLOW}}Git deposu zaten mevcut, güncelleniyor...${{NC}}"
    git pull
else
    echo -e "${{YELLOW}}Git deposu oluşturuluyor...${{NC}}"
    git init
    git remote add origin {GITHUB_REPO}
fi

# Değişiklikleri ekle
echo -e "${{YELLOW}}Değişiklikler ekleniyor...${{NC}}"
git add .

# Commit oluştur
echo -e "${{YELLOW}}Commit oluşturuluyor...${{NC}}"
git commit -m "{COMMIT_MESSAGE}"

# GitHub'a gönder
echo -e "${{YELLOW}}GitHub'a gönderiliyor...${{NC}}"
git push -u origin master

echo -e "${{GREEN}}GitHub entegrasyonu tamamlandı!${{NC}}"
"""
    
    script_file = os.path.join(PROJECT_ROOT, "github_push.sh")
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Çalıştırma izni ver
    os.chmod(script_file, 0o755)
    
    print_success(f"GitHub entegrasyon scripti oluşturuldu: {script_file}")

def create_zip_package():
    """ZIP paketi oluştur"""
    print_header("ZIP Paketi Oluşturma")
    
    zip_file = f"/home/ubuntu/recaria_{VERSION}_{TIMESTAMP}.zip"
    
    try:
        shutil.make_archive(
            zip_file.replace('.zip', ''),
            'zip',
            '/home/ubuntu/unicorn_bodrum_technologies'
        )
        print_success(f"ZIP paketi oluşturuldu: {zip_file}")
        return zip_file
    except Exception as e:
        print_error(f"ZIP paketi oluşturulurken hata: {str(e)}")
        return None

def main():
    """Ana fonksiyon"""
    print_header(f"Recaria {VERSION} Güncelleme ve GitHub Entegrasyon Scripti")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Versiyon bilgilerini güncelle
    update_version_in_files()
    
    # Versiyon bilgi dosyası oluştur
    create_version_file()
    
    # CHANGELOG güncellemesi
    create_changelog_entry()
    
    # GitHub scripti oluştur
    create_github_script()
    
    # ZIP paketi oluştur
    zip_file = create_zip_package()
    
    print_header("Sonuç")
    print_success(f"Recaria {VERSION} güncellemesi tamamlandı!")
    
    if zip_file:
        print_success(f"ZIP paketi: {zip_file}")
    
    print_success(f"GitHub entegrasyon scripti: {os.path.join(PROJECT_ROOT, 'github_push.sh')}")
    print_success(f"GitHub'a göndermek için: cd {PROJECT_ROOT} && ./github_push.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
