#!/bin/bash
# UNIBOS Version Update Script
# Updates version information across all files

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Get Istanbul time
get_istanbul_time() {
    TZ='Europe/Istanbul' date "$1"
}

# Main function
main() {
    VERSION=$1
    DESCRIPTION=$2
    
    if [ -z "$VERSION" ]; then
        print_color "$RED" "❌ Error: Version number required!"
        print_color "$YELLOW" "Usage: ./update_version.sh vXXX \"Description\""
        exit 1
    fi
    
    # Remove 'v' prefix if present for numeric operations
    VERSION_NUM=${VERSION#v}
    
    # Get Istanbul timestamp
    TIMESTAMP=$(get_istanbul_time '+%Y%m%d_%H%M')
    RELEASE_DATE=$(get_istanbul_time '+%Y-%m-%d %H:%M:%S %z')
    DATE_ONLY=$(get_istanbul_time '+%Y-%m-%d')
    
    print_color "$CYAN" "╔══════════════════════════════════════════════════════╗"
    print_color "$CYAN" "║        UNIBOS Version Update - $VERSION              ║"
    print_color "$CYAN" "╚══════════════════════════════════════════════════════╝"
    print_color "$BLUE" "📅 Istanbul Time: $(get_istanbul_time '+%Y-%m-%d %H:%M:%S %Z')"
    print_color "$BLUE" "🏷️ Build Number: $TIMESTAMP"
    
    # Update src/VERSION.json
    print_color "$YELLOW" "\n📝 Updating src/VERSION.json..."
    if [ -f "src/VERSION.json" ]; then
        # Read existing VERSION.json and update relevant fields
        python3 -c "
import json
import sys

with open('src/VERSION.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['version'] = '$VERSION'
data['build_number'] = '$TIMESTAMP'
data['release_date'] = '$RELEASE_DATE'
if '$DESCRIPTION':
    data['description'] = '$DESCRIPTION'

with open('src/VERSION.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('✅ VERSION.json updated')
"
    else
        print_color "$RED" "❌ src/VERSION.json not found!"
    fi
    
    # Update Django login template
    print_color "$YELLOW" "\n📝 Updating Django login template..."
    LOGIN_TEMPLATE="backend/templates/web_ui/login.html"
    if [ -f "$LOGIN_TEMPLATE" ]; then
        # Update version in ASCII art
        sed -i '' "s/unibos v[0-9]*/unibos $VERSION/g" "$LOGIN_TEMPLATE"
        # Update build number
        sed -i '' "s/build [0-9]*_[0-9]*/build $TIMESTAMP/g" "$LOGIN_TEMPLATE"
        print_color "$GREEN" "✅ Login template updated"
    else
        print_color "$YELLOW" "⚠️ Login template not found, skipping..."
    fi
    
    # Update Django web_ui/views.py fallback version
    print_color "$YELLOW" "\n📝 Updating Django views.py..."
    VIEWS_FILE="backend/apps/web_ui/views.py"
    if [ -f "$VIEWS_FILE" ]; then
        # Update fallback version data
        sed -i '' "s/\"version\": \"v[0-9]*\"/\"version\": \"$VERSION\"/g" "$VIEWS_FILE"
        sed -i '' "s/\"build_number\": \"[0-9]*_[0-9]*\"/\"build_number\": \"$TIMESTAMP\"/g" "$VIEWS_FILE"
        sed -i '' "s/\"release_date\": \"[0-9]*-[0-9]*-[0-9]*\"/\"release_date\": \"$DATE_ONLY\"/g" "$VIEWS_FILE"
        print_color "$GREEN" "✅ Django views.py updated"
    else
        print_color "$YELLOW" "⚠️ Django views.py not found, skipping..."
    fi
    
    # Archive current version
    print_color "$YELLOW" "\n📦 Creating archive..."
    ARCHIVE_NAME="unibos_${VERSION}_${TIMESTAMP}"
    ARCHIVE_PATH="archive/versions/${ARCHIVE_NAME}"
    
    if [ ! -d "archive/versions" ]; then
        mkdir -p archive/versions
    fi
    
    # Create archive directory
    print_color "$YELLOW" "➤ Creating archive: $ARCHIVE_PATH"
    rsync -av --exclude='archive' --exclude='.git' --exclude='venv' \
              --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
              --exclude='db.sqlite3' --exclude='*.db' \
              . "$ARCHIVE_PATH/"
    
    # Show archive size
    ARCHIVE_SIZE=$(du -sh "$ARCHIVE_PATH" | awk '{print $1}')
    print_color "$GREEN" "✅ Archive created: $ARCHIVE_SIZE"
    
    # Restart Django server if running
    print_color "$YELLOW" "\n🔄 Restarting Django server..."
    pkill -f "python.*manage.py runserver" 2>/dev/null
    sleep 1
    DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency python backend/manage.py runserver 0.0.0.0:8000 > /tmp/django_server.log 2>&1 &
    print_color "$GREEN" "✅ Django server restarted"
    
    # Summary
    print_color "$CYAN" "\n╔══════════════════════════════════════════════════════╗"
    print_color "$CYAN" "║              Version Update Complete!                 ║"
    print_color "$CYAN" "╚══════════════════════════════════════════════════════╝"
    print_color "$GREEN" "📌 Version: $VERSION"
    print_color "$GREEN" "🏷️ Build: $TIMESTAMP"
    print_color "$GREEN" "📅 Date: $RELEASE_DATE"
    print_color "$GREEN" "📦 Archive: $ARCHIVE_NAME"
    print_color "$GREEN" "📂 Size: $ARCHIVE_SIZE"
    print_color "$CYAN" "════════════════════════════════════════════════════════"
    
    # Ask if user wants to push to git
    print_color "$YELLOW" "\n🚀 Do you want to push to git? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ./git_version_push.sh "$VERSION" "$DESCRIPTION"
    fi
}

# Run main function
main "$@"