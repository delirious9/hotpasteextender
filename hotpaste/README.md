# HotPasteExtender

macOS menu bar app for instant text pasting via global hotkeys. Store up to 5 text snippets and paste them into any app — including RDP/VNC remote sessions — with Ctrl+Alt+1 through Ctrl+Alt+5.

## Install

### Homebrew (recommended)

```bash
brew tap delirious9/hotpasteextender
brew install hotpasteextender
```

### Manual

```bash
git clone https://github.com/delirious9/hotpasteextender.git
cd hotpasteextender
./setup.sh
```

## Setup

After install, grant Accessibility access:

**System Preferences > Privacy & Security > Accessibility** — add the Python binary (shown during setup).

## Usage

- Click the 📋 icon in the menu bar to edit your 5 slots
- Press **Ctrl+Alt+1** through **Ctrl+Alt+5** to paste the corresponding slot

### How it works

- **Native macOS apps**: Copies to clipboard and simulates Cmd+V
- **RDP/VNC apps**: Types characters directly via CGEvent (clipboard is not touched to avoid sync issues)

## Uninstall

### Homebrew

```bash
brew uninstall hotpasteextender
```

### Manual

```bash
./uninstall.sh
```

## Customization

This repo includes a `CLAUDE.md` with full architecture docs and debugging history. Open the repo in [Claude Code](https://claude.ai/claude-code) to customize hotkeys, add slots, or fix issues for your specific setup.

## License

MIT
