# HotPaste

macOS menu bar hotkey text expander. Define up to 5 text snippets and paste them instantly with **Ctrl+1** through **Ctrl+5**.

Click the keyboard icon in the menu bar to view and edit your hotkey slots.

## Requirements

- macOS
- Python 3

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Grant Accessibility Permissions

HotPaste needs Accessibility access to listen for global hotkeys.

1. Open **System Settings > Privacy & Security > Accessibility**
2. Click the **+** button
3. Add your **Terminal** app (or the Python binary you are using)
4. Toggle it on

Without this, hotkey listening will not work.

## Install as LaunchAgent (start on login)

1. Edit `com.hotpaste.app.plist` and replace `REPLACE_WITH_ABSOLUTE_PATH` with the actual absolute path to this project directory.

2. Copy the plist to LaunchAgents:

   ```bash
   cp com.hotpaste.app.plist ~/Library/LaunchAgents/
   ```

3. Load it:

   ```bash
   launchctl load ~/Library/LaunchAgents/com.hotpaste.app.plist
   ```

## Uninstall LaunchAgent

```bash
launchctl unload ~/Library/LaunchAgents/com.hotpaste.app.plist
```
