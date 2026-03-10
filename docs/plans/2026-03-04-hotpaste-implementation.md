# HotPaste Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a macOS menu bar hotkey text expander that pastes predefined text via Ctrl+1–5.

**Architecture:** rumps menu bar app with pynput global hotkey listener in a background thread. Config stored as plain JSON at `~/.hotpaste/config.json`. Clipboard-based pasting via pyperclip + simulated Cmd+V.

**Tech Stack:** Python 3, rumps, pynput, pyperclip

---

### Task 1: Project Setup & Dependencies

**Files:**
- Create: `hotpaste/requirements.txt`

**Step 1: Create requirements.txt**

```
rumps
pynput
pyperclip
```

**Step 2: Install dependencies**

Run: `pip install -r hotpaste/requirements.txt`
Expected: All packages install successfully.

**Step 3: Commit**

```bash
git init
git add hotpaste/requirements.txt
git commit -m "chore: initial project setup with dependencies"
```

---

### Task 2: Config Module

**Files:**
- Create: `hotpaste/config.py`
- Create: `hotpaste/tests/test_config.py`

**Step 1: Write the failing tests**

```python
# hotpaste/tests/test_config.py
import json
import os
import tempfile
import pytest
from config import load_config, save_config, DEFAULT_CONFIG, get_config_path

@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    config_dir = tmp_path / ".hotpaste"
    monkeypatch.setattr("config.CONFIG_DIR", str(config_dir))
    monkeypatch.setattr("config.CONFIG_PATH", str(config_dir / "config.json"))
    return config_dir

def test_default_config_has_5_empty_slots():
    assert DEFAULT_CONFIG == {"slots": {"1": "", "2": "", "3": "", "4": "", "5": ""}}

def test_load_config_creates_default_when_missing(tmp_config):
    result = load_config()
    assert result == DEFAULT_CONFIG
    assert (tmp_config / "config.json").exists()

def test_load_config_reads_existing(tmp_config):
    tmp_config.mkdir(parents=True)
    data = {"slots": {"1": "pw1", "2": "", "3": "", "4": "", "5": ""}}
    (tmp_config / "config.json").write_text(json.dumps(data))
    result = load_config()
    assert result["slots"]["1"] == "pw1"

def test_save_config_writes_json(tmp_config):
    data = {"slots": {"1": "test", "2": "", "3": "", "4": "", "5": ""}}
    save_config(data)
    written = json.loads((tmp_config / "config.json").read_text())
    assert written == data

def test_save_config_creates_dir_if_missing(tmp_config):
    data = {"slots": {"1": "", "2": "", "3": "", "4": "", "5": ""}}
    save_config(data)
    assert (tmp_config / "config.json").exists()
```

**Step 2: Run tests to verify they fail**

Run: `cd hotpaste && python -m pytest tests/test_config.py -v`
Expected: FAIL — `config` module doesn't exist yet.

**Step 3: Write the implementation**

```python
# hotpaste/config.py
import json
import os

CONFIG_DIR = os.path.expanduser("~/.hotpaste")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "slots": {
        "1": "",
        "2": "",
        "3": "",
        "4": "",
        "5": "",
    }
}


def load_config():
    """Load config from disk, creating default if missing."""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):
    """Save config to disk, creating directory if needed."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
```

**Step 4: Run tests to verify they pass**

Run: `cd hotpaste && python -m pytest tests/test_config.py -v`
Expected: All 5 tests PASS.

**Step 5: Commit**

```bash
git add hotpaste/config.py hotpaste/tests/test_config.py
git commit -m "feat: add config module with load/save and tests"
```

---

### Task 3: Hotkey Listener Module

**Files:**
- Create: `hotpaste/hotkeys.py`

**Step 1: Write the implementation**

Note: Global hotkey listening + clipboard + key simulation is inherently side-effectful and requires macOS Accessibility permissions, so unit testing is impractical. We test manually in Task 5.

```python
# hotpaste/hotkeys.py
import threading
import time
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Controller

kb_controller = Controller()

# Will be set by main.py
_get_slot_value = None


def set_slot_getter(fn):
    """Register a callback that takes a slot number (str) and returns its value."""
    global _get_slot_value
    _get_slot_value = fn


def _paste_text(text):
    """Copy text to clipboard and simulate Cmd+V."""
    if not text:
        return
    pyperclip.copy(text)
    time.sleep(0.05)
    kb_controller.press(Key.cmd)
    kb_controller.press('v')
    kb_controller.release('v')
    kb_controller.release(Key.cmd)


def _on_hotkey(slot_number):
    """Called when Ctrl+<slot_number> is pressed."""
    if _get_slot_value is None:
        return
    value = _get_slot_value(str(slot_number))
    if value:
        _paste_text(value)


def start_listener():
    """Start the global hotkey listener in a background thread."""
    hotkeys = {}
    for i in range(1, 6):
        slot = i
        hotkeys[f'<ctrl>+{i}'] = lambda s=slot: _on_hotkey(s)

    listener = keyboard.GlobalHotKeys(hotkeys)
    listener.daemon = True
    listener.start()
    return listener
```

