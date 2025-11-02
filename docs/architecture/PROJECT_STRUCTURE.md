# 🗺️ UNIBOS Project Structure Map
*Last Updated: 2025-08-12 | Current Version: v446+*

## 🔗 Essential Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture details
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflow
- [INSTALLATION.md](INSTALLATION.md) - Setup instructions
- [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md) - Archive system guide

## 📁 Directory Overview

```
unibos/
├── backend/          # Django REST API + Web UI
├── src/              # Terminal UI & System Management
├── data/             # Shared Data Storage
├── archive/          # Version History & Documentation
├── quarantine/       # Temporary/Unknown Files
└── venv/             # Python Virtual Environment
```

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  UNIBOS v430                        │
│         Hybrid Terminal + Web Application           │
└─────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
   Terminal UI                          Web UI
   (/src/main.py)                  (Django Backend)
        │                                   │
        ├── Launches ──────────────────────→│
        │                                   │
        ├── currencies_enhanced.py         ├── apps/currencies/
        ├── personal_inflation.py          ├── apps/personal_inflation/
        ├── git_manager.py                 ├── apps/documents/
        └── version_manager.py             └── apps/[others]/
                │                                   │
                ↓                                   ↓
        /data/personal_inflation.db        /backend/db.sqlite3
```

## 📂 Detailed Structure

### `/backend/` - Django Web Backend
**Purpose:** REST API server and template-based web UI

```
backend/
├── manage.py                       # Django management script
├── db.sqlite3                      # Main database (SQLite)
├── unibos_backend/                 # Django project settings
│   ├── settings/
│   │   ├── base.py                # Base configuration
│   │   ├── development.py         # Dev settings
│   │   ├── production.py          # Production settings
│   │   └── emergency.py           # Minimal settings
│   ├── urls.py                     # URL routing
│   └── wsgi.py                     # WSGI application
├── apps/                           # Django applications
│   ├── core/                      # Core models & utilities
│   ├── authentication/            # JWT auth, 2FA
│   ├── users/                     # User management
│   ├── currencies/                # Exchange rates, crypto
│   ├── personal_inflation/        # Inflation tracking
│   ├── documents/                 # OCR, receipt management
│   ├── wimm/                      # Where Is My Money
│   ├── wims/                      # Where Is My Stuff
│   ├── cctv/                      # Camera monitoring
│   ├── recaria/                   # Space game
│   ├── birlikteyiz/               # Emergency mesh network
│   ├── administration/            # Admin features
│   ├── common/                    # Shared utilities
│   └── web_ui/                    # Web UI views
├── templates/                      # HTML templates
│   ├── web_ui/
│   │   ├── base.html              # Base template
│   │   ├── main.html              # Dashboard
│   │   └── modules/               # Module templates
│   ├── documents/                 # Document templates
│   └── cctv/                      # CCTV templates
└── static/                         # Static files (CSS, JS)
```

**Key Features:**
- JWT Authentication with refresh tokens
- WebSocket support via Django Channels
- PostgreSQL/SQLite database
- Template-based rendering (no separate frontend)
- RESTful API endpoints
- Celery task queue ready
- Redis cache support

### `/src/` - Terminal UI & System Management
**Purpose:** Command-line interface and system orchestration

```
src/
├── main.py                         # Main terminal UI entry point
├── VERSION.json                    # Version information
├── translations.py                 # 10-language support
├── database/                       # SQLAlchemy configuration
│   ├── config.py                  # Database settings
│   ├── models.py                  # Data models
│   └── migrations/                # Alembic migrations
├── Modules (Active):
│   ├── currencies_enhanced.py     # Currency tracking (API-based)
│   ├── personal_inflation.py      # Inflation calculator
│   ├── git_manager.py             # Git operations UI
│   ├── version_manager.py         # Version management
│   ├── development_manager.py     # Development tools
│   ├── server_manager.py          # Server control
│   └── communication_logger.py    # Session logging
├── UI Components:
│   ├── ui_architecture.py         # UI framework
│   ├── suggestion_manager.py      # AI suggestions
│   └── screenshot_manager.py      # Screenshot capture
└── Backups (To Clean):
    ├── main.py.backup_*           # Old versions
    └── git_manager_*.py           # Old managers
