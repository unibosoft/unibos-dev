# UNIBOS Deployment Guide

**Last Updated:** 2025-11-13
**Target Version:** v533+

---

## Overview

This guide covers deploying UNIBOS to production environments:
- **Rocksteady VPS** - Primary production server
- **Local Production** - Local macOS production instance
- **Raspberry Pi** - Edge device deployment (future)

---

## Prerequisites

Before deploying:

1. ✅ Development environment working ([setup.md](setup.md))
2. ✅ All tests passing (`unibos dev test`)
3. ✅ Database migrations created and tested
4. ✅ Git repository clean (no uncommitted changes)
5. ✅ Read [deployment rules](../rules/deployment.md)

---

## Deployment Targets

### Rocksteady VPS

**Server:** `ubuntu@158.178.201.117`
**Path:** `/var/www/unibos/`
**Status:** ✅ Production (v533)

**Stack:**
- OS: Ubuntu 22.04 LTS
- Python: 3.10+
- Web Server: Nginx
- WSGI Server: Gunicorn
- Database: PostgreSQL 14
- Task Queue: Celery + Redis

### Local Production

**Path:** `/Users/berkhatirli/Applications/unibos/`
**Status:** 📋 Planned

**Stack:**
- OS: macOS
- Python: 3.13
- Web Server: Nginx (via Homebrew)
- WSGI Server: Gunicorn
- Database: PostgreSQL (via Homebrew)

### Raspberry Pi

**Status:** 📋 Planned for Phase 4

**Stack:**
- OS: Raspberry Pi OS (64-bit)
- Python: 3.10+
- Web Server: Nginx
- WSGI Server: Gunicorn (lightweight config)
- Database: SQLite or PostgreSQL

---

## Rocksteady VPS Deployment

### Quick Deployment

```bash
# Full deployment (recommended)
unibos deploy rocksteady

# Quick sync (no migrations, faster)
unibos deploy rocksteady --quick

# Pre-flight check only
unibos deploy rocksteady --check-only
```

### What Happens During Deployment

1. **Pre-flight Checks:**
   - Git status (must be clean or have only safe uncommitted changes)
   - SSH connectivity test
   - Disk space check

2. **Code Sync:**
   - rsync code to remote server
   - Excludes: venv/, data/, logs/, *.pyc, __pycache__

3. **Dependencies:**
   - Installs/updates Python packages from requirements.txt

4. **Database:**
   - Runs pending migrations
   - Creates backup before migrations

5. **Static Files:**
   - Collects static files (CSS, JS, images)

6. **Services:**
   - Restarts Gunicorn (WSGI server)
   - Restarts Nginx (web server)
   - Restarts Celery workers (if configured)

7. **Verification:**
   - Checks service status
   - Tests HTTP connectivity
   - Verifies database connectivity

### Manual Deployment Steps

If the CLI is not available, deploy manually:

```bash
# 1. SSH to server
ssh ubuntu@158.178.201.117

# 2. Navigate to project
cd /var/www/unibos

# 3. Backup database
sudo -u postgres pg_dump unibos > /tmp/unibos_backup_$(date +%Y%m%d_%H%M%S).sql

# 4. Pull latest code
git pull origin v533_migration

# 5. Activate venv
source venv/bin/activate

# 6. Install dependencies
pip install -r core/web/requirements.txt

# 7. Run migrations
cd core/web
python manage.py migrate

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart celery  # if configured

# 10. Check status
sudo systemctl status gunicorn
sudo systemctl status nginx

# 11. Test
curl http://localhost:8000/api/health/
```

### Rollback Procedure

If deployment fails:

```bash
# 1. SSH to server
ssh ubuntu@158.178.201.117

# 2. Navigate to project
cd /var/www/unibos

# 3. Checkout previous version
git log --oneline -n 5  # Find previous commit
git checkout <previous-commit-hash>

# 4. Restore database (if migrations ran)
sudo -u postgres psql unibos < /tmp/unibos_backup_YYYYMMDD_HHMMSS.sql

# 5. Restart services
source venv/bin/activate
cd core/web
python manage.py migrate --fake-initial  # If needed
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 6. Verify
curl http://localhost:8000/api/health/
```

---

## Local Production Deployment

**Status:** Planned for Phase 4

### Setup Local Production

```bash
# 1. Create production directory
sudo mkdir -p /Users/berkhatirli/Applications/unibos
sudo chown $USER /Users/berkhatirli/Applications/unibos

# 2. Clone repository
cd /Users/berkhatirli/Applications
git clone <repo-url> unibos
cd unibos

# 3. Install dependencies
cd core/web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure production settings
cp .env.example .env
# Edit .env with production values

# 5. Run migrations
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.production
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Create superuser
python manage.py createsuperuser
```

### Using CLI for Local Deployment

```bash
# Deploy to local production
unibos deploy local
```

---

## Raspberry Pi Deployment

**Status:** Planned for Phase 4

### Hardware Requirements

- Raspberry Pi 4 or 5 (4GB+ RAM recommended)
- 32GB+ microSD card (Class 10 or better)
- Stable power supply
- Ethernet connection (recommended for reliability)

### Setup Process

```bash
# On Raspberry Pi

# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql redis-server

# 3. Clone repository
cd /home/pi
git clone <repo-url> unibos
cd unibos

# 4. Install Python dependencies
cd core/web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure for Pi (lightweight settings)
# ... configuration steps ...

# 6. Setup database
sudo -u postgres createuser unibos
sudo -u postgres createdb unibos
python manage.py migrate

# 7. Setup systemd services
# ... service configuration ...

# 8. Start services
sudo systemctl start gunicorn
sudo systemctl start nginx
```

