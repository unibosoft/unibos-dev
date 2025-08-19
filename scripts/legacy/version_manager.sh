#!/bin/bash
# UNIBOS Complete Version Manager
# All-in-one script for version updates, archiving, and git operations
# Author: Berk Hatırlı

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print section headers
print_header() {
    print_color "$CYAN" "╔══════════════════════════════════════════════════════════════╗"
    print_color "$CYAN" "║$(printf "%-62s" " $1")║"
    print_color "$CYAN" "╚══════════════════════════════════════════════════════════════╝"
}

# Get Istanbul time
get_istanbul_time() {
    TZ='Europe/Istanbul' date "$1"
}

# Check if git is clean
check_git_status() {
    if [[ -n $(git status -s) ]]; then
        return 1
    else
        return 0
    fi
}

# Update VERSION.json
update_version_json() {
    local version=$1
    local timestamp=$2
    local release_date=$3
    local description=$4
    
    python3 -c "
import json
import sys

try:
    with open('src/VERSION.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['version'] = '$version'
    data['build_number'] = '$timestamp'
    data['release_date'] = '$release_date'
    data['author'] = 'berk hatırlı'
    data['location'] = 'bitez, bodrum, muğla, türkiye, dünya, güneş sistemi, samanyolu, yerel galaksi grubu, evren'
    
    if '$description':
        data['description'] = '$description'
    
    with open('src/VERSION.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print('✅ VERSION.json updated successfully')
except Exception as e:
    print(f'❌ Error updating VERSION.json: {e}')
    sys.exit(1)
"
}

# Update Django files
update_django_files() {
    local version=$1
    local timestamp=$2
    local date_only=$3
    
    # Update login template
    LOGIN_TEMPLATE="backend/templates/web_ui/login.html"
    if [ -f "$LOGIN_TEMPLATE" ]; then
        sed -i '' "s/unibos v[0-9]*/unibos $version/g" "$LOGIN_TEMPLATE"
        sed -i '' "s/build [0-9]*_[0-9]*/build $timestamp/g" "$LOGIN_TEMPLATE"
        print_color "$GREEN" "  ✓ Login template updated"
    fi
    
    # Update Django views.py fallback
    VIEWS_FILE="backend/apps/web_ui/views.py"
    if [ -f "$VIEWS_FILE" ]; then
        sed -i '' "s/\"version\": \"v[0-9]*\"/\"version\": \"$version\"/g" "$VIEWS_FILE"
        sed -i '' "s/\"build_number\": \"[0-9]*_[0-9]*\"/\"build_number\": \"$timestamp\"/g" "$VIEWS_FILE"
        sed -i '' "s/\"release_date\": \"[0-9]*-[0-9]*-[0-9]*\"/\"release_date\": \"$date_only\"/g" "$VIEWS_FILE"
        print_color "$GREEN" "  ✓ Django views.py updated"
    fi
}

# Create archive
create_archive() {
    local version=$1
    local timestamp=$2
    
    ARCHIVE_NAME="unibos_${version}_${timestamp}"
    ARCHIVE_PATH="archive/versions/${ARCHIVE_NAME}"
    
    # Create directories if not exist
    [ ! -d "archive/versions" ] && mkdir -p archive/versions
    
    # Create archive
    print_color "$YELLOW" "  Creating archive: $ARCHIVE_PATH"
    rsync -av --exclude='archive' --exclude='.git' --exclude='venv' \
              --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
              --exclude='db.sqlite3' --exclude='*.db' --exclude='node_modules' \
              --exclude='.env' --exclude='*.log' \
              . "$ARCHIVE_PATH/" > /dev/null 2>&1
    
    # Get archive folder size
    ARCHIVE_SIZE=$(du -sh "$ARCHIVE_PATH" | awk '{print $1}')
    print_color "$GREEN" "  ✓ Archive created: $ARCHIVE_SIZE"
    
    return 0
}

# Git operations
perform_git_operations() {
    local version=$1
    local description=$2
    
    print_header "GIT OPERATIONS"
    
    # Check for uncommitted changes
    if ! check_git_status; then
        print_color "$YELLOW" "📝 Committing changes..."
        
        # Add all changes
        git add -A
        
        # Create commit message
        if [ -z "$description" ]; then
            description="Version $version updates"
        fi
        
        COMMIT_MSG="$version: $description

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
        
        git commit -m "$COMMIT_MSG" > /dev/null 2>&1
        print_color "$GREEN" "  ✓ Changes committed"
    else
        print_color "$GREEN" "  ✓ Git status clean"
    fi
    
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    print_color "$BLUE" "  📍 Current branch: $CURRENT_BRANCH"
    
    # Create and push version branch
    print_color "$YELLOW" "  Creating version branch..."
    git checkout -b "$version" 2>/dev/null || git checkout "$version"
    git push origin "$version" > /dev/null 2>&1
    print_color "$GREEN" "  ✓ Branch $version pushed"
    
    # Switch to main and push
    git checkout main > /dev/null 2>&1
    git push origin main > /dev/null 2>&1
    print_color "$GREEN" "  ✓ Main branch updated"
    
    # Create and push tag
    git tag "$version" 2>/dev/null
    git push origin --tags > /dev/null 2>&1
    print_color "$GREEN" "  ✓ Tag $version created and pushed"
}

# Restart Django server
restart_django_server() {
    print_color "$YELLOW" "  Stopping existing server..."
    pkill -f "python.*manage.py runserver" 2>/dev/null
    sleep 1
    
    print_color "$YELLOW" "  Starting Django server..."
    cd backend && \
    DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency \
    python manage.py runserver 0.0.0.0:8000 > /tmp/django_server.log 2>&1 & \
    cd ..
    
    sleep 2
    if pgrep -f "python.*manage.py runserver" > /dev/null; then
        print_color "$GREEN" "  ✓ Django server running on port 8000"
    else
        print_color "$RED" "  ✗ Failed to start Django server"
    fi
}

# Main function
main() {
    VERSION=$1
    DESCRIPTION=$2
    
    # Validate version format
    if [ -z "$VERSION" ]; then
        print_color "$RED" "❌ Error: Version number required!"
        print_color "$YELLOW" "Usage: ./version_manager.sh vXXX \"Description\""
        print_color "$YELLOW" "Example: ./version_manager.sh v433 \"Added new features\""
        exit 1
    fi
    
    # Ensure version starts with 'v'
    if [[ ! "$VERSION" =~ ^v ]]; then
        VERSION="v$VERSION"
    fi
    
    # Get Istanbul timestamp and dates
    TIMESTAMP=$(get_istanbul_time '+%Y%m%d_%H%M')
    RELEASE_DATE=$(get_istanbul_time '+%Y-%m-%d %H:%M:%S %z')
    DATE_ONLY=$(get_istanbul_time '+%Y-%m-%d')
    TIME_ONLY=$(get_istanbul_time '+%H:%M:%S')
    
    # Print header
    clear
    print_header "UNIBOS VERSION MANAGER"
    print_color "$MAGENTA" "  📌 Version: $VERSION"
    print_color "$MAGENTA" "  🏷️ Build: $TIMESTAMP"
    print_color "$MAGENTA" "  📅 Istanbul Time: $DATE_ONLY $TIME_ONLY"
    print_color "$MAGENTA" "  📝 Description: ${DESCRIPTION:-'Version update'}"
    echo
    
    # Step 1: Update version files
    print_header "UPDATING VERSION FILES"
    update_version_json "$VERSION" "$TIMESTAMP" "$RELEASE_DATE" "$DESCRIPTION"
    update_django_files "$VERSION" "$TIMESTAMP" "$DATE_ONLY"
    echo
    
    # Step 2: Create archive
    print_header "CREATING ARCHIVE"
    if create_archive "$VERSION" "$TIMESTAMP"; then
        print_color "$GREEN" "  ✓ Archive created successfully"
    else
        print_color "$RED" "  ✗ Archive creation failed"
    fi
    echo
    
    # Step 3: Git operations
    perform_git_operations "$VERSION" "$DESCRIPTION"
    echo
    
    # Step 4: Restart Django server
    print_header "DJANGO SERVER"
    restart_django_server
    echo
    
    # Summary
    print_header "VERSION UPDATE COMPLETE"
    print_color "$GREEN" "  ✅ Version: $VERSION"
    print_color "$GREEN" "  ✅ Build: $TIMESTAMP"
    print_color "$GREEN" "  ✅ Archive: unibos_${VERSION}_${TIMESTAMP}"
    print_color "$GREEN" "  ✅ Git Branch: $VERSION"
    print_color "$GREEN" "  ✅ Git Tag: $VERSION"
    print_color "$GREEN" "  ✅ Django: Running on http://localhost:8000"
    echo
    print_color "$CYAN" "  🚀 All operations completed successfully!"
    print_color "$CYAN" "════════════════════════════════════════════════════════════════"
    
    # Show git log
    echo
    print_color "$BLUE" "📝 Latest commits:"
    git log --oneline -3
    
    # Show remote URL
    echo
    print_color "$BLUE" "📡 Remote repository:"
    git remote -v | head -1
}

# Run main function
main "$@"