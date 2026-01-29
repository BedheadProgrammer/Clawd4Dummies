#!/bin/bash
# ClawdForDummies Launcher for macOS
# This script launches the security scanner when double-clicked

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Open Terminal and run the main script
osascript <<EOF
tell application "Terminal"
    do script "cd '$SCRIPT_DIR' && bash '$SCRIPT_DIR/start.sh'"
    activate
end tell
EOF