### Using CLI for Pi Deployment

```bash
# Deploy to Raspberry Pi
unibos deploy raspberry <pi-ip-address>
```

---

## Environment Configuration

### Production Settings

**File:** `core/web/unibos_backend/settings/production.py`

**Key settings:**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', '158.178.201.117']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unibos',
        'USER': 'unibos',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

MEDIA_ROOT = '/var/www/unibos/data/modules/'
STATIC_ROOT = '/var/www/unibos/staticfiles/'
```

### Environment Variables

Production `.env` file:

```bash
# Django
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,158.178.201.117

# Database
DB_NAME=unibos
DB_USER=unibos
DB_PASSWORD=<strong-password>
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Service Configuration

### Gunicorn

**File:** `/etc/systemd/system/gunicorn.service`

```ini
[Unit]
Description=Gunicorn daemon for UNIBOS
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/unibos/core/web
Environment="PATH=/var/www/unibos/core/web/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=unibos_backend.settings.production"
ExecStart=/var/www/unibos/core/web/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/unibos/gunicorn.sock \
    --timeout 120 \
    --access-logfile /var/www/unibos/logs/gunicorn-access.log \
    --error-logfile /var/www/unibos/logs/gunicorn-error.log \
    unibos_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Nginx

**File:** `/etc/nginx/sites-available/unibos`

```nginx
server {
    listen 80;
    server_name yourdomain.com 158.178.201.117;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/unibos/staticfiles/;
    }

    location /media/ {
        alias /var/www/unibos/data/modules/;
    }

    location / {
        proxy_pass http://unix:/var/www/unibos/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/unibos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Celery (Optional)

**File:** `/etc/systemd/system/celery.service`

```ini
[Unit]
Description=Celery worker for UNIBOS
After=network.target redis.service

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/unibos/core/web
Environment="PATH=/var/www/unibos/core/web/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=unibos_backend.settings.production"
ExecStart=/var/www/unibos/core/web/venv/bin/celery -A unibos_backend worker \
    --loglevel=info \
    --logfile=/var/www/unibos/logs/celery.log

[Install]
WantedBy=multi-user.target
```

---

## Monitoring & Maintenance

### Check Service Status

```bash
# On remote server
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status celery
sudo systemctl status redis
sudo systemctl status postgresql
```

### View Logs

```bash
# Gunicorn logs
tail -f /var/www/unibos/logs/gunicorn-error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Django logs
tail -f /var/www/unibos/core/web/logs/django.log

# Celery logs
tail -f /var/www/unibos/logs/celery.log
```

### Database Backups

```bash
# Manual backup
unibos db backup

# Or on remote server
ssh ubuntu@158.178.201.117 'cd /var/www/unibos && source venv/bin/activate && python core/web/manage.py dumpdata > /tmp/backup.json'

# Automated backups (cron)
# Add to crontab: crontab -e
0 2 * * * cd /var/www/unibos && source venv/bin/activate && python core/web/manage.py dumpdata > /var/backups/unibos_$(date +\%Y\%m\%d).json
```

### Disk Space

```bash
# Check disk usage
df -h

# Check data directory size
du -sh /var/www/unibos/data/

# Clean old log files
find /var/www/unibos/logs -name "*.log" -mtime +30 -delete
```

---

## Troubleshooting

### Deployment Failed

```bash
# Check deployment logs
unibos deploy rocksteady --check-only

# Check SSH connectivity
ssh ubuntu@158.178.201.117 'echo "SSH OK"'

# Check disk space on remote
ssh ubuntu@158.178.201.117 'df -h'

# Check git status on remote
ssh ubuntu@158.178.201.117 'cd /var/www/unibos && git status'
```

### Service Not Starting

```bash
# Check service status
sudo systemctl status gunicorn

# View detailed logs
sudo journalctl -u gunicorn -n 50

# Check file permissions
ls -la /var/www/unibos/

# Check socket file
ls -la /var/www/unibos/gunicorn.sock
```

### 502 Bad Gateway

Common causes:

1. **Gunicorn not running:**
   ```bash
   sudo systemctl start gunicorn
   sudo systemctl status gunicorn
   ```

2. **Socket permission issues:**
   ```bash
   sudo chown ubuntu:www-data /var/www/unibos/gunicorn.sock
   sudo chmod 660 /var/www/unibos/gunicorn.sock
   ```

3. **Nginx misconfiguration:**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Database Connection Failed

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
psql -U unibos -d unibos -h localhost

# Check credentials in .env
cat /var/www/unibos/core/web/.env | grep DB_
```

---

## Security Checklist

Before deploying to production:

- [ ] `DEBUG = False` in production settings
- [ ] Strong `SECRET_KEY` (50+ random characters)
- [ ] HTTPS enabled (SSL certificates installed)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] Database password is strong (20+ characters)
- [ ] `.env` file permissions: `chmod 600 .env`
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] SSH key authentication (password auth disabled)
- [ ] Regular backups configured
- [ ] Monitoring set up (Sentry, logs, etc.)

---

## Next Steps

- **Monitoring setup:** Configure Sentry, Prometheus, or similar
- **SSL certificates:** Set up Let's Encrypt for HTTPS
- **CDN:** Configure CloudFlare or similar for static files
- **Scaling:** Add load balancer, multiple workers

---

## See Also

- **Deployment Rules:** [../rules/deployment.md](../rules/deployment.md)
- **Architecture:** [../design/v533-architecture.md](../design/v533-architecture.md)
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md)
- **CLI Guide:** [cli.md](cli.md)

---

**Questions?** Check [troubleshooting.md](troubleshooting.md) or create an issue.
