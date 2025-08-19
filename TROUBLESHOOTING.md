# UNIBOS Troubleshooting Guide

> **Essential troubleshooting information for common UNIBOS issues**

## 🔗 Quick Links
- [INSTALLATION.md](INSTALLATION.md) - Installation guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md) - Archive protocols

## 🚨 Critical Issues

### Navigation Problems
**Symptoms**: Arrow keys not working, menu navigation broken
**Common Causes**:
- Terminal state corruption
- ANSI escape sequence issues
- Input buffer problems

**Solutions**:
```bash
# Reset terminal state
reset

# Clear input buffers
stty sane

# Restart UNIBOS
./unibos.sh

# If problem persists, check recent changes in main.py get_single_key() function
```

**Version History**: Fixed in v322 after regression in v321

### Screenshot Issues
**Symptoms**: Screenshots not being processed, accumulating in main directory
**Solutions**:
```bash
# Manual check for screenshots
ls -la | grep -E '\.(png|jpg|jpeg|PNG|JPG|JPEG)$'

# Process screenshots manually
python3 src/screenshot_manager.py

# Archive screenshots with proper naming
mv "Screenshot 2025-*.png" "unibos_vXXX_YYYYMMDD_HHMM_1.png"
mv "unibos_vXXX_YYYYMMDD_HHMM_1.png" "archive/media/screenshots/vXXX-XXX/"
```

**Prevention**: Always check for screenshots at start of each session

### Web UI Connection Issues
**Symptoms**: Web interface not starting, connection refused, timeout errors
**Solutions**:
```bash
# Check if ports are in use
lsof -i :3000
lsof -i :8000

# Kill conflicting processes
pkill -f "node.*3000"
pkill -f "python.*8000"

# Restart services with proper sequence
python3 src/simple_server_manager.py

# Check for CI environment variables
echo $CI  # Should be empty or 'false'
```

**Configuration**: Ensure 60s timeout, CI=false in environment

### Version Sync Issues
**Symptoms**: VERSION.json and main.py showing different versions
**Solutions**:
```bash
# Check version consistency
cat src/VERSION.json | grep version
grep "VERSION_INFO" src/main.py -A 5

# Get current Istanbul time
TZ='Europe/Istanbul' date "+%Y%m%d_%H%M"

# Update both files with same timestamp
python3 src/get_current_time.py
# Then manually update VERSION.json and main.py
```

**Prevention**: Always use system time commands, never estimate

## 🐛 Common Bugs

### Database Connection Issues
**Symptoms**: Database errors, connection refused, migration issues
**Solutions**:
```bash
# Check database file
ls -la data/personal_inflation.db

# Check database wizard
python3 src/database_setup_wizard.py

# Reset database if corrupted
rm data/personal_inflation.db
python3 src/database_setup_wizard.py --reset
```

### Module Loading Failures
**Symptoms**: Modules not appearing in menu, import errors
**Solutions**:
```bash
# Check module availability
ls -la projects/

# Test module imports
python3 -c "
import sys
sys.path.append('src')
sys.path.append('projects')
try:
    import recaria
    print('Recaria: OK')
except: print('Recaria: FAIL')
"

# Check Python path and dependencies
python3 -c "import sys; print('\n'.join(sys.path))"
```

### Terminal Display Issues
**Symptoms**: Garbled text, ANSI characters visible, display corruption
**Solutions**:
```bash
# Reset terminal completely
reset
clear

# Check terminal type
echo $TERM

# Fix ANSI sequence handling
# Edit main.py get_single_key() function if needed

# Ensure proper flush
# All print() statements should have flush=True
```

## ⚡ Performance Issues

### Slow Startup
**Causes & Solutions**:
- **Large archive directory**: Normal, archives preserved intentionally
- **Module initialization**: Check for hanging imports
- **Database operations**: Optimize queries, check db file size
- **Network timeouts**: Check web ui startup sequence

### Memory Usage
**Monitoring**:
```bash
# Check process memory
ps aux | grep python | grep unibos

# Check directory sizes
du -sh archive/
du -sh src/
du -sh projects/
```

