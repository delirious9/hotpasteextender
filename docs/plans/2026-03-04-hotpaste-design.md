# HotPaste Design

## Overview
macOS menu bar hotkey text expander. Press Ctrl+1 through Ctrl+5 to instantly paste predefined text (passwords) into any focused app.

## Decisions
- **Pasting strategy**: Clipboard-based (pyperclip.copy + simulate Cmd+V). No clipboard restore.
- **UI**: rumps only, no tkinter. Menu bar shows slots with values visible. Click to edit via rumps Window dialog.
- **Config storage**: Plain text JSON at `~/.hotpaste/config.json`. No encryption.
- **Auto-start**: LaunchAgent plist, loaded via `launchctl load`.

## Architecture

```
hotpaste/
├── main.py                 # Entry point — rumps app + hotkey listener setup
├── hotkeys.py              # pynput global listener for Ctrl+1–5
├── config.py               # Load/save ~/.hotpaste/config.json
├── requirements.txt        # rumps, pynput, pyperclip
├── README.md               # Setup, permissions, LaunchAgent
└── com.hotpaste.app.plist  # LaunchAgent for auto-start on login
```

## Flow

1. `main.py` starts rumps menu bar app (keyboard icon) and loads config.
2. Menu dropdown shows `Ctrl+1: <value>` through `Ctrl+5: <value>`, plus Quit.
3. Click a slot → rumps Window dialog → edit value → saves to JSON immediately.
4. pynput listener runs in background thread, listens for Ctrl+1–5.
5. On hotkey: read slot value → `pyperclip.copy(value)` → simulate Cmd+V via pynput Controller.

## Config Format

```json
{
  "slots": {
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": ""
  }
}
```

Default: 5 empty slots. Stored at `~/.hotpaste/config.json`.

## Dependencies
- `rumps` — menu bar app + UI dialogs
- `pynput` — global hotkey listening + Cmd+V simulation
- `pyperclip` — clipboard access

## LaunchAgent
- plist at `~/Library/LaunchAgents/com.hotpaste.app.plist`
- Points to Python interpreter + absolute path to `main.py`
- `RunAtLoad: true`

## Accessibility Permissions
- Required for pynput to listen globally and simulate keystrokes
- README will guide user to System Settings > Privacy & Security > Accessibility
