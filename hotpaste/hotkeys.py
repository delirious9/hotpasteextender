# hotpaste/hotkeys.py
import time
import os
import threading
import pyperclip
from AppKit import NSWorkspace
from Quartz import (
    CGEventSourceFlagsState, kCGEventSourceStateHIDSystemState,
    CGEventCreateKeyboardEvent, CGEventSetFlags, CGEventGetFlags, CGEventPost,
    CGEventSourceCreate, kCGEventSourceStatePrivate,
    kCGHIDEventTap, kCGEventFlagMaskCommand, kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
    # CGEvent tap for hotkey interception
    CGEventTapCreate, kCGSessionEventTap, kCGHeadInsertEventTap,
    kCGEventTapOptionDefault, CGEventTapEnable,
    CGEventMaskBit, kCGEventKeyDown, kCGEventKeyUp,
    CGEventGetIntegerValueField, kCGKeyboardEventKeycode,
    kCGEventFlagMaskAlternate,
    CFMachPortCreateRunLoopSource, CFRunLoopGetCurrent,
    CFRunLoopAddSource, kCFRunLoopCommonModes, CFRunLoopRun,
)

# Dedicated event source for synthetic events (more reliable than None)
_event_source = CGEventSourceCreate(kCGEventSourceStatePrivate)

# Will be set by main.py
_get_slot_value = None

# macOS virtual keycodes
_KEYCODE_V = 9

# Map keycodes for number keys 1-5 to slot numbers
_HOTKEY_KEYCODES = {18: 1, 19: 2, 20: 3, 21: 4, 23: 5}

# Bundle IDs where Ctrl+V should be used instead of Cmd+V
_CTRL_V_APPS = {
    "com.microsoft.rdc.macos",      # Windows App / Microsoft Remote Desktop
    "com.microsoft.rdc.osx",        # Older Microsoft Remote Desktop
    "com.citrix.XenAppViewer",      # Citrix
    "com.citrix.receiver.icaviewer.mac",
    "com.vmware.horizon",           # VMware Horizon
    "com.realvnc.vncviewer",        # RealVNC
}

_LOG_FILE = os.path.expanduser("~/.hotpaste/debug.log")


