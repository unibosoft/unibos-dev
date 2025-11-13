# Git Workflow - Kullanım Kılavuzu

**Document Type:** Usage Guide
**Created:** 2025-11-13
**Status:** Active

---

## 📋 Genel Bakış

UNIBOS, dev ve prod için iki ayrı git repository kullanır:

- **Dev:** `https://github.com/unibosoft/unibos_dev` - Tüm geliştirme geçmişi
- **Prod:** `https://github.com/unibosoft/unibos` - Temiz production releases

---

## 🚀 Hızlı Başlangıç

### İlk Kurulum

```bash
# 1. Git remote'ları kur
unibos git setup

# 2. Durumu kontrol et
unibos git status
```

---

## 📝 Günlük Kullanım

### 1. Development İçin (unibos_dev)

```bash
# Değişiklikler yap
vim core/web/...

# Stage ve commit
git add .
git commit -m "feat: yeni özellik"

# Dev repo'ya push
git push origin v533_migration
# veya CLI ile:
unibos git push-dev
```

**Dev'e GİDEN:**
- ✅ Tüm kaynak kod
- ✅ TODO.md, RULES.md
- ✅ docs/ (tüm dökümanlar)
- ✅ .prodignore, .archiveignore
- ✅ Test dosyaları
- ✅ CLI tools

### 2. Production İçin (unibos)

Production push'ları **sadece stable releases için** yapılır.

#### Manuel Yöntem (Şu an kullanılan):

```bash
# 1. Prod için branch oluştur
git checkout -b prod-main

# 2. Dev-only dosyaları kaldır
git rm -r TODO.md RULES.md .prodignore docs/rules/ docs/design/decisions/

# 3. Commit
git commit -m "chore: prepare production release v533"

# 4. Prod'a push
git push prod prod-main:main --force

# 5. Tag oluştur
git tag -a v533 -m "Release v533"
git push prod v533

# 6. Cleanup ve dev'e dön
git checkout v533_migration
git branch -D prod-main
```

#### CLI Yöntemi (Geliştirme aşamasında):

```bash
# Dry-run ile test
unibos git push-prod --dry-run

# Gerçek push (onay gerektirir)
unibos git push-prod
```

**Prod'a GİDEN:**
- ✅ Core source code
- ✅ README.md
- ✅ docs/guides/ (kullanıcı dökümanları)
- ✅ setup.py, VERSION.json
- ✅ Dockerfile, docker-compose.yml

**Prod'a GİTMEYEN:**
- ❌ TODO.md, RULES.md
- ❌ .prodignore
- ❌ docs/rules/, docs/design/decisions/
- ❌ archive/, data/, logs/
- ❌ .claude/, screenshots

---

## 🔄 Branch ve Tag Stratejisi

### Development (unibos_dev)

```
main                    # Ana development branch (kullanılmıyor)
v533_migration          # Aktif development branch ✅
v533                    # Version tag

Gelecek:
v534_migration          # Sonraki feature branch
v534                    # Version tag
```

### Production (unibos)

```
main                    # Ana production branch ✅
v533                    # Version tag

Gelecek:
v534                    # Version tag
```

---

## 🛠️ CLI Komutları Detaylı

### `unibos git status`

Her iki repo'nun durumunu gösterir.

```bash
unibos git status
```

**Çıktı:**
- Current branch
- Remotes (origin, prod)
- Working directory status
- Unpushed commits

### `unibos git setup`

Git remote'ları konfigüre eder.

```bash
# İlk kurulum
unibos git setup

# Force update
unibos git setup --force
```

**Kurduğu remote'lar:**
- `origin` → `https://github.com/unibosoft/unibos_dev`
- `prod` → `https://github.com/unibosoft/unibos`

### `unibos git push-dev`

Development repo'ya push yapar.

```bash
# Mevcut branch'i push et
unibos git push-dev

# Belirli branch'i push et
unibos git push-dev --branch v533_migration

# Force push (DİKKATLİ!)
unibos git push-dev --force
```

**Güvenlik:**
- ✅ Working directory temizliği kontrol eder
- ✅ Remote varlığını doğrular
- ⚠️ Force push için uyarı verir

### `unibos git sync-prod`

Local production dizinine sync yapar (test için).

