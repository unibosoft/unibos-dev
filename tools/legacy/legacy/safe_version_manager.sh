#!/bin/bash

# UNIBOS Safe Version Manager
# Prevents version number conflicts and ensures sequential versioning

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get current version from VERSION.json
get_current_version() {
    if [ -f "src/VERSION.json" ]; then
        grep '"version"' src/VERSION.json | head -1 | sed 's/.*"v\([0-9]*\)".*/\1/'
    else
        echo "0"
    fi
}

# Get highest version from git tags
get_highest_git_version() {
    git tag | grep "^v[0-9]" | sed 's/^v//' | sort -n | tail -1
}

# Check if version exists in git tags
version_exists() {
    local version=$1
    git tag | grep -q "^v${version}$"
}

# Calculate next safe version
calculate_next_version() {
    local current_json=$(get_current_version)
    local highest_git=$(get_highest_git_version)
    
    # Get the highest number between VERSION.json and git tags
    local highest=$current_json
    if [ "$highest_git" -gt "$current_json" ] 2>/dev/null; then
        highest=$highest_git
    fi
    
    # Next version is highest + 1
    echo $((highest + 1))
}

# Main function
main() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║        UNIBOS Safe Version Manager                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
    
    # Check current state
    echo -e "\n${BLUE}📊 Current Version Status:${NC}"
    
    current_json=$(get_current_version)
    highest_git=$(get_highest_git_version)
    
    echo -e "   VERSION.json: ${YELLOW}v${current_json}${NC}"
    echo -e "   Highest Git Tag: ${YELLOW}v${highest_git}${NC}"
    
    # Check for version conflicts
    if [ "$current_json" != "$highest_git" ]; then
        echo -e "\n${YELLOW}⚠️  Version mismatch detected!${NC}"
        echo -e "   VERSION.json and git tags are out of sync."
    fi
    
    # List recent versions
    echo -e "\n${BLUE}📝 Recent Versions:${NC}"
    git tag | grep "^v[0-9]" | sort -V | tail -5 | while read tag; do
        echo -e "   $tag"
    done
    
    # Check for gaps in versioning
    echo -e "\n${BLUE}🔍 Checking for version gaps:${NC}"
    last_version=$((highest_git - 10))
    if [ $last_version -lt 1 ]; then
        last_version=1
    fi
    
    gaps_found=false
    for ((i=last_version; i<=highest_git; i++)); do
        if ! version_exists "$i"; then
            echo -e "   ${RED}Missing: v${i}${NC}"
            gaps_found=true
        fi
    done
    
    if [ "$gaps_found" = false ]; then
        echo -e "   ${GREEN}✓ No gaps found${NC}"
    fi
    
    # Calculate next version
    next_version=$(calculate_next_version)
    echo -e "\n${GREEN}✅ Next safe version: v${next_version}${NC}"
    
    # Ask user to proceed
    echo -e "\n${YELLOW}Do you want to create version v${next_version}? (y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "\n${BLUE}Enter commit message:${NC}"
        read -r commit_message
        
        if [ -z "$commit_message" ]; then
            echo -e "${RED}❌ Commit message cannot be empty${NC}"
            exit 1
        fi
        
        # Use the git_version_push.sh script with the safe version
        echo -e "\n${CYAN}Creating version v${next_version}...${NC}"
        ./git_version_push.sh "v${next_version}" "$commit_message"
        
        echo -e "\n${GREEN}✅ Version v${next_version} created successfully!${NC}"
    else
        echo -e "${YELLOW}Operation cancelled.${NC}"
    fi
}

# Check if we're in the right directory
if [ ! -f "unibos.sh" ]; then
    echo -e "${RED}❌ Error: Must run from UNIBOS root directory${NC}"
    exit 1
fi

# Run main function
main