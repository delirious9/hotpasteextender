# HotPasteExtender Distribution Design

**Date**: 2026-03-10
**Goal**: Make HotPaste distributable via Homebrew and git clone, renamed to HotPasteExtender.

## Naming

- App name: HotPasteExtender
- GitHub repo: `delirious9/hotpasteextender`
- Homebrew tap repo: `delirious9/homebrew-hotpasteextender`
- Install command: `brew tap delirious9/hotpasteextender && brew install hotpasteextender`
- LaunchAgent label: `com.hotpasteextender.app`
- Config dir: `~/.hotpaste/` (unchanged, no migration needed)

## Repo Cleanup

- Remove hardcoded paths from `com.hotpaste.app.plist` — setup script generates with user's paths
- Fix `requirements.txt` — add `pyobjc-framework-Quartz`, `pyobjc-framework-Cocoa`; remove `pynput` (replaced by CGEvent tap)
- Add `.gitignore` — `__pycache__/`, `*.pyc`, `.DS_Store`, `*.png`, `*.jpg`, `*.jpeg`
- Update `README.md` — accurate hotkeys (Ctrl+Alt+1-5), both brew and manual install instructions
- Keep `CLAUDE.md` with full debugging history for Claude Code users
- Add MIT license
- Tag `v1.0.0` after cleanup

## setup.sh (for git clone installs)

1. Check Python 3 is installed
2. `pip3 install -r requirements.txt`
3. Generate LaunchAgent plist with current user's Python path and script path
4. Copy plist to `~/Library/LaunchAgents/`
5. Load via `launchctl load`
6. Print Accessibility permissions reminder

## uninstall.sh

1. `launchctl unload ~/Library/LaunchAgents/com.hotpasteextender.app.plist`
2. Remove plist from `~/Library/LaunchAgents/`
3. Optionally remove `~/.hotpaste/` config dir

## Homebrew Tap

### Repo: `delirious9/homebrew-hotpasteextender`

Contains `Formula/hotpasteextender.rb`:
- Downloads tagged release tarball from `delirious9/hotpasteextender`
- Installs Python deps into Homebrew-managed virtualenv (`libexec`)
- Generates LaunchAgent plist with Homebrew paths
- Installs plist to `~/Library/LaunchAgents/`
- Caveats: remind about Accessibility permissions

### User experience

```bash
brew tap delirious9/hotpasteextender
brew install hotpasteextender
# Grant Accessibility in System Preferences > Privacy & Security > Accessibility
```

### Updates

Tag new release on main repo, update formula URL + SHA256, users run `brew upgrade hotpasteextender`.

## CLAUDE.md

Maintained with:
- Codebase overview and structure
- Full debugging history (CGEvent bugs, RDP quirks, failed approaches)
- How to change hotkeys, add slots, modify paste behavior
- Known gotchas (US keyboard layout, RDP clipboard sync, Mission Control conflicts)

Enables any Claude Code user to customize the app with full context.

## What does NOT work (documented for future devs)

- **Ctrl+V via CGEvent for RDP** — RDP clients strip Control modifier from synthetic events
- **Clipboard copy during RDP char-typing** — triggers RDP clipboard sync, injects stray 'v'
- **pynput GlobalHotKeys** — passive listener, doesn't suppress keystrokes (number key leaks to app)
- **Session-level CGEvent tap** — Mission Control processes shortcuts at HID level before session tap
