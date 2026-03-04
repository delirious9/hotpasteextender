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