```bash
# Default path: /Users/berkhatirli/Applications/unibos
unibos git sync-prod

# Custom path
unibos git sync-prod --path /path/to/prod

# Dry-run (önce test et)
unibos git sync-prod --dry-run
```

**Kullanım:**
- Local'de prod test etmek için
- Deployment öncesi doğrulama
- Prod build boyutu kontrolü

### `unibos git push-prod`

Production repo'ya filtered push yapar.

```bash
# Dry-run (ÖNERİLİR!)
unibos git push-prod --dry-run

# Gerçek push (onay ister)
unibos git push-prod

# Force push (onay atla)
unibos git push-prod --force
```

**Süreç:**
1. Temporary branch oluşturur (`prod-push-XXXXX`)
2. `.prodignore` patterns'e göre dosyaları kaldırır
3. Filtered tree'yi commit eder
4. `prod` remote'a push eder (main branch)
5. Temporary branch'i temizler

**⚠️ UYARI:** Bu prod repo için destructive bir işlemdir!

---

## 📋 Checklist: Production Release

Production push yapmadan önce:

- [ ] Tüm testler geçti
- [ ] Development branch temiz (`git status`)
- [ ] Version number güncellendi (`VERSION.json`)
- [ ] CHANGELOG/release notes hazır
- [ ] Local prod test edildi (`unibos git sync-prod`)
- [ ] Dry-run yapıldı (`unibos git push-prod --dry-run`)
- [ ] Backup alındı (gerekirse)

---

## 🔍 Verification

### Dev Push Sonrası

```bash
# Dev repo'da görünmeli
git log origin/v533_migration --oneline -5

# GitHub'da kontrol
# https://github.com/unibosoft/unibos_dev
```

### Prod Push Sonrası

```bash
# Prod repo'da görünmeli
git log prod/main --oneline -5

# GitHub'da kontrol
# https://github.com/unibosoft/unibos

# TODO.md, RULES.md olmamalı
# docs/rules/ olmamalı
# .prodignore olmamalı
```

---

## 🐛 Troubleshooting

### Problem: "Remote 'prod' not found"

```bash
# Solution
unibos git setup
```

### Problem: "Working directory not clean"

```bash
# Uncommitted changes var
git status

# Commit veya stash yap
git add .
git commit -m "..."
# veya
git stash
```

### Problem: Prod push başarısız

```bash
# 1. Dry-run ile test et
unibos git push-prod --dry-run

# 2. Log'ları kontrol et
git log --oneline -10

# 3. Remote'u kontrol et
git remote -v

# 4. Manuel fix gerekirse:
git checkout -b prod-fix
# Düzelt
git push prod prod-fix:main --force
git checkout v533_migration
git branch -D prod-fix
```

### Problem: Branch/tag conflict

```bash
# v533 hem branch hem tag ise
git branch -d v533  # Branch'i sil
git tag -d v533     # Tag'i sil

# Tekrar oluştur
git tag -a v533 -m "Release v533"
git push origin v533
```

---

## 📊 Best Practices

### 1. Commit Messages

```bash
# Development (detaylı)
git commit -m "feat(module): add new feature

- Implementation details
- Breaking changes
- Migration notes"

# Production (özet)
git commit -m "chore: prepare production release v533

Version: v533
Features: Dev/Prod workflow, CLI automation"
```

### 2. Push Frequency

**Development:**
- ✅ Her stable feature sonrası
- ✅ End of day backups
- ✅ Before major changes

**Production:**
- ✅ Major releases only (v533, v534, etc.)
- ✅ Critical hotfixes
- ❌ NOT for every dev commit

### 3. Branch Management

```bash
# Development
v533_migration → active development
v534_migration → next feature

# Production
main → always stable
v533, v534 → version tags
```

---

## 🔗 İlgili Dökümanlar

- [dev-prod-workflow.md](./dev-prod-workflow.md) - Complete workflow guide
- [deployment.md](./deployment.md) - Production deployment
- [../rules/archive-safety.md](../rules/archive-safety.md) - Archive protection

---

## 📝 Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-11-13 | Initial creation | System |
| 2025-11-13 | Added CLI commands reference | System |
| 2025-11-13 | Added troubleshooting guide | System |

---

**Last Updated:** 2025-11-13
**Status:** Active
**Review Frequency:** After major workflow changes
