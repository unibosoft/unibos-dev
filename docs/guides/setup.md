# UNIBOS Setup Guide

**Last Updated:** 2025-11-13
**Target Version:** v533+

---

## Prerequisites

- **Operating System:** macOS, Linux, or Raspberry Pi OS
- **Python:** 3.10+ (3.13 recommended)
- **PostgreSQL:** 14+ (or SQLite for development)
- **Redis:** 6+ (for Celery task queue)
- **Git:** 2.30+

---

## Quick Start (Local Development)

### 1. Clone Repository

```bash
cd ~/Desktop
git clone <repository-url> unibos
cd unibos
```

### 2. Install Python Dependencies

```bash
cd core/web
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 3. Install UNIBOS CLI

From the root directory:

```bash
pip install -e .
```

Verify installation:

```bash
unibos --version
unibos --help
```

### 4. Configure Settings

Use the emergency settings for first-time setup:

```bash
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency
```

### 5. Initialize Database

```bash
cd core/web
unibos db migrate  # Or: ./venv/bin/python3 manage.py migrate
```

### 6. Create Superuser

```bash
unibos dev shell
# In Django shell:
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@unibos.local', 'your-password')
exit()
```

### 7. Start Development Server

```bash
unibos dev run
# Or with custom port:
unibos dev run --port 8080
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Directory Structure

After setup, your directory structure should look like:

```
unibos/
├── core/
│   ├── cli/              # CLI tool
│   ├── web/              # Django web application
│   │   ├── venv/         # Python virtual environment
│   │   ├── unibos_backend/  # Django project
│   │   └── manage.py
│   └── deployment/       # Deployment scripts
├── modules/              # UNIBOS modules
│   ├── birlikteyiz/
│   ├── documents/
│   ├── music/
│   └── ...
├── data/                 # Data directory (created on first run)
│   ├── modules/          # Module uploads
│   ├── shared/           # Shared data
│   └── database/         # Database backups
├── docs/                 # Documentation
└── setup.py
```

---

## Configuration Files

### Settings Files (Priority Order)

UNIBOS uses different settings files for different environments:

1. **emergency.py** - Minimal settings (SQLite, no Redis, simple MEDIA_ROOT)
   - Use for: First-time setup, recovery, testing
   - `DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency`

2. **dev_simple.py** - Simple development settings
   - Use for: Basic development
   - `DJANGO_SETTINGS_MODULE=unibos_backend.settings.dev_simple`

3. **development.py** - Full development settings (PostgreSQL, Redis, Celery)
   - Use for: Full-stack development
   - `DJANGO_SETTINGS_MODULE=unibos_backend.settings.development`

4. **production.py** - Production settings
   - Use for: Deployment (rocksteady, raspberry pi)
   - `DJANGO_SETTINGS_MODULE=unibos_backend.settings.production`

### Environment Variables

Create a `.env` file in `core/web/`:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (if using PostgreSQL)
DB_NAME=unibos
DB_USER=unibos
DB_PASSWORD=unibos_password
DB_HOST=localhost
DB_PORT=5432

# Redis (if using Celery)
REDIS_URL=redis://localhost:6379/0

# EMSC API (for earthquake data - birlikteyiz module)
EMSC_API_URL=https://www.seismicportal.eu/fdsnws/event/1/query
```

---

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'unibos_backend'`:

```bash
# Ensure you're in core/web/ directory
cd core/web

# Set PYTHONPATH
export PYTHONPATH=/path/to/unibos/core/web:/path/to/unibos:$PYTHONPATH

# Or use the CLI which handles this automatically
unibos dev run
```

### Database Errors

If migrations fail:

```bash
# Check database status
unibos db status

# Reset database (⚠️ DELETES ALL DATA)
rm core/web/db.sqlite3
unibos db migrate
```

### Permission Errors

If you see "Permission denied" for `data/` directory:

```bash
# Create data directory with correct permissions
mkdir -p data/modules
chmod -R 755 data/
```

### Port Already in Use

If port 8000 is busy:

```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use a different port
unibos dev run --port 8080
```

---

## Next Steps

After setup:

1. **Learn the CLI:** [cli.md](cli.md)
2. **Start developing:** [development.md](development.md)
3. **Deploy to production:** [deployment.md](deployment.md)

---

## See Also

- **Architecture:** [../design/v533-architecture.md](../design/v533-architecture.md)
- **Rules:** [../rules/](../rules/)
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md)

---

**Questions?** Check [troubleshooting.md](troubleshooting.md) or create an issue.
