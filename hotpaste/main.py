# hotpaste/main.py
import rumps
from config import load_config, save_config
from hotkeys import set_slot_getter, start_listener


class HotPasteApp(rumps.App):
    def __init__(self):
        super().__init__("HotPasteExtender", icon=None, title="\U0001F4CB")
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
                f"Ctrl+Alt+{slot}: {display}",
                callback=self._make_edit_callback(slot),
            )
            self.menu.add(item)

    def _make_edit_callback(self, slot):
        """Return a callback that opens an edit dialog for the given slot."""
        def callback(sender):
            current = self.config["slots"].get(slot, "")
            response = rumps.Window(
                message=f"Enter value for Ctrl+Alt+{slot}:",
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
