# UNIBOS .gitignore stratejisi
3 ayrı repository için özel ignore dosyaları

## genel bakış

unibos projesi artık 3 ayrı git repository kullanıyor:

1. **unibos-dev** - development environment (mac)
2. **unibos-server** - production server (rocksteady)
3. **unibos** - production nodes (raspberry pi/mac)

her repo'nun kendi özel `.gitignore` dosyası var.

## ignore dosyaları

### ana dizinde 3 adet ignore dosyası:

```
.gitignore          # aktif ignore (şu an dev için)
.gitignore.dev      # development repo için
.gitignore.server   # server repo için
.gitignore.prod     # production nodes için
```

### yedekler:

eski ignore dosyaları `archive/ignore_files_backup_20251115/` dizininde yedeklendi:
- `gitignore_old.txt`
- `prodignore_old.txt`
- `rsyncignore_old.txt`
- `archiveignore_old.txt`

## repo bazında farklar

### 1. unibos-dev (development)

**dahil:**
- ✅ tüm cli'lar (cli_dev, cli_server, cli_node)
- ✅ tüm settings (development, server, node, base)
- ✅ tüm deployment scripts
- ✅ tüm modüller
- ✅ tüm dökümanlar

**hariç:**
- ❌ `archive/` - **KRİTİK** (sadece local)
- ❌ `data/` - runtime data
- ❌ `build/`, `dist/` - build artifacts
- ❌ `venv/` - python environment
- ❌ `.env` - secrets
- ❌ database files
- ❌ logs

**kullanım:**
```bash
# dev repo için gitignore aktifleştir
cp .gitignore.dev .gitignore
git add .
git commit -m "feat: development changes"
git push dev main
```

### 2. unibos-server (rocksteady production)

**dahil:**
- ✅ `cli_server/` - server management
- ✅ `cli_node/` - server bazen node gibi çalışabilir
- ✅ `settings/server.py`, `settings/node.py`, `settings/base.py`
- ✅ `deployment/server.py`, `deployment/node.py`
- ✅ tüm modüller

**hariç:**
- ❌ `cli_dev/` - **GÜVENLİK** (dev tools server'da olmamalı)
- ❌ `archive/` - production'da arşiv yok
- ❌ `data/` - runtime data server'da ayrı yönetilir
- ❌ `build/`, `dist/` - build artifacts
- ❌ dev-only docs (TODO.md, RULES.md)
- ❌ .claude/, screenshots
- ❌ dev settings (development.py, dev_*.py)

**kullanım:**
```bash
# server repo için gitignore aktifleştir
cp .gitignore.server .gitignore
git add .
git commit -m "feat: server deployment"
git push server main
```

### 3. unibos (production nodes)

**dahil:**
- ✅ `cli_node/` **SADECE** - node management
- ✅ `settings/node.py`, `settings/base.py`
- ✅ `deployment/node.py`
- ✅ tüm modüller (p2p için)

**hariç:**
- ❌ `cli_dev/` - **GÜVENLİK**
- ❌ `cli_server/` - **GÜVENLİK** (node'larda server cli yok)
- ❌ `archive/` - production'da arşiv yok
- ❌ `data/` - her node'da ayrı yönetilir
- ❌ `build/`, `dist/` - build artifacts
- ❌ dev-only files
- ❌ server settings (server.py, production.py)
- ❌ server deployment (deployment/server.py)

**kullanım:**
```bash
# production node repo için gitignore aktifleştir
cp .gitignore.prod .gitignore
git add .
git commit -m "feat: node deployment"
git push prod main
```

## workflow

### development → push to dev

```bash
# development çalışması
cd /Users/berkhatirli/Desktop/unibos-dev

# dev gitignore kullan
cp .gitignore.dev .gitignore

# commit & push
git add .
git commit -m "feat: new feature"
git push dev main
```

### development → deploy to server

```bash
# server için hazırla
cp .gitignore.server .gitignore

# commit & push
git add .
git commit -m "deploy: server v0.534.0"
git push server main
```

### development → release to production

```bash
# production için hazırla
cp .gitignore.prod .gitignore

# version tag
git tag -a v0.534.0 -m "v0.534.0 release"

# commit & push
git add .
git commit -m "release: v0.534.0"
git push prod main --tags
```

## kritik güvenlik notları

### asla commit edilmemesi gerekenler:

1. **archive/** - development history, asla repo'ya gitmesin
2. **data/** - runtime data, her ortamda ayrı
3. **.env** - secrets ve api keys
4. **cli_dev/** - server ve prod'da olmamalı (güvenlik)
5. **build/**, **dist/** - build artifacts

### repo bazında güvenlik:

- **dev repo:** tüm tools (güvenli, sadece local)
- **server repo:** cli_dev yok, production tools var
- **prod repo:** sadece node cli, minimal exposure

## ignore dosyalarını test et

```bash
# hangi dosyalar ignore ediliyor?
git status --ignored

# belirli bir dosya ignore mi?
git check-ignore -v data/test.txt

# ignore kuralını test et
git check-ignore -v archive/versions/test/
```

## özet tablo

| ne? | dev | server | prod |
|-----|-----|--------|------|
| cli_dev | ✅ | ❌ | ❌ |
| cli_server | ✅ | ✅ | ❌ |
| cli_node | ✅ | ✅ | ✅ |
| settings/development.py | ✅ | ❌ | ❌ |
| settings/server.py | ✅ | ✅ | ❌ |
| settings/node.py | ✅ | ✅ | ✅ |
| deployment/server.py | ✅ | ✅ | ❌ |
| deployment/node.py | ✅ | ✅ | ✅ |
| archive/ | ❌ | ❌ | ❌ |
| data/ | ❌ | ❌ | ❌ |
| build/ | ❌ | ❌ | ❌ |
| modules/* | ✅ | ✅ | ✅ |
