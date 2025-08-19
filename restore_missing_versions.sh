#!/bin/bash

# Script to restore missing versions from git history
# Author: Claude
# Date: 2025-08-19

echo "🔍 Checking for missing versions in git history..."

# Get all version tags from git
GIT_VERSIONS=$(git tag | grep -E "^v[0-9]+$" | sed 's/v//' | sort -n)

# Get all existing archive versions
ARCHIVE_VERSIONS=$(ls archive/versions/ | grep -E "^unibos_v[0-9]+_" | sed 's/unibos_v\([0-9]*\)_.*/\1/' | sort -n | uniq)

# Find missing versions
echo "📊 Analyzing versions..."
MISSING_VERSIONS=""

for version in $GIT_VERSIONS; do
    if ! echo "$ARCHIVE_VERSIONS" | grep -q "^$version$"; then
        MISSING_VERSIONS="$MISSING_VERSIONS $version"
    fi
done

if [ -z "$MISSING_VERSIONS" ]; then
    echo "✅ No missing versions found in git tags!"
else
    echo "⚠️  Found missing versions from git tags: $MISSING_VERSIONS"
    
    for version in $MISSING_VERSIONS; do
        echo ""
        echo "🔄 Restoring version v$version from git..."
        
        # Create archive directory name with placeholder timestamp
        ARCHIVE_DIR="archive/versions/unibos_v${version}_20250819_restored"
        
        if [ -d "$ARCHIVE_DIR" ]; then
            echo "  ⚠️  Archive already exists: $ARCHIVE_DIR"
            continue
        fi
        
        # Checkout the version tag
        echo "  📥 Checking out v$version..."
        git checkout -q "v$version" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            # Create archive directory
            mkdir -p "$ARCHIVE_DIR"
            
            # Copy files (excluding .git and archive directories)
            echo "  📦 Creating archive..."
            rsync -a --exclude='.git' --exclude='archive' --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' . "$ARCHIVE_DIR/"
            
            echo "  ✅ Restored v$version to $ARCHIVE_DIR"
        else
            echo "  ❌ Failed to checkout v$version"
        fi
    done
    
    # Return to main branch
    echo ""
    echo "🔄 Returning to main branch..."
    git checkout main 2>/dev/null || git checkout master 2>/dev/null
fi

echo ""
echo "📊 Final archive status:"
echo "  Total archives: $(ls archive/versions/ | wc -l)"
echo "  Git tags: $(git tag | grep -E "^v[0-9]+$" | wc -l)"
echo ""
echo "✅ Version restoration complete!"