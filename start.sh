#!/bin/bash
# ClawdForDummies Launcher for Linux/macOS
# This script launches the security scanner with proper environment setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}   CLAWD FOR DUMMIES - Security Scanner${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}ERROR: Python is not installed or not in PATH${NC}"
        echo "Please install Python 3.8 or higher from https://python.org"
        echo ""
        exit 1
    else
        PYTHON=python
    fi
else
    PYTHON=python3
fi

# Check Python version
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

# Check if version is 3.8 or higher
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}ERROR: Python 3.8 or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if we're in a virtual environment
if [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    echo -e "${YELLOW}Using virtual environment...${NC}"
    PYTHON="$PROJECT_DIR/venv/bin/python"
fi

# Install dependencies if needed
if [ ! -d "$PROJECT_DIR/clawd_for_dummies.egg-info" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    if ! $PYTHON -m pip install -e "$PROJECT_DIR" --quiet; then
        echo -e "${RED}ERROR: Failed to install dependencies${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}Starting security scan...${NC}"
echo ""

# Run the scanner
$PYTHON -m clawd_for_dummies "$@"

# Pause to see results
echo ""
echo -e "${BLUE}Scan complete. Press Enter to exit...${NC}"
read -r
