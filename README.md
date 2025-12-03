# UNIBOS - Unicorn Bodrum Operating System

> **v1.0.0** - Production-ready modular platform with 4-tier CLI architecture, P2P foundation, and multi-platform support

## Quick Start

### Development (unibos-dev)
```bash
# Install development CLI
pipx install -e . --force

# Launch TUI
unibos-dev

# Or specific commands
unibos-dev dev run        # Start local web server
unibos-dev dev tui        # Open TUI
unibos-dev deploy         # Deploy to rocksteady
```

### Server (unibos-server)
```bash
# On production server
unibos-server start       # Start services
unibos-server status      # Check status
unibos-server logs        # View logs
```

## Architecture

### 4-Tier CLI System

| Profile | Command | Purpose | Target |
|---------|---------|---------|--------|
| **dev** | `unibos-dev` | Development & DevOps | Developers |
| **manager** | `unibos-manager` | Multi-node orchestration | System admins |
| **server** | `unibos-server` | Single server management | Server operators |
| **prod** | `unibos` | End-user application | All users |

### Project Structure

```
unibos-dev/
├── core/                          # Core system infrastructure
│   ├── clients/                   # Client applications
│   │   ├── cli/                   # CLI framework
│   │   ├── tui/                   # TUI framework (BaseTUI)
│   │   └── web/                   # Django backend
│   ├── profiles/                  # CLI profiles
│   │   ├── dev/                   # Developer profile
│   │   ├── manager/               # Manager profile
│   │   ├── server/                # Server profile
│   │   └── prod/                  # Production profile
│   ├── system/                    # System modules
│   │   ├── authentication/        # Auth & permissions
│   │   ├── users/                 # User management
│   │   ├── web_ui/                # Web interface
│   │   ├── common/                # Shared utilities
│   │   ├── administration/        # System admin
│   │   ├── logging/               # Audit logs
│   │   └── version_manager/       # Version control
│   └── base/                      # Shared models & registry
│
├── modules/                       # Business modules (13)
│   ├── currencies/                # Currency & crypto tracking
│   ├── wimm/                      # Financial management
│   ├── wims/                      # Inventory management
│   ├── documents/                 # OCR & document scanning
│   ├── personal_inflation/        # Personal CPI tracker
│   ├── birlikteyiz/              # Earthquake alerts
│   ├── cctv/                      # Camera monitoring
│   ├── recaria/                   # Recipe management
│   ├── movies/                    # Media library
│   ├── music/                     # Music player
│   ├── restopos/                  # Restaurant POS
│   ├── solitaire/                 # Multiplayer game
│   └── store/                     # E-commerce
│
├── deploy/                        # Deployment system
├── docs/                          # Documentation
├── data/                          # Runtime data (gitignored)
└── archive/                       # Version archives
```

## Requirements

### Minimum
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- 4GB RAM (8GB recommended)
- 20GB disk space

### Production Stack
- **ASGI Server**: Gunicorn + Uvicorn workers
- **Database**: PostgreSQL 15+
- **Cache/Broker**: Redis 7+
- **Task Queue**: Celery 5.3+
- **WebSocket**: Django Channels

## Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| PostgreSQL | Active | Primary database |
| Redis | Active | Cache, sessions, channels, celery |
| Gunicorn/Uvicorn | Active | ASGI with WebSocket support |
| Celery Worker | Active | 12 tasks discovered |
| Django Channels | Active | Real-time WebSocket |
| Deploy Pipeline | Active | 17-step automated deployment |

## Development

### Web Server
```bash
cd core/clients/web
./venv/bin/python manage.py runserver
```

### With Uvicorn (WebSocket support)
```bash
./venv/bin/uvicorn unibos_backend.asgi:application --reload
```

### Celery Worker
```bash
./venv/bin/celery -A unibos_backend worker --loglevel=info
```

### Celery Beat (Scheduler)
```bash
./venv/bin/celery -A unibos_backend beat --loglevel=info
```

## Deployment

### To Rocksteady Server
```bash
unibos-dev deploy rocksteady       # Dry run
unibos-dev deploy rocksteady live  # Live deployment
```

### Deploy Steps (17)
1. Validate configuration
2. Check SSH connectivity
3. **Backup database** (new)
4. Prepare deployment directory
5. Clone repository
6. Setup Python environment
7. Install dependencies
8. Install CLI
9. Create environment file
10. Setup module registry
11. Setup data directories
12. Setup PostgreSQL
13. Run migrations
14. Collect static files
15. Setup systemd service
16. Start service
17. Health check

## Documentation

- `docs/` - All documentation
- `TODO.md` - Development roadmap
- `CHANGELOG.md` - Version history
- `RULES.md` - Project rules

## Key Features

- **TUI**: Full-featured terminal interface
- **Web UI**: Django-based dashboard
- **Real-time**: WebSocket for live updates
- **Background Tasks**: Celery for async processing
- **Multi-node**: P2P architecture foundation
- **Version Archive**: Timestamp-based snapshots

## Author

**Berk Hatirli**
Bitez, Bodrum, Mugla, Turkiye

*Built with Claude Code*

---

**Current Version**: v1.0.0
**Last Updated**: 2025-12-03
