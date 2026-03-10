

Build me a macOS hotkey text expander app in Python with the following specs:
Core functionality:

Runs silently in the background as a macOS menu bar app
Listens globally for hotkeys Ctrl+1 through Ctrl+5
When a hotkey is triggered, it instantly types/pastes the pre-defined text into whatever is currently focused (browser, terminal, any app)
Starts automatically on login via a macOS LaunchAgent plist

Settings UI:

Accessible by clicking the menu bar icon
Shows a small native-looking settings window where I can see all 5 slots
Each slot shows the hotkey (e.g. Ctrl+1) and an editable text field for the content
A Save button that persists the changes to a local JSON config file (~/.hotpaste/config.json)
Changes take effect immediately without restarting the app

Tech requirements:

Use pynput for global hotkey listening
Use pyautogui or pyperclip + simulated Cmd+V for pasting
Use rumps for the macOS menu bar icon and UI
Use tkinter for the settings window
All dependencies installable via pip
Must request macOS Accessibility permissions on first launch and guide the user through enabling them in System Settings (required for global hotkeys and simulated typing on macOS)

Project structure:
hotpaste/
├── main.py           # entry point
├── hotkeys.py        # hotkey listener logic
├── settings.py       # settings window UI
├── config.py         # load/save JSON config
├── config.json       # default empty config
├── requirements.txt
├── README.md         # setup instructions
└── com.hotpaste.app.plist  # LaunchAgent for auto-start on login
README must include:

How to install dependencies (pip install -r requirements.txt)
How to run the app
How to install the LaunchAgent so it auto-starts on login (launchctl load)
How to grant Accessibility permissions in System Settings

Default config should have 5 empty slots pre-defined so the user can fill them in via the settings UI on first launch. The menu bar icon should show a small clipboard or keyboard emoji as the icon.