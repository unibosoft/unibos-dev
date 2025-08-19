#!/bin/bash

# UNIBOS Development Log Entry Adder
# Usage: ./add_dev_log.sh "Category" "Title" "Details"

LOG_FILE="DEVELOPMENT_LOG.md"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get current time in Istanbul timezone
TIMESTAMP=$(TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M')

# Interactive mode if no arguments
if [ $# -eq 0 ]; then
    echo -e "${CYAN}=== Add Development Log Entry ===${NC}"
    echo
    
    echo -e "${YELLOW}Categories:${NC}"
    echo "  1) Version Manager"
    echo "  2) UI/UX"
    echo "  3) Modules"
    echo "  4) Navigation"
    echo "  5) Backend"
    echo "  6) Bug Fix"
    echo "  7) Performance"
    echo "  8) Archive System"
    echo "  9) Other"
    
    echo -e "\n${YELLOW}Select category (1-9):${NC} "
    read -r cat_choice
    
    case $cat_choice in
        1) CATEGORY="Version Manager" ;;
        2) CATEGORY="UI/UX" ;;
        3) CATEGORY="Modules" ;;
        4) CATEGORY="Navigation" ;;
        5) CATEGORY="Backend" ;;
        6) CATEGORY="Bug Fix" ;;
        7) CATEGORY="Performance" ;;
        8) CATEGORY="Archive System" ;;
        9) CATEGORY="Other" ;;
        *) CATEGORY="Development" ;;
    esac
    
    echo -e "${YELLOW}Enter title (brief description):${NC} "
    read -r TITLE
    
    echo -e "${YELLOW}Enter details (what was done and why):${NC} "
    read -r DETAILS
    
    echo -e "${YELLOW}Enter result/impact:${NC} "
    read -r RESULT
else
    CATEGORY=$1
    TITLE=$2
    DETAILS=$3
    RESULT=${4:-""}
fi

# Create log entry
ENTRY="## [$TIMESTAMP] $CATEGORY: $TITLE
- $DETAILS"

if [ -n "$RESULT" ]; then
    ENTRY="$ENTRY
- Result: $RESULT"
fi

ENTRY="$ENTRY

"

# Append to log file
echo "$ENTRY" >> "$LOG_FILE"

echo -e "${GREEN}✅ Development log entry added successfully!${NC}"
echo -e "${CYAN}Category:${NC} $CATEGORY"
echo -e "${CYAN}Title:${NC} $TITLE"
echo -e "${CYAN}Time:${NC} $TIMESTAMP"