**Step 2: Commit**

```bash
git add hotpaste/hotkeys.py
git commit -m "feat: add hotkey listener with clipboard-based pasting"
```

---

### Task 4: Main App (rumps Menu Bar)

**Files:**
- Create: `hotpaste/main.py`

**Step 1: Write the implementation**

```python
# hotpaste/main.py
import rumps
from config import load_config, save_config
from hotkeys import set_slot_getter, start_listener


class HotPasteApp(rumps.App):
    def __init__(self):
        super().__init__("HotPaste", icon=None, title="\u2328")
        self.config = load_config()
        self._build_menu()
        set_slot_getter(self._get_slot_value)
        self.listener = start_listener()

    def _build_menu(self):
        """Build menu items from current config."""
        self.menu.clear()
        for i in range(1, 6):
            slot = str(i)
            value = self.config["slots"].get(slot, "")
            display = value if value else "(empty)"
            item = rumps.MenuItem(
                f"Ctrl+{slot}: {display}",
                callback=self._make_edit_callback(slot),
            )
            self.menu.add(item)

    def _make_edit_callback(self, slot):
        """Return a callback that opens an edit dialog for the given slot."""
        def callback(sender):
            current = self.config["slots"].get(slot, "")
            response = rumps.Window(
                message=f"Enter value for Ctrl+{slot}:",
                title="Edit Slot",
                default_text=current,
                ok="Save",
                cancel="Cancel",
            ).run()
            if response.clicked:
                self.config["slots"][slot] = response.text
                save_config(self.config)
                self._build_menu()
        return callback

    def _get_slot_value(self, slot):
        """Get the current value for a slot number."""
        return self.config["slots"].get(slot, "")


if __name__ == "__main__":
    HotPasteApp().run()
```

**Step 2: Commit**

```bash
git add hotpaste/main.py
git commit -m "feat: add rumps menu bar app with slot editing"
```

---

### Task 5: Manual Integration Test

**Step 1: Run the app**

Run: `cd hotpaste && python main.py`

**Step 2: Verify menu bar**

- Keyboard icon appears in menu bar
- Click it → see 5 slots with "(empty)" values
- Click a slot → edit dialog appears
- Type a test value → click Save
- Menu updates to show the new value

**Step 3: Verify hotkeys**

- Open a text editor (e.g. TextEdit)
- Press Ctrl+1 → the saved value should be pasted
- Verify `~/.hotpaste/config.json` contains the saved value

**Step 4: If Accessibility permission prompt appears**

- Grant permission in System Settings > Privacy & Security > Accessibility
- Restart the app and retest

---

### Task 6: LaunchAgent Plist

**Files:**
- Create: `hotpaste/com.hotpaste.app.plist`

**Step 1: Write the plist**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hotpaste.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>REPLACE_WITH_ABSOLUTE_PATH/hotpaste/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/hotpaste.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/hotpaste.err</string>
</dict>
</plist>
```

**Step 2: Commit**

```bash
git add hotpaste/com.hotpaste.app.plist
git commit -m "feat: add LaunchAgent plist for auto-start on login"
```

---

### Task 7: README

**Files:**
- Create: `hotpaste/README.md`

**Step 1: Write README covering:**

- What HotPaste does
- Install dependencies: `pip install -r requirements.txt`
- Run the app: `python main.py`
- Grant Accessibility permissions (System Settings > Privacy & Security > Accessibility > add Terminal/Python)
- Install LaunchAgent:
  - Edit plist to set absolute path to `main.py`
  - `cp com.hotpaste.app.plist ~/Library/LaunchAgents/`
  - `launchctl load ~/Library/LaunchAgents/com.hotpaste.app.plist`
- Uninstall LaunchAgent:
  - `launchctl unload ~/Library/LaunchAgents/com.hotpaste.app.plist`

**Step 2: Commit**

```bash
git add hotpaste/README.md
git commit -m "docs: add README with setup and usage instructions"
```
