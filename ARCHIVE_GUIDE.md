# UNIBOS Archive System Guide

> **Complete guide to UNIBOS archive system and protection protocols**

## 🔗 Related Documentation
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version control system
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) - Change tracking
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Directory organization

## 🚨 CRITICAL RULE: NEVER DELETE ARCHIVES

**THE MOST IMPORTANT RULE**: Archives are NEVER deleted under any circumstances.

- Archives contain complete project history (v001 to current)
- Deletion would cause irreversible damage
- No "cleanup" operations allowed on archive content
- This rule overrides all other rules

## 📂 Archive Structure

### Main Archive Directory: `archive/`
```
archive/
├── versions/              # All past versions (PROTECTED)
│   ├── unibos_v001_*/    # First version
│   ├── unibos_v002_*/    # Second version
│   ├── ...               # All versions preserved
│   └── unibos_v425_*/    # Latest archived version
├── media/                # Media files
│   ├── screenshots/      # Screenshot archives by version range
│   │   ├── v001-099/    # Early versions
│   │   ├── v100-199/    # UI redesign era
│   │   ├── v200-299/    # Architecture maturation
│   │   └── v300-399/    # Web integration era
│   └── diagrams/        # Technical diagrams
├── reports/             # Generated reports
└── references/          # External references
```

### Version Directory Format
- **Standard naming**: `unibos_vXXX_YYYYMMDD_HHMM/`
- **Examples**:
  - `unibos_v062_20250715_1808/`
  - `unibos_v322_20250802_2211/`
  - `unibos_v425_20250809_0152/`

## 🛡️ Protection Protocols

### Absolutely Prohibited Operations
```bash
# NEVER DO THESE:
rm -rf archive/versions/*           # FORBIDDEN
rm archive/versions/unibos_v*       # FORBIDDEN  
mv archive/versions/* /tmp/         # FORBIDDEN
"cleanup" of archive directories    # FORBIDDEN
renaming version directories        # FORBIDDEN
```

### Allowed Operations
```bash
# THESE ARE SAFE:
ls -la archive/versions/                    # List contents
cp -r archive/versions/unibos_v123_* /backup/  # Backup copy
mkdir archive/versions/unibos_vNEW_*/       # Add new version
cat archive/versions/unibos_v123_*/README.md   # Read files
```

## 📦 Creating New Archives

### Automatic Method (Recommended)
```bash
# Use the official archive script
python3 src/archive_version.py
```

### Manual Method (If Needed)
```bash
# 1. Create version directory
VERSION="v123"
TIMESTAMP=$(TZ='Europe/Istanbul' date "+%Y%m%d_%H%M")
mkdir -p "archive/versions/unibos_${VERSION}_${TIMESTAMP}"

# 2. Copy files (EXCLUDE archive to prevent nesting)
rsync -av \
  --exclude='archive' \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='src/venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  . "archive/versions/unibos_${VERSION}_${TIMESTAMP}/"

# 3. Verify no nested archive (CRITICAL CHECK)
find archive/versions/unibos_${VERSION}_${TIMESTAMP} -name "archive" -type d
# This MUST return empty - if not, fix immediately
```

## 🔍 Archive Verification

### Daily Health Checks
```bash
# 1. Count total versions (should only increase)
ls -la archive/versions/ | wc -l

# 2. Check for nested archives (MUST be empty)
find archive/versions -name "archive" -type d

# 3. Check recent archives exist
ls -la archive/versions/ | tail -5

# 4. Verify standard naming
ls archive/versions/ | grep -v "^unibos_v[0-9].*_[0-9].*_[0-9].*$"
# This should be empty (all names follow standard)
```

### Size Monitoring
```bash
# Check archive sizes (normal range: 10MB-50MB per version)
du -sh archive/versions/unibos_v*/ | tail -10

# Total archive size
du -sh archive/
```

## 📸 Screenshot Archive Management

### Screenshot Processing Workflow
1. **Detection**: Check main directory for screenshots
2. **Analysis**: Read and understand screenshot content  
3. **Naming**: Use format `unibos_vXXX_YYYYMMDD_HHMM_N.png`
4. **Archiving**: Move to appropriate version range directory
5. **Verification**: Ensure main directory is clean

