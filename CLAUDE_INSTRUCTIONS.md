# CLAUDE INSTRUCTIONS - UNIBOS Development Guide

> **Essential rules and instructions for Claude AI when working on the UNIBOS project**

**Time Zone**: Europe/Istanbul (UTC+3) - ALL timestamps must use Istanbul time

## 🚨 CRITICAL RULES - NEVER IGNORE

### 1. Screenshot Priority (Most Important)
- **FIRST ACTION** every session: `ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'`
- If screenshots found: Read → Analyze → Archive → Add to todos
- Screenshots MUST be analyzed before ANY other work
- Archive format: `unibos_vXXX_YYYYMMDD_HHMM_N.png`
- Never leave screenshots in main directory

### 2. Archive Protection - ABSOLUTE PROHIBITION
- **NEVER DELETE** anything in `archive/` directory
- Archives contain entire project history (v001 to current)
- `archive/versions/` contains all past versions - NEVER remove
- No "cleanup" operations on archives allowed
- Archive loss = irreversible project damage

### 3. Directory Boundaries
- **NEVER leave** `/Users/berkhatirli/Desktop/unibos` directory
- Stay within project boundaries at all times
- No operations in Desktop or parent directories

### 4. Version Synchronization
- `src/VERSION.json` = `src/main.py` version info ALWAYS match
- Time format: Istanbul timezone (UTC+3) ONLY
- Build numbers: Use `date "+%Y%m%d_%H%M"` command output

### 5. Lowercase UI Standard
- ALL user interface text MUST be lowercase
- Applies to: menus, buttons, messages, errors, terminal UI
- Exceptions: protocols (HTTP), abbreviations (API), proper names (Django)
- Examples: "server starting..." ✅ "Server Starting..." ❌

## 📋 Communication Log Management

### Mandatory Log Creation
- **REQUIRED** for every version update
- Maximum 3 logs kept (auto-cleanup older logs)
- Format: `CLAUDE_COMMUNICATION_LOG_vXXX_to_vYYY_YYYYMMDD_HHMM.md`
- Must be created BEFORE version updates

### Log Structure
```markdown
# CLAUDE COMMUNICATION LOG

## Session Information
- **Start Version**: vXXX
- **End Version**: vYYY
- **Date**: YYYY-MM-DD
- **Start Time**: HH:MM:SS +03:00 (Istanbul)
- **End Time**: HH:MM:SS +03:00 (Istanbul)
- **Claude Model**: [Model name]

## Completed Tasks
- Task list

## User Feedback
- User messages and responses

## Resolved Issues
- ✅ Fixed issues

## Ongoing Issues
- ⚠️ Unresolved problems

## Technical Notes
- Important technical details
```

## 🔄 Version Delivery Process

### 1. Pre-Version Checklist
- [ ] Communication logs reviewed for unfinished tasks
- [ ] All screenshots processed and archived
- [ ] Critical issues resolved
- [ ] Tests passing (if test agent available)

### 2. Version Update Steps
1. **Get Current Time**: `TZ='Europe/Istanbul' date "+%Y%m%d_%H%M"`
2. **Update VERSION.json**: Use exact timestamp from step 1
3. **Update main.py**: Match VERSION_INFO with VERSION.json
4. **Update CHANGELOG.md**: Add new version entry at top
5. **Create/Update Communication Log**

### 3. Archiving (Choose One)
- **Recommended**: `python3 src/archive_version.py`
- **Alternative**: `bash src/version_manager.sh`
- **Never use**: Old scripts in archive/versions/

### 4. Git Operations - MANDATORY
```bash
git add -A
git commit -m "vXXX: [Description]"
git push origin main
git tag vXXX
git push origin vXXX
```

### 5. Django Server Restart - MANDATORY AFTER DJANGO CHANGES
**CRITICAL**: After any Django backend changes (models, views, templates, settings):
```bash
# Stop the server
pkill -f "manage.py runserver"

# Wait for cleanup
sleep 2

# Restart the server
cd /Users/berkhatirli/Desktop/unibos/backend
python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &

# Verify server is running
sleep 3
curl -I http://localhost:8000/
```
**Never skip this step after Django modifications!**

