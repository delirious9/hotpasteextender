#!/bin/bash

echo "=== HotPasteExtender Uninstall ==="

PLIST_NAME="com.hotpasteextender.app.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

# Stop and unload LaunchAgent
if [ -f "$PLIST_PATH" ]; then
    echo "Unloading LaunchAgent..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm "$PLIST_PATH"
    echo "LaunchAgent removed."
else
    echo "No LaunchAgent found."
fi

# Kill running process
pkill -f "hotpaste/main.py" 2>/dev/null && echo "Stopped running process." || true

# Ask about config
echo ""
read -p "Remove config (~/.hotpaste/)? [y/N] " answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm -rf "$HOME/.hotpaste"
    echo "Config removed."
else
    echo "Config kept at ~/.hotpaste/"
fi

echo ""
echo "=== Uninstall Complete ==="