**Optimization**:
- Archive cleanup NOT allowed (archives protected)
- Clear temporary files in /tmp/
- Restart if memory usage excessive

### Web Interface Slow Loading
**Solutions**:
```bash
# Check frontend build
ls -la web/frontend/build/

# Rebuild if necessary
cd web/frontend/
npm install
npm run build

# Check backend performance
python3 manage.py check --deploy
```

## 🔧 Development Issues

### Git Push Failures
**Symptoms**: Push rejected, conflicts, uncommitted changes
**Solutions**:
```bash
# Check status
git status

# Force add all changes
git add -A

# Commit with proper message
git commit -m "vXXX: [Description]"

# Push main branch
git push origin main

# Create and push tag
git tag vXXX
git push origin vXXX

# Verify remote
git ls-remote --tags origin | grep vXXX
```

### Archive Creation Issues
**Symptoms**: Archive script fails, version not created
**Solutions**:
```bash
# Use recommended archiving method
python3 src/archive_version.py

# If that fails, try manual method
mkdir -p archive/versions/unibos_vXXX_YYYYMMDD_HHMM
rsync -av --exclude='archive' --exclude='.git' --exclude='venv' \
      --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
      . "archive/versions/unibos_vXXX_YYYYMMDD_HHMM/"

# Verify no nested archives
find archive/versions -name "archive" -type d
# Should return empty
```

### Communication Log Management
**Symptoms**: Too many logs, logs not being created
**Solutions**:
```bash
# Check current logs
ls -la CLAUDE_COMMUNICATION_LOG_*.md

# Count logs (should be max 3)
ls CLAUDE_COMMUNICATION_LOG_*.md | wc -l

# Clean old logs if needed
ls -t CLAUDE_COMMUNICATION_LOG_*.md | tail -n +4 | xargs rm

# Create new log manually if needed
# Follow format in CLAUDE_INSTRUCTIONS.md
```

## 🛡️ Safety Checks

### Archive Integrity
```bash
# Check archive structure
ls -la archive/versions/ | wc -l

# Verify no nested archives (should be empty)
find archive/versions -name "archive" -type d

# Check recent versions
ls -la archive/versions/ | tail -5
```

### Version Consistency
```bash
# Check version files match
echo "VERSION.json:"
cat src/VERSION.json | grep -E "(version|build)"
echo "main.py:"
grep -A 3 "VERSION_INFO" src/main.py
```

### File System Health
```bash
# Check main directory cleanliness
ls -la *.png *.jpg *.jpeg 2>/dev/null || echo "✅ No screenshots in main dir"

# Check for temporary files
find . -name "*.tmp" -o -name "*.log" -o -name "*~" | head -10

# Check permissions
ls -la src/main.py src/VERSION.json
```

## 📞 Getting Help

### Log Analysis
When reporting issues, include:
```bash
# System info
uname -a
python3 --version

# Recent logs
tail -50 unibos.log 

# Recent changes
git log --oneline -5

# Current version
cat src/VERSION.json
```

### Common Error Patterns
- **"No such file"**: Check working directory is `/Users/berkhatirli/Desktop/unibos`
- **"Permission denied"**: Check file permissions, may need chmod +x
- **"Module not found"**: Check Python path and virtual environment
- **"Address in use"**: Kill existing processes on ports 3000/8000
- **"Database locked"**: Check for other processes using database

---

## 📊 Troubleshooting Statistics
- **Issues Resolved**: 500+
- **Common Problems**: Navigation, Screenshots, Version Sync
- **Critical Rules**: Never delete archives, Always check screenshots
- **Version Range**: v001 to v446+

**Quick Reference**: For urgent issues, check recent communication logs first - they contain session-specific troubleshooting info.
**Archive Safety**: Never delete archives even during troubleshooting - they contain complete project history.

---

*This guide covers common issues from 446+ versions of development experience.*
*Last Updated: 2025-08-12 | Version: 2.0*