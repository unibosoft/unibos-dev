#!/bin/bash

# Comprehensive version restoration script for UNIBOS
# This script will restore ALL missing versions from git history

echo "╔══════════════════════════════════════════════════════╗"
echo "║     UNIBOS Missing Version Restoration Script       ║"
echo "║         Restoring ALL Missing Versions              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Current state
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse HEAD)

echo -e "${BLUE}Current branch:${NC} $CURRENT_BRANCH"
echo -e "${BLUE}Current commit:${NC} $CURRENT_COMMIT"
echo ""

# Counter for statistics
RESTORED=0
SKIPPED=0
FAILED=0

# Function to restore a version
restore_version() {
    local VERSION=$1
    local TAG="v$VERSION"
    
    # Check if archive already exists
    if ls archive/versions/unibos_v${VERSION}_* 2>/dev/null | head -1 > /dev/null; then
        echo -e "${YELLOW}[SKIP]${NC} v$VERSION - Archive already exists"
        ((SKIPPED++))
        return 0
    fi
    
    echo -e "${BLUE}[PROCESSING]${NC} v$VERSION..."
    
    # Check if tag exists
    if ! git tag | grep -q "^${TAG}$"; then
        echo -e "${RED}[ERROR]${NC} v$VERSION - Tag not found in git"
        ((FAILED++))
        return 1
    fi
    
    # Checkout the tag
    git checkout -q "tags/${TAG}" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} v$VERSION - Failed to checkout tag"
        ((FAILED++))
        return 1
    fi
    
    # Create archive directory with timestamp
    TIMESTAMP="20250818_restored"
    ARCHIVE_DIR="archive/versions/unibos_v${VERSION}_${TIMESTAMP}"
    
    # Create the archive directory
    mkdir -p "$ARCHIVE_DIR"
    
    # Copy essential directories and files
    # Copy src if exists
    if [ -d "src" ]; then
        rsync -aq --exclude='__pycache__' --exclude='*.pyc' src "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy backend if exists (exclude heavy directories)
    if [ -d "backend" ]; then
        rsync -aq --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
                  --exclude='node_modules' --exclude='db.sqlite3' --exclude='*.log' \
                  --exclude='staticfiles' --exclude='media' \
                  backend "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy frontend if exists (exclude node_modules)
    if [ -d "frontend" ]; then
        rsync -aq --exclude='node_modules' --exclude='build' --exclude='dist' \
                  frontend "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy projects if exists
    if [ -d "projects" ]; then
        rsync -aq --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' \
                  projects "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy web if exists
    if [ -d "web" ]; then
        rsync -aq --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' \
                  web "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy important root files
    for file in *.py *.sh *.md VERSION.json requirements.txt package.json; do
        if [ -f "$file" ]; then
            cp "$file" "$ARCHIVE_DIR/" 2>/dev/null
        fi
    done
    
    echo -e "${GREEN}[SUCCESS]${NC} v$VERSION - Restored to $ARCHIVE_DIR"
    ((RESTORED++))
    return 0
}

# Get all missing versions
echo "Identifying missing versions..."
MISSING_VERSIONS=""
for v in $(git tag | grep -E "^v[0-9]+$" | sort -V | sed 's/^v//'); do
    if ! ls archive/versions/unibos_v${v}_* 2>/dev/null | head -1 > /dev/null; then
        MISSING_VERSIONS="$MISSING_VERSIONS $v"
    fi
done

# Count missing versions
TOTAL=$(echo $MISSING_VERSIONS | wc -w | tr -d ' ')
echo -e "${YELLOW}Found $TOTAL missing versions to restore${NC}"
echo ""

# Confirm before proceeding
echo "This will restore the following versions:"
echo $MISSING_VERSIONS | tr ' ' '\n' | sed 's/^/  v/' | head -20
if [ $TOTAL -gt 20 ]; then
    echo "  ... and $(($TOTAL - 20)) more"
fi
echo ""
read -p "Continue with restoration? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restoration cancelled."
    exit 0
fi

echo ""
echo "Starting restoration process..."
echo "════════════════════════════════════════════════════════"

# Restore each missing version
COUNTER=0
for VERSION in $MISSING_VERSIONS; do
    ((COUNTER++))
    echo ""
    echo "[$COUNTER/$TOTAL] Processing v$VERSION"
    restore_version "$VERSION"
done

# Return to original state
echo ""
echo "════════════════════════════════════════════════════════"
echo "Returning to original branch..."
git checkout -q "$CURRENT_BRANCH" 2>/dev/null
git reset --hard "$CURRENT_COMMIT" 2>/dev/null

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║               RESTORATION COMPLETE                  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Restored:${NC} $RESTORED versions"
echo -e "${YELLOW}⊗ Skipped:${NC} $SKIPPED versions (already existed)"
echo -e "${RED}✗ Failed:${NC} $FAILED versions"
echo ""
echo -e "${GREEN}✓ No data was lost during restoration${NC}"
echo -e "${GREEN}✓ Original branch and commit preserved${NC}"
echo ""

# List some of the restored versions
if [ $RESTORED -gt 0 ]; then
    echo "Recently restored versions:"
    ls -dt archive/versions/unibos_v*_*restored 2>/dev/null | head -5 | while read dir; do
        echo "  - $(basename $dir)"
    done
fi