### Screenshot Organization
```
archive/media/screenshots/
├── v001-099/           # Foundation era screenshots
├── v100-199/           # UI redesign era screenshots  
├── v200-299/           # Architecture maturation screenshots
├── v300-399/           # Web integration era screenshots
└── v400-499/           # Current era screenshots
```

### Screenshot Commands
```bash
# Check for unprocessed screenshots
ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'

# Archive screenshot manually
CURRENT_VERSION="v425"
TIMESTAMP=$(TZ='Europe/Istanbul' date "+%Y%m%d_%H%M")
mv "Screenshot 2025-08-09 at 10.30.45.png" "unibos_${CURRENT_VERSION}_${TIMESTAMP}_1.png"
mv "unibos_${CURRENT_VERSION}_${TIMESTAMP}_1.png" "archive/media/screenshots/v400-499/"

# Verify main directory clean
ls *.png *.jpg *.jpeg 2>/dev/null || echo "✅ Main directory clean"
```

## 🔄 Archive Maintenance

### Regular Maintenance Tasks
1. **Version Verification**: Ensure all versions properly archived
2. **Naming Consistency**: Check all directories follow standard format
3. **No Nesting**: Verify no archive directories within archives
4. **Backup Status**: Confirm external backups are current

### Emergency Recovery
If archives are accidentally damaged:

```bash
# 1. STOP immediately - don't make it worse
# 2. Check if backup exists
ls -la unibos_backup_2025_*/

# 3. Restore from backup
rsync -av unibos_backup_2025_*/archive/ archive/

# 4. Restore from git history if needed
git log --name-status | grep archive

# 5. Verify restoration
find archive/versions -name "archive" -type d  # Should be empty
ls -la archive/versions/ | wc -l              # Should show expected count
```

### Backup Creation
```bash
# Create external backup (recommended weekly)
BACKUP_DATE=$(date +%Y_%m_%d)
rsync -av archive/ "../unibos_backup_${BACKUP_DATE}/"

# Verify backup
diff -r archive/ "../unibos_backup_${BACKUP_DATE}/"
```

## 📊 Archive Statistics

### Current Status (as of v425)
- **Total Versions Archived**: 244+
- **Archive Size**: ~11GB
- **Development Period**: 2025-present
- **Oldest Version**: v001 (preserved)
- **Protection Status**: ✅ All versions protected

### Growth Metrics
- **Average Version Size**: ~45MB (excluding nested archives)
- **Daily Growth**: 2-5 new versions typical
- **Screenshot Collection**: 500+ screenshots across all versions
- **Critical Milestones Preserved**: All major feature releases

## 🚀 Integration with Development

### Pre-Development Checks
```bash
# Always verify archive health before starting work
find archive/versions -name "archive" -type d | wc -l  # Must be 0
ls -la archive/versions/ | tail -3                    # Check recent versions
```

### Post-Development Actions
```bash
# Archive the completed version
python3 src/archive_version.py

# Verify archiving succeeded
ls -la archive/versions/ | tail -1                    # Check latest
find archive/versions -name "archive" -type d | wc -l  # Still must be 0
```

### Communication Log Integration
- Communication logs are archived with each version
- Maximum 3 active logs maintained (older archived)
- Archive preserves complete development conversation history

## 💡 Best Practices

### Do's ✅
- Always use official archive scripts when possible
- Verify archive integrity after each operation  
- Maintain consistent naming conventions
- Keep archives organized by version ranges
- Create regular external backups

### Don'ts ❌
- Never delete any archive content
- Never rename archived versions
- Never move archives to different locations
- Never "clean up" old versions
- Never store large files outside proper structure

---

**Remember**: Archives are the project's memory. They contain the complete evolution from v001 to current, including all decision-making context, debugging history, and development lessons learned. Their loss would be catastrophic and irreversible.

**Philosophy**: "Every version tells a story - preserve them all."

## 📈 Archive System Metrics
- **Protection Level**: Maximum (Never Delete)
- **Backup Frequency**: Weekly recommended
- **Version Naming**: Standardized format enforced
- **Nested Archive Check**: Automated verification

*This guide ensures UNIBOS archive system integrity across all development activities.*
*Last Updated: 2025-08-12 | Version: 2.0*