```

**Key Features:**
- Curses-based terminal UI
- Can launch Django backend
- Independent modules (doesn't import from backend)
- Uses `/data/` directory for storage
- Multi-language support
- Git integration

### `/data/` - Shared Data Storage
**Purpose:** Terminal UI data persistence

```
data/
├── personal_inflation.db           # SQLite for inflation data
└── suggestions.json                # AI suggestion cache
```

### `/archive/` - Version History
**Purpose:** Historical versions and documentation

```
archive/
├── versions/                       # Source code snapshots
│   └── unibos_v[XXX]_[timestamp]/
├── compressed/                     # ZIP archives
│   └── unibos_v[XXX]_[timestamp].zip
├── media/
│   └── screenshots/               # Version screenshots
├── communication_logs/             # Claude interaction logs
└── reports/                        # Development reports
```

### `/quarantine/` - Temporary Storage
**Purpose:** Files pending review or deletion

```
quarantine/
├── quarantine_manifest.json       # File tracking
└── QUARANTINE_KEEPER_LOG.md      # Activity log
```

## 💾 Database Architecture

### 1. Django Backend Database (`/backend/db.sqlite3`)
- **Type:** SQLite (dev) / PostgreSQL (production)
- **ORM:** Django ORM
- **Tables:** 100+ tables including:
  - auth_user, auth_group
  - currencies_*, documents_*
  - personal_inflation_*
  - administration_*

### 2. Terminal UI Database (`/data/personal_inflation.db`)
- **Type:** SQLite
- **ORM:** SQLAlchemy
- **Tables:** Products, prices, inflation data
- **Note:** Independent from Django database

### 3. Configuration Database (Planned)
- **Location:** `~/.unibos/unibos.db`
- **Purpose:** User preferences, settings

## 🔄 Component Relationships

### Terminal → Backend
- Terminal UI can start/stop Django server
- No direct data sharing
- Communication via HTTP API (if needed)

### Backend Internal
- All apps share Django ORM models
- Common middleware and authentication
- Shared templates and static files

### Data Flow
```
User Input → Terminal UI → Launch Backend
                ↓               ↓
           Local SQLite    Django Server
                           (Port 8000)
                                ↓
                           Web Browser
```

## 🚀 Entry Points

1. **Terminal UI:** `python src/main.py`
2. **Django Backend:** `python backend/manage.py runserver`
3. **Quick Start:** `./unibos.sh` (if exists)

## 🔧 Configuration Files

- `alembic.ini` - SQLAlchemy migrations
- `backend/.env` - Django environment variables
- `src/VERSION.json` - Version tracking
- `.git/` - Git repository

## 📝 Notes

### Active Development Areas
- `/backend/apps/` - All new features
- `/src/main.py` - Terminal UI improvements

### Deprecated/To Clean
- `/src/*.backup*` files
- Duplicate communication logs
- `__pycache__` directories

### Future Considerations
1. Unify database strategy
2. Create shared data layer
3. Implement proper API communication
4. Clean up backup files
5. Standardize module structure

---

## 📝 Documentation Organization

### Core Documentation Files
- `README.md` - Main project documentation
- `ARCHITECTURE.md` - System design and components
- `DEVELOPMENT.md` - Development guide
- `INSTALLATION.md` - Installation instructions
- `FEATURES.md` - Feature documentation
- `CHANGELOG.md` - Version history

### Development Guidelines
- `CLAUDE.md` - Claude AI development rules
- `CLAUDE_INSTRUCTIONS.md` - Detailed Claude instructions
- `DEVELOPMENT_LOG.md` - Development activity log
- `VERSION_MANAGEMENT.md` - Version system documentation

### System Documentation
- `PROJECT_STRUCTURE.md` - This file
- `ARCHIVE_GUIDE.md` - Archive protection guide
- `TROUBLESHOOTING.md` - Common issues and solutions
- `API.md` - API documentation

### Module-Specific Documentation
- `DOCUMENTS_MODULE_*.md` - Documents module guides
- `INVOICE_PROCESSOR_*.md` - Invoice processing documentation
- Various other module-specific files

---
*This structure map reflects the current state of UNIBOS v446+. The system operates as a hybrid application with independent Terminal and Web interfaces sharing minimal resources.*