### 6. Delivery Message Format
```
İşlemleri tamamladım.
Versiyon: vXXX
Build: YYYYMMDD_HHMM
Yapılan işlemler: [Brief description]

📦 Arşivleme işlemi başlatılıyor...
[Archive command executed]
✅ Versiyon arşivlendi: versions klasörüne
```

## 🏗️ Project Structure

### Main Directory: `/Users/berkhatirli/Desktop/unibos`
```
unibos/
├── src/                    # Source code (single VERSION.json here)
│   ├── main.py            # Main application
│   ├── VERSION.json       # ONLY version file
│   └── [other modules]
├── archive/               # Protected archive (NEVER delete)
│   ├── versions/          # All past versions
│   └── media/             # Screenshots, diagrams
├── projects/              # Project modules
│   ├── recaria/           # Space exploration game
│   ├── birlikteyiz/       # Mesh network system
│   ├── currencies/        # Currency tracking
│   └── kisiselenflasyon/  # Inflation calculator
└── [documentation files]
```

## 🎯 Module System

### 4 Main Modules
1. **Recaria**: Space exploration and universe mapping game
2. **Birlikteyiz**: Mesh network communication system
3. **Currencies**: Enhanced currency tracking with live rates
4. **Kişisel Enflasyon**: Personal inflation calculator

### Development Standards
- Lowercase UI compliance mandatory
- Istanbul timezone for all timestamps
- Modular architecture with clear separation
- Test coverage for critical functions

## 🛡️ Safety Protocols

### Archive Safety
- Archive directory is PROJECT MEMORY - never modify
- All past versions preserved (v001 to current)
- No cleanup operations on archived content
- Backup before any major operations

### Screenshot Management
- Process immediately when found in main directory
- Archive with proper naming: `unibos_vXXX_YYYYMMDD_HHMM_N.png`
- Organize by version ranges in archive/media/screenshots/
- Always analyze content before archiving

### File Management
- Maximum 30K characters per documentation file
- Split into parts if size exceeded
- Never create files unless absolutely necessary
- Prefer editing existing files

## 🚀 Common Tasks

### Starting a Session
1. Run screenshot check: `ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'`
2. Read recent communication logs (last 3)
3. Check current version: `cat src/VERSION.json`
4. Review any unfinished tasks from logs

### Screenshot Processing
1. Found screenshots: Read with tool
2. Analyze content and extract requirements
3. Archive with proper naming
4. Add derived tasks to todo system
5. Verify main directory is clean

### Version Updates
1. Complete all pending tasks
2. Get current Istanbul time
3. Update VERSION.json and main.py
4. Add CHANGELOG entry
5. Create communication log
6. Archive version
7. Git push with tags

## 📚 Technology Stack

- **Backend**: Python/Django, SQLite/PostgreSQL
- **Frontend**: Terminal UI (primary), Web UI (secondary)
- **Architecture**: Modular monolith with plugin system
- **Deployment**: Raspberry Pi, local servers, cloud-ready
- **UI Theme**: Ultima Online 2 inspired retro terminal interface

## 🎮 UI/UX Philosophy

- **Aesthetic**: Retro terminal, Ultima Online 2 inspired
- **Typography**: Lowercase preference for modern clean look
- **Navigation**: Arrow keys, intuitive keyboard shortcuts
- **Feedback**: Clear status indicators, helpful error messages
- **Accessibility**: Terminal-first, web as secondary interface

---

**Project Owner**: Berk Hatırlı, Bitez/Bodrum, Türkiye
**Philosophy**: "🌍 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria! 🚀✨"

*This consolidated guide replaces 10+ separate CLAUDE files while maintaining all critical information.*
*Last Updated: 2025-08-09 - Istanbul Time*