def _log(msg):
    """Append a debug line to the log file."""
    try:
        with open(_LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    except Exception:
        pass


def _get_frontmost_bundle_id():
    """Return the bundle ID of the frontmost application."""
    try:
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        return app.bundleIdentifier() or ""
    except Exception:
        return ""


def _should_use_ctrl_v(bundle_id):
    """Check if the frontmost app needs Ctrl+V instead of Cmd+V."""
    if bundle_id in _CTRL_V_APPS:
        return True
    lower = bundle_id.lower()
    return any(kw in lower for kw in ("rdc", "rdp", "citrix", "vmware", "vnc"))


def _wait_for_modifiers_released(timeout=1.0):
    """Wait until all physical modifier keys are released."""
    start = time.time()
    while time.time() - start < timeout:
        flags = CGEventSourceFlagsState(kCGEventSourceStateHIDSystemState)
        if (flags & 0xFF0000) == 0:
            return True
        time.sleep(0.01)
    return False


def _paste_via_cgevent(use_ctrl):
    """Simulate Cmd+V or Ctrl+V using low-level CGEvents."""
    flag = kCGEventFlagMaskControl if use_ctrl else kCGEventFlagMaskCommand
    event_down = CGEventCreateKeyboardEvent(_event_source, _KEYCODE_V, True)
    CGEventSetFlags(event_down, CGEventGetFlags(event_down) | flag)
    event_up = CGEventCreateKeyboardEvent(_event_source, _KEYCODE_V, False)
    CGEventSetFlags(event_up, CGEventGetFlags(event_up) | flag)
    CGEventPost(kCGHIDEventTap, event_down)
    time.sleep(0.05)
    CGEventPost(kCGHIDEventTap, event_up)


# macOS virtual keycodes for US keyboard layout
_KEYCODE_MAP = {
    'a': 0, 'b': 11, 'c': 8, 'd': 2, 'e': 14, 'f': 3, 'g': 5, 'h': 4,
    'i': 34, 'j': 38, 'k': 40, 'l': 37, 'm': 46, 'n': 45, 'o': 31, 'p': 35,
    'q': 12, 'r': 15, 's': 1, 't': 17, 'u': 32, 'v': 9, 'w': 13, 'x': 7,
    'y': 16, 'z': 6,
    '0': 29, '1': 18, '2': 19, '3': 20, '4': 21, '5': 23, '6': 22,
    '7': 26, '8': 28, '9': 25,
    ' ': 49, '-': 27, '=': 24, '[': 33, ']': 30, '\\': 42, ';': 41,
    "'": 39, '`': 50, ',': 43, '.': 47, '/': 44, '\t': 48, '\n': 36,
}

# Characters that require Shift + their base key
_SHIFT_MAP = {
    '!': 18, '@': 19, '#': 20, '$': 21, '%': 23, '^': 22, '&': 26,
    '*': 28, '(': 25, ')': 29, '_': 27, '+': 24, '{': 33, '}': 30,
    '|': 42, ':': 41, '"': 39, '~': 50, '<': 43, '>': 47, '?': 44,
}

# macOS virtual keycode for left Shift key
_KEYCODE_SHIFT = 56


def _type_char_cgevent(char):
    """Type a single character using CGEvent with proper keycode and Shift."""
    needs_shift = False

    if char in _KEYCODE_MAP:
        keycode = _KEYCODE_MAP[char]
    elif char in _SHIFT_MAP:
        keycode = _SHIFT_MAP[char]
        needs_shift = True
    elif char.lower() in _KEYCODE_MAP:
        keycode = _KEYCODE_MAP[char.lower()]
        needs_shift = True
    else:
        _log(f"no keycode for char: {repr(char)}")
        return

    if needs_shift:
        shift_down = CGEventCreateKeyboardEvent(_event_source, _KEYCODE_SHIFT, True)
        CGEventPost(kCGHIDEventTap, shift_down)
        time.sleep(0.04)

    event_down = CGEventCreateKeyboardEvent(_event_source, keycode, True)
    if needs_shift:
        CGEventSetFlags(event_down, CGEventGetFlags(event_down) | kCGEventFlagMaskShift)
    CGEventPost(kCGHIDEventTap, event_down)
    time.sleep(0.02)
    event_up = CGEventCreateKeyboardEvent(_event_source, keycode, False)
    if needs_shift:
        CGEventSetFlags(event_up, CGEventGetFlags(event_up) | kCGEventFlagMaskShift)
    CGEventPost(kCGHIDEventTap, event_up)

    if needs_shift:
        time.sleep(0.04)
        shift_up = CGEventCreateKeyboardEvent(_event_source, _KEYCODE_SHIFT, False)
        CGEventPost(kCGHIDEventTap, shift_up)


def _type_characters(text):
    """Type text character-by-character using CGEvents with proper keycodes."""
    for char in text:
        _type_char_cgevent(char)
        time.sleep(0.03)


def set_slot_getter(fn):
    """Register a callback that takes a slot number (str) and returns its value."""
    global _get_slot_value
    _get_slot_value = fn


def _paste_text(text):
    """Copy text to clipboard and paste using the appropriate method."""
    if not text:
        return

    bundle_id = _get_frontmost_bundle_id()
    use_ctrl = _should_use_ctrl_v(bundle_id)
    _log(f"hotkey fired | app={bundle_id} | use_ctrl={use_ctrl} | text={text[:30]}")

    # Wait for user to physically release all modifier keys
    released = _wait_for_modifiers_released()
    _log(f"modifiers released={released}")
    time.sleep(0.05)

    if use_ctrl:
        # RDP/VNC apps: type characters directly (CGEvent modifier flags
        # get stripped by RDP clients, so Ctrl+V doesn't work).
        # Do NOT copy to clipboard here — RDP clipboard sync would inject
        # a stray 'v' (from a mangled Ctrl+V) mid-typing.
        _type_characters(text)
        _log("typed characters directly for RDP")
    else:
        # Native Mac apps: copy to clipboard then Cmd+V paste
        pyperclip.copy(text)
        _paste_via_cgevent(use_ctrl=False)
        _log("sent CGEvent Cmd+V")


def _on_hotkey(slot_number):
    """Called when Ctrl+Alt+<slot_number> is pressed."""
    if _get_slot_value is None:
        return
    value = _get_slot_value(str(slot_number))
    if value:
        _paste_text(value)


# Track suppressed key-downs so we also suppress their matching key-ups
_suppressed_keycodes = set()


def _event_tap_callback(proxy, event_type, event, refcon):
    """CGEvent tap callback — intercepts Ctrl+Alt+1-5 and suppresses them."""
    keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)

    # Suppress key-up for any key whose key-down we already suppressed
    if event_type == kCGEventKeyUp:
        if keycode in _suppressed_keycodes:
            _suppressed_keycodes.discard(keycode)
            return None
        return event

    # Key-down: check for Ctrl+Alt+1-5
    flags = CGEventGetFlags(event)
    has_ctrl = bool(flags & kCGEventFlagMaskControl)
    has_alt = bool(flags & kCGEventFlagMaskAlternate)

    if not (has_ctrl and has_alt):
        return event  # not our combo, pass through

    if keycode in _HOTKEY_KEYCODES:
        slot = _HOTKEY_KEYCODES[keycode]
        _suppressed_keycodes.add(keycode)
        _log(f"tap: suppressed Ctrl+Alt+{slot} (keycode={keycode})")
        # Fire hotkey handler in a separate thread so we don't block the tap
        threading.Thread(target=_on_hotkey, args=(slot,), daemon=True).start()
        return None  # suppress the event — prevents '1' from reaching the app

    return event  # other key with Ctrl+Alt, pass through


def start_listener():
    """Start a CGEvent tap that intercepts Ctrl+Alt+1-5 hotkeys."""
    tap = CGEventTapCreate(
        kCGHIDEventTap,                  # HID level: before system shortcuts
        kCGHeadInsertEventTap,
        kCGEventTapOptionDefault,        # active tap: can suppress events
        CGEventMaskBit(kCGEventKeyDown) | CGEventMaskBit(kCGEventKeyUp),
        _event_tap_callback,
        None,
    )
    if tap is None:
        _log("ERROR: failed to create CGEvent tap — check Accessibility permissions")
        return None

    source = CFMachPortCreateRunLoopSource(None, tap, 0)

    def _run_tap():
        loop = CFRunLoopGetCurrent()
        CFRunLoopAddSource(loop, source, kCFRunLoopCommonModes)
        CGEventTapEnable(tap, True)
        _log("CGEvent tap started")
        CFRunLoopRun()

    thread = threading.Thread(target=_run_tap, daemon=True)
    thread.start()
    return thread
