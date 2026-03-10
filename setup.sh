#!/bin/bash
set -e

echo "=== HotPasteExtender Setup ==="

# Check Python 3
PYTHON=$(which python3 2>/dev/null)
if [ -z "$PYTHON" ]; then
    echo "ERROR: python3 not found. Install Python 3 first."
    exit 1
fi
echo "Found Python: $PYTHON"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r hotpaste/requirements.txt

# Generate LaunchAgent plist
SCRIPT_DIR="$(cd "$(dirname "$0")/hotpaste" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/main.py"
PLIST_NAME="com.hotpasteextender.app.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Generating LaunchAgent..."
sed -e "s|__PYTHON_PATH__|$PYTHON|g" \
    -e "s|__SCRIPT_PATH__|$SCRIPT_PATH|g" \
    "hotpaste/$PLIST_NAME" > "$PLIST_DEST"

# Load LaunchAgent
echo "Loading LaunchAgent..."
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "IMPORTANT: Grant Accessibility access to Python:"
echo "  System Preferences > Privacy & Security > Accessibility"
echo "  Add: $PYTHON"
echo ""
echo "HotPasteExtender will start on login. To start now:"
echo "  cd hotpaste && python3 main.py &"
