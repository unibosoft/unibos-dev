#!/bin/bash
# Git Version Push Script - UNIBOS
# Bu script her versiyonda git push işlemlerini otomatik yapar

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if git is clean
check_git_status() {
    if [[ -n $(git status -s) ]]; then
        return 1
    else
        return 0
    fi
}

# Main function
main() {
    VERSION=$1
    DESCRIPTION=$2
    
    if [ -z "$VERSION" ]; then
        print_color "$RED" "❌ Hata: Versiyon numarası gerekli!"
        print_color "$YELLOW" "Kullanım: ./git_version_push.sh vXXX \"Açıklama\""
        exit 1
    fi
    
    print_color "$BLUE" "🚀 UNIBOS Git Version Push - $VERSION"
    print_color "$BLUE" "============================================"
    
    # Check if there are uncommitted changes
    if ! check_git_status; then
        print_color "$YELLOW" "📝 Commit edilmemiş değişiklikler var..."
        
        # Add all changes
        print_color "$YELLOW" "➤ git add -A"
        git add -A
        
        # Commit with version message
        if [ -z "$DESCRIPTION" ]; then
            DESCRIPTION="Version $VERSION updates"
        fi
        
        COMMIT_MSG="$VERSION: $DESCRIPTION

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
        
        print_color "$YELLOW" "➤ git commit"
        git commit -m "$COMMIT_MSG"
    else
        print_color "$GREEN" "✅ Git durumu temiz"
    fi
    
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    print_color "$BLUE" "📍 Mevcut branch: $CURRENT_BRANCH"
    
    # Create version branch
    print_color "$YELLOW" "➤ git checkout -b $VERSION"
    git checkout -b $VERSION 2>/dev/null || {
        print_color "$YELLOW" "⚠️ $VERSION branch'i zaten var, geçiş yapılıyor..."
        git checkout $VERSION
    }
    
    # Push version branch
    print_color "$YELLOW" "➤ git push origin $VERSION"
    git push origin $VERSION
    
    # Switch to main and push
    print_color "$YELLOW" "➤ git checkout main"
    git checkout main
    
    # Merge version branch to main (optional - comment out if not wanted)
    # print_color "$YELLOW" "➤ git merge $VERSION --no-edit"
    # git merge $VERSION --no-edit
    
    print_color "$YELLOW" "➤ git push origin main"
    git push origin main
    
    # Create tag
    print_color "$YELLOW" "➤ git tag $VERSION"
    git tag $VERSION 2>/dev/null || print_color "$YELLOW" "ℹ️ Tag $VERSION zaten var"
    
    print_color "$YELLOW" "➤ git push origin --tags"
    git push origin --tags
    
    # Summary
    print_color "$GREEN" "============================================"
    print_color "$GREEN" "✅ Git push işlemleri tamamlandı!"
    print_color "$GREEN" "📌 Version: $VERSION"
    print_color "$GREEN" "🌿 Branch'ler: main, $VERSION"
    print_color "$GREEN" "🏷️ Tag: $VERSION"
    print_color "$GREEN" "============================================"
    
    # Show remote URLs
    print_color "$BLUE" "📡 Remote URL:"
    git remote -v | head -1
    
    # Show last commit
    print_color "$BLUE" "📝 Son commit:"
    git log --oneline -1
}

# Run main function
main "$@"