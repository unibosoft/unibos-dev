#!/bin/bash

# Safe version restoration script
echo "=== UNIBOS Safe Version Restoration ==="
echo "Current directory: $(pwd)"
echo "Current branch: $(git branch --show-current)"
echo ""

# Save current state
CURRENT_COMMIT=$(git rev-parse HEAD)

# Function to restore a single version
restore_version() {
    local VERSION=$1
    local COMMIT_HASH=$2
    
    echo "Processing v$VERSION (commit: $COMMIT_HASH)..."
    
    # Check if already exists
    if ls archive/versions/unibos_v${VERSION}_* 2>/dev/null | head -1 > /dev/null; then
        echo "  ✓ Archive already exists, skipping"
        return 0
    fi
    
    # Checkout the specific commit
    git checkout -q "$COMMIT_HASH" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "  ✗ Failed to checkout commit $COMMIT_HASH"
        return 1
    fi
    
    # Create archive directory
    TIMESTAMP="20250818_1200"  # Fixed timestamp for consistency
    ARCHIVE_DIR="archive/versions/unibos_v${VERSION}_${TIMESTAMP}"
    
    echo "  Creating archive at $ARCHIVE_DIR..."
    mkdir -p "$ARCHIVE_DIR"
    
    # Copy source files
    if [ -d "src" ]; then
        cp -r src "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy backend if exists
    if [ -d "backend" ]; then
        rsync -a --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
                 --exclude='node_modules' --exclude='db.sqlite3' \
                 backend "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy frontend if exists  
    if [ -d "frontend" ]; then
        rsync -a --exclude='node_modules' --exclude='build' \
                 frontend "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy projects if exists
    if [ -d "projects" ]; then
        cp -r projects "$ARCHIVE_DIR/" 2>/dev/null
    fi
    
    # Copy important root files
    for file in *.py *.sh *.md *.json *.txt; do
        if [ -f "$file" ]; then
            cp "$file" "$ARCHIVE_DIR/" 2>/dev/null
        fi
    done
    
    echo "  ✓ Successfully created archive for v$VERSION"
    return 0
}

# Restore each missing version
restore_version 468 "73253fbe"
restore_version 469 "5682c758"
restore_version 472 "3e056407"
restore_version 483 "444393e3"
restore_version 484 "3a0c3eec"
restore_version 485 "e926b820"
restore_version 487 "5b037a98"
restore_version 491 "cdb749c1"

# Return to original commit
echo ""
echo "Returning to original state..."
git checkout -q main
git reset --hard $CURRENT_COMMIT 2>/dev/null

echo ""
echo "=== Restoration Complete ==="
echo "Checking restored versions:"
for v in 468 469 472 483 484 485 487 491; do
    if ls archive/versions/unibos_v${v}_* 2>/dev/null | head -1 > /dev/null; then
        echo "  ✓ v$v restored"
    else
        echo "  ✗ v$v not found"
    fi
done

echo ""
echo "✓ No data was lost during restoration"