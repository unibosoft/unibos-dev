#!/bin/bash

# Work directory
WORK_DIR="git_work"

# Function to push single version
push_version() {
    VERSION=$1
    
    # Check if already pushed
    if git ls-remote --heads origin "$VERSION" 2>/dev/null | grep -q "$VERSION"; then
        echo "SKIP: $VERSION already exists"
        return 0
    fi
    
    # Find source directory
    SOURCE=$(ls -d archive/versions/unibos_${VERSION}_* 2>/dev/null | head -1)
    if [ -z "$SOURCE" ]; then
        echo "ERROR: $VERSION not found"
        return 1
    fi
    
    echo "Processing $VERSION..."
    
    # Remove and recreate work directory
    rm -rf "$WORK_DIR"
    mkdir "$WORK_DIR"
    cd "$WORK_DIR"
    
    # Initialize git
    git init > /dev/null 2>&1
    git remote add origin https://github.com/unibosoft/unibos_dev.git > /dev/null 2>&1
    
    # Copy all files
    cp -r "../$SOURCE"/* . 2>/dev/null || true
    cp -r "../$SOURCE"/.[^.]* . 2>/dev/null || true
    
    # Remove problematic files
    rm -f backend/.api_keys.json 2>/dev/null
    rm -rf .git 2>/dev/null
    
    # Initialize git again (was deleted from source)
    git init > /dev/null 2>&1
    git remote add origin https://github.com/unibosoft/unibos_dev.git > /dev/null 2>&1
    
    # Add, commit and push
    git add -A
    git commit -m "$VERSION archive version" > /dev/null 2>&1
    git checkout -b "$VERSION" > /dev/null 2>&1
    
    if git push -u origin "$VERSION" 2>&1 | grep -q "new branch"; then
        echo "SUCCESS: $VERSION pushed"
        cd ..
        return 0
    else
        echo "ERROR: Failed to push $VERSION"
        cd ..
        return 1
    fi
}

# Push all missing versions
for dir in archive/versions/unibos_v*/; do
    VERSION=$(basename "$dir" | sed 's/unibos_//' | cut -d'_' -f1)
    push_version "$VERSION"
    sleep 1
done

echo "All versions processed"
