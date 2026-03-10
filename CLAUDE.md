## Codebase Overview

HotPasteExtender is a macOS menu bar app (Python/rumps) that lets users store 5 text snippets and paste them into any app via Ctrl+Alt+1–5 hotkeys, with special RDP/VNC support using low-level Quartz CGEvent injection.

**Stack**: Python 3.11, rumps (menu bar), pynput (hotkeys), pyperclip (clipboard), Quartz/AppKit (macOS APIs)
**Structure**: `hotpaste/main.py` (entry point + UI) → `config.py` (JSON I/O) → `hotkeys.py` (listener + paste engine)
**Menu bar icon**: 📋 (clipboard emoji)

For detailed architecture, see [docs/CODEBASE_MAP.md](docs/CODEBASE_MAP.md).

## Critical Debugging History (2026-03-10)

### CGEvent bugs found and fixed in `hotkeys.py`:

1. **`CGEventSetFlags` was stripping system flags** — `CGEventSetFlags(evt, flag)` replaces ALL flags. Fixed to `CGEventSetFlags(evt, CGEventGetFlags(evt) | flag)` to preserve `NX_NONCOALESCED` and other system markers that apps need.

2. **`None` event source** — `CGEventCreateKeyboardEvent(None, ...)` is unreliable. Fixed by creating a dedicated `CGEventSourceCreate(kCGEventSourceStatePrivate)` event source.

3. **Zero delay between keydown/keyup in `_paste_via_cgevent`** — apps ignored zero-duration keypresses. Added 50ms gap.

4. **RDP clipboard sync caused phantom 'v' character** — `pyperclip.copy(text)` triggered RDP clipboard redirection, which sent a mangled Ctrl+V (stripped to just 'v') into the VM mid-typing. **Fix**: clipboard is only used for native macOS Cmd+V path; RDP char-typing path never touches the clipboard.

5. **Character typing timing too aggressive for RDP** — 8ms inter-char delay caused dropped keystrokes over network. Increased to 30ms between chars, 40ms for shift key delays, 20ms keydown-keyup gap.

6. **Shift flag missing on character events** — shift key was sent as separate event but the character event itself lacked `kCGEventFlagMaskShift`, confusing some apps. Now sets shift flag on both the shift key event AND the character event.

### What does NOT work for RDP:

- **Ctrl+V via CGEvent** — RDP clients strip the Control modifier flag from synthetic CGEvents, resulting in just 'v' being typed. Do not attempt this approach again.
- **Clipboard-based paste for RDP** — Even copying to clipboard without sending Ctrl+V causes problems because RDP clipboard redirection auto-syncs and injects stray characters.

### What works:

- **Native macOS apps**: `pyperclip.copy()` + CGEvent Cmd+V (with preserved system flags, proper event source, keydown-keyup delay)
- **RDP/VNC apps**: Character-by-character CGEvent typing (no clipboard involvement, proper event source, shift flags on char events, relaxed timing)

## Removed dead code

- `pynput.keyboard.Controller` — was imported and instantiated but never used (replaced by CGEvent functions)
