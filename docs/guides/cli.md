# UNIBOS CLI Guide

**Last Updated:** 2025-11-13
**Version:** v533+

---

## Overview

The `unibos` CLI is a comprehensive command-line tool for managing all aspects of UNIBOS development, deployment, and maintenance.

**Features:**
- 🎨 Animated splash screen with UNIBOS logo
- 🌈 Color-coded output for better readability
- 📦 Modular command structure
- 🔧 Integration with existing scripts
- ⚡ Global command availability

---

## Installation

```bash
# From UNIBOS root directory
pip install -e .

# Verify installation
unibos --version
```

---

## Command Structure

```
unibos [OPTIONS] COMMAND [ARGS]...

Commands:
  status    System health check
  deploy    Deployment operations
  dev       Development commands
  db        Database management
```

---

## Commands Reference

### Status Commands

Check system health and configuration.

```bash
# Basic status check
unibos status

# Detailed status with all checks
unibos status --detailed

# JSON output (for scripts)
unibos status --json
```

**What it checks:**
- Python version and environment
- Django configuration
- Database connectivity
- Redis connectivity (if configured)
- Celery workers (if running)
- Directory structure
- Module status

---

### Deployment Commands

Deploy UNIBOS to various targets.

#### Deploy to Rocksteady VPS

```bash
# Full deployment (rsync + migrate + restart)
unibos deploy rocksteady

# Quick sync (no migration, faster)
unibos deploy rocksteady --quick

# Pre-flight check only (no actual deployment)
unibos deploy rocksteady --check-only
```

**What it does:**
1. Runs pre-flight checks (git status, uncommitted changes)
2. Syncs code to remote server via rsync
3. Installs dependencies (pip install -r requirements.txt)
4. Runs database migrations
5. Collects static files
6. Restarts Gunicorn and Nginx

#### Other Deployment Targets

```bash
# Deploy to local production
unibos deploy local

# Deploy to Raspberry Pi
unibos deploy raspberry <ip-address>

# Health check for deployment
unibos deploy check
```

---

### Development Commands

Manage local development environment.

#### Start Development Server

```bash
# Default (127.0.0.1:8000)
unibos dev run

# Custom port
unibos dev run --port 8080

# Custom host (accessible from network)
unibos dev run --host 0.0.0.0 --port 8000

# With settings override
unibos dev run --settings unibos_backend.settings.emergency
```

#### Django Shell

```bash
# Interactive Django shell
unibos dev shell

# IPython shell (if installed)
unibos dev shell --ipython
```

Example usage:

```python
# In Django shell
from modules.birlikteyiz.models import Earthquake
earthquakes = Earthquake.objects.filter(magnitude__gte=5.0)
print(f"Found {earthquakes.count()} earthquakes >= 5.0")
```

#### Run Tests

```bash
# Run all tests
unibos dev test

# Run specific app tests
unibos dev test modules.birlikteyiz

# Run with coverage
unibos dev test --coverage

# Verbose output
unibos dev test --verbose
```

#### Database Migrations

```bash
# Run migrations
unibos dev migrate

# Create new migrations
unibos dev makemigrations

# Create migrations for specific app
unibos dev makemigrations birlikteyiz

# Show migration plan (dry run)
unibos dev migrate --plan
```

#### View Logs

```bash
# Tail development logs
unibos dev logs

# Follow logs (live)
unibos dev logs --follow

# Last N lines
unibos dev logs --lines 100

# Filter by level
unibos dev logs --level ERROR
```

---

### Database Commands

Manage database operations.

#### Backup Database

```bash
# Create database backup
unibos db backup

# Backup with verification
unibos db backup --verify

# Backup to specific location
unibos db backup --output /path/to/backup.sql
```

**Backup location:** `data/database/backups/`

#### Restore Database

```bash
# Restore from backup
unibos db restore /path/to/backup.sql

# Restore with confirmation prompt
unibos db restore /path/to/backup.sql --interactive
```

⚠️ **Warning:** This will overwrite your current database!

#### Migration Status

