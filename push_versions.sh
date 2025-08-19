#!/bin/bash

# Safety checks
if [ ! -d "archive/versions" ]; then
    echo "Error: archive/versions not found"
    exit 1
fi

# Create temporary git directory
TEMP_DIR="git_push_temp"
if [ ! -d "$TEMP_DIR" ]; then
    mkdir "$TEMP_DIR"
    cd "$TEMP_DIR"
    git init
    git remote add origin https://github.com/unibosoft/unibos_dev.git
else
    cd "$TEMP_DIR"
fi

# Get list of versions to push
cd ..
for dir in archive/versions/unibos_v*/; do
    version=$(basename "$dir" | sed 's/unibos_//' | cut -d'_' -f1)
    
    # Skip if no version detected
    if [ -z "$version" ]; then
        continue
    fi
    
    echo "Checking $version..."
    
    # Check if already exists on remote
    if git ls-remote --heads origin "$version" | grep -q "$version"; then
        echo "  Already exists, skipping"
        continue
    fi
    
    echo "  Processing $version..."
    
    cd "$TEMP_DIR"
    
    # Clean directory
    git rm -rf . 2>/dev/null || true
    rm -rf * .[^.]* 2>/dev/null || true
    
    # Copy version files
    cp -r "../$dir"/* . 2>/dev/null || true
    cp -r "../$dir"/.[^.]* . 2>/dev/null || true
    
    # Remove problematic files
    rm -f backend/.api_keys.json 2>/dev/null
    rm -rf .git 2>/dev/null
    
    # Commit and push
    git add -A
    git commit -m "$version archive version" || true
    git branch -D "$version" 2>/dev/null || true
    git checkout -b "$version"
    
    # Try to push
    if git push -u origin "$version" 2>&1 | tee push.log | grep -E "(error|rejected|fatal)"; then
        echo "  ERROR: Failed to push $version"
        cat push.log
    else
        echo "  SUCCESS: $version pushed"
    fi
    
    cd ..
    sleep 1
done
