# UNIBOS Git Workflow
üç ayrı git repository yapısı ve kullanımı

## repository yapısı

UNIBOS projesi artık 3 ayrı git repository kullanıyor:

### 1. unibos-dev (development)
- **repo:** `https://github.com/unibosoft/unibos-dev.git`
- **kullanım:** mac geliştirme ortamı
- **cli:** `unibos-dev`
- **amaç:**
  - yeni özellik geliştirme
  - test ve debug
  - deployment yönetimi (dev → server/prod)
  - git ve versiyon kontrolü

### 2. unibos-server (production server)
- **repo:** `https://github.com/unibosoft/unibos-server.git`
- **kullanım:** rocksteady production server
- **cli:** `unibos-server`
- **amaç:**
  - production server deployment
  - merkezi veritabanı (postgresql)
  - node koordinasyonu
  - central api endpoints

### 3. unibos (production)
- **repo:** `https://github.com/unibosoft/unibos.git`
- **kullanım:** genel production release
- **cli:** `unibos` (node cli)
- **amaç:**
  - public production releases
  - standalone node deployment
  - raspberry pi kurulumları
  - p2p mesh networking

## git remote yapılandırması

mevcut development dizininde (`/Users/berkhatirli/Desktop/unibos-dev`):

```bash
# mevcut remote'ları kontrol et
git remote -v

# yeni remote'lar ekle
git remote add dev https://github.com/unibosoft/unibos-dev.git
git remote add server https://github.com/unibosoft/unibos-server.git
git remote add prod https://github.com/unibosoft/unibos.git

# eski origin'i kaldır (opsiyonel)
git remote remove origin
```

## workflow

### development → dev repo
günlük geliştirme için:

```bash
# değişiklikleri commit et
git add .
git commit -m "feat: yeni özellik eklendi"

# dev repo'ya push et
git push dev main
```

### development → server repo
server deployment için:

```bash
# server deployment hazırlığı
# server-specific branch oluştur (opsiyonel)
git checkout -b server-deploy

# server ayarlarını kullan
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.server

# test et
unibos-server health

# server repo'ya push et
git push server main
```

### development → production
production release için:

```bash
# production release hazırlığı
# version tag ekle
git tag -a v0.534.0 -m "v0.534.0 - phoenix release"

# production repo'ya push et
git push prod main --tags
```

## cli entrypoints

her repo'nun kendi cli'ı var:

```bash
# development cli (mac)
unibos-dev              # interactive mode
unibos-dev platform     # platform info
unibos-dev deploy       # deployment management

# server cli (rocksteady)
unibos-server           # interactive mode
unibos-server health    # health check
unibos-server nodes list # list nodes

# node cli (raspberry pi / standalone)
unibos                  # interactive mode
unibos status           # node status
unibos p2p discover     # discover peers
```

## örnek workflow

### yeni özellik geliştirme

1. **geliştirme (mac)**
```bash
cd /Users/berkhatirli/Desktop/unibos-dev

# özellik geliştir
vim core/modules/yeni_modul.py

# test et
unibos-dev

# commit et
git add .
git commit -m "feat: yeni modül eklendi"

# dev repo'ya push et
git push dev main
```

2. **server'a deploy**
```bash
# server'a bağlan ve test et
unibos-dev deploy server

# veya manuel:
git push server main
ssh rocksteady "cd /var/www/unibos && git pull && systemctl restart gunicorn"
```

3. **production release**
```bash
# version bump
./tools/scripts/unibos_version.sh update 0.535.0 "yeni özellik"

# tag oluştur
git tag -a v0.535.0 -m "v0.535.0 - yeni özellik"

# production'a push et
git push prod main --tags
```

## branch stratejisi

### dev repo
- `main` - aktif development
- `feature/*` - yeni özellikler
- `fix/*` - bug fix'ler

### server repo
- `main` - production server kodu
- `hotfix/*` - acil yamalar

### prod repo
- `main` - stable production
- sadece tagged release'ler

## arşiv koruma

⚠️ **önemli:** arşiv dizinlerine asla dokunma!

```bash
# arşiv dizinleri:
archive/versions/       # versiyon arşivleri
archive/database_backups/  # veritabanı yedekleri

# git ignore'a ekli:
.gitignore
.archiveignore
```

## eski repo (archived)

`unibos_dev` repo'su artık kullanılmıyor:
- github'da `unibos_dev_old_20251115` olarak yeniden adlandırıldı
- local'de referans amaçlı tutulabilir
- yeni development için `unibos-dev` kullanılacak

## deployment scriptleri

her deployment tipi için script var:

```bash
# server deployment (python)
python -c "from core.deployment.server import deploy_to_server; deploy_to_server()"

# node setup (python)
python -c "from core.deployment.node import setup_node; setup_node()"

# veya cli üzerinden:
unibos-dev deploy server
unibos-dev setup node
```

## özet

| ne yapıyorsun? | hangi repo? | hangi cli? |
|----------------|-------------|------------|
| özellik geliştiriyorum | unibos-dev | unibos-dev |
| server'a deploy ediyorum | unibos-server | unibos-server |
| production release | unibos | unibos |
| raspberry pi kuruyorum | unibos | unibos |
| p2p test ediyorum | unibos | unibos |