```bash
# Show migration status
unibos db status

# Show unapplied migrations
unibos db status --pending

# Show migration plan
unibos db status --plan
```

#### Run Migrations

```bash
# Run all pending migrations
unibos db migrate

# Migrate specific app
unibos db migrate birlikteyiz

# Fake migration (mark as applied without running)
unibos db migrate --fake
```

---

## Environment Variables

The CLI respects these environment variables:

```bash
# Django settings module
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.development

# Python path (auto-set by CLI)
export PYTHONPATH=/path/to/unibos/core/web:/path/to/unibos

# Deployment target (for scripts)
export UNIBOS_DEPLOY_TARGET=rocksteady

# Debug mode
export UNIBOS_DEBUG=1
```

---

## Configuration

### CLI Configuration File

Optional configuration file: `~/.unibos/config.yaml`

```yaml
# Default settings module
default_settings: unibos_backend.settings.development

# Default deployment target
default_deploy_target: rocksteady

# Deployment targets
targets:
  rocksteady:
    host: ubuntu@158.178.201.117
    path: /var/www/unibos/

  raspberry:
    host: pi@192.168.1.100
    path: /home/pi/unibos/

  local:
    path: /Users/berkhatirli/Applications/unibos/

# Colors (disable for CI/CD)
colors: true

# Splash screen (disable for scripts)
splash: true
```

---

## Integration with Existing Scripts

The CLI wraps existing shell scripts for compatibility:

| CLI Command | Underlying Script |
|-------------|-------------------|
| `unibos deploy rocksteady` | `core/deployment/rocksteady_deploy.sh` |
| `unibos db backup` | `tools/scripts/backup_database.sh` |
| `unibos dev run` | `core/web/manage.py runserver` |

You can still use the scripts directly if needed:

```bash
# Direct script usage
./core/deployment/rocksteady_deploy.sh

# Via CLI (recommended)
unibos deploy rocksteady
```

---

## Tips & Tricks

### Aliases

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
alias ub='unibos'
alias ubs='unibos status'
alias ubd='unibos dev run'
alias ubdr='unibos deploy rocksteady'
```

### Quick Status Check

```bash
# Combine with watch for live monitoring
watch -n 5 'unibos status --detailed'
```

### Scripting with CLI

```bash
#!/bin/bash
# Deploy script example

set -e

echo "Running pre-deployment checks..."
unibos status --json > /tmp/status.json

if ! jq -e '.database.connected' /tmp/status.json; then
    echo "Database not connected!"
    exit 1
fi

echo "Deploying to rocksteady..."
unibos deploy rocksteady

echo "Verifying deployment..."
ssh ubuntu@158.178.201.117 'cd /var/www/unibos && source venv/bin/activate && python manage.py check'
```

### Development Workflow

```bash
# 1. Start dev server in background
unibos dev run &

# 2. Make changes to code...

# 3. Run tests
unibos dev test

# 4. Check status
unibos status

# 5. Deploy if all good
unibos deploy rocksteady --check-only
unibos deploy rocksteady
```

---

## Troubleshooting

### Command Not Found

```bash
# Reinstall CLI
pip install -e .

# Check installation
which unibos
unibos --version
```

### Permission Denied

```bash
# Ensure scripts are executable
chmod +x core/deployment/*.sh
chmod +x tools/scripts/*.sh
```

### Import Errors

The CLI automatically sets `PYTHONPATH`, but if you see import errors:

```bash
# Check current PYTHONPATH
echo $PYTHONPATH

# Manually set if needed
export PYTHONPATH=/path/to/unibos/core/web:/path/to/unibos:$PYTHONPATH
```

---

## Next Steps

- **Development workflow:** [development.md](development.md)
- **Deployment guide:** [deployment.md](deployment.md)
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md)

---

## See Also

- **CLI Source Code:** [core/cli/](../../core/cli/)
- **Deployment Scripts:** [core/deployment/](../../core/deployment/)
- **Architecture:** [../design/v533-architecture.md](../design/v533-architecture.md)

---

**Questions?** Create an issue or check the troubleshooting guide.
