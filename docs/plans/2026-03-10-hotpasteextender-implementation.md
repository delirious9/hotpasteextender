# HotPasteExtender Distribution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Clean up the HotPaste repo for public release as HotPasteExtender, distributable via Homebrew tap and git clone.

**Architecture:** The main repo `delirious9/hotpasteextender` holds the app source, setup/uninstall scripts, and docs. A separate repo `delirious9/homebrew-hotpasteextender` holds the Homebrew formula. The plist is a template — `setup.sh` generates the real one with user-specific paths at install time.

**Tech Stack:** Python 3, rumps, pyperclip, pyobjc (Quartz/AppKit), Homebrew Ruby formula, bash scripts.

---

### Task 1: Add .gitignore

**Files:**
- Create: `.gitignore`

**Step 1: Create .gitignore**

```
__pycache__/
*.pyc
*.pyo
.DS_Store
*.png
*.jpg
*.jpeg
.pytest_cache/
*.egg-info/
dist/
build/
```

**Step 2: Remove cached tracked files that match gitignore**

Run: `git rm -r --cached hotpaste/__pycache__ hotpaste/tests/__pycache__ 2>/dev/null; git rm --cached .DS_Store hotpaste/.DS_Store 2>/dev/null; echo "done"`

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore for pycache, DS_Store, images"
```

---

### Task 2: Fix requirements.txt

**Files:**
- Modify: `hotpaste/requirements.txt`

**Step 1: Update requirements**

Replace contents with:

```
rumps
pyperclip
pyobjc-framework-Quartz
pyobjc-framework-Cocoa
```

Note: `pynput` removed (replaced by CGEvent tap). `pyobjc-framework-Cocoa` provides `AppKit`.

**Step 2: Verify imports still work**

Run: `cd hotpaste && python3 -c "import hotkeys; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add hotpaste/requirements.txt
git commit -m "fix: update requirements — add pyobjc deps, remove unused pynput"
```

---

### Task 3: Rename plist to template

**Files:**
- Rename: `hotpaste/com.hotpaste.app.plist` -> `hotpaste/com.hotpasteextender.app.plist`
- Modify contents to be a template with placeholders

**Step 1: Delete old plist from git**

Run: `git rm hotpaste/com.hotpaste.app.plist`

**Step 2: Create new template plist**

Create `hotpaste/com.hotpasteextender.app.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hotpasteextender.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>__PYTHON_PATH__</string>
        <string>__SCRIPT_PATH__</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/hotpasteextender.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/hotpasteextender.err</string>
</dict>
</plist>
```

**Step 3: Commit**

```bash
git add hotpaste/com.hotpasteextender.app.plist
git commit -m "chore: rename plist to hotpasteextender, use path placeholders"
```

---

### Task 4: Rename app references in source code

**Files:**
- Modify: `hotpaste/main.py:9` — app name `"HotPaste"` -> `"HotPasteExtender"`

**Step 1: Update main.py**

Change line 9:
```python
super().__init__("HotPasteExtender", icon=None, title="\U0001F4CB")
```

**Step 2: Verify app still starts**

Run: `cd hotpaste && python3 -c "from main import HotPasteApp; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add hotpaste/main.py
git commit -m "chore: rename app to HotPasteExtender"
```

---

### Task 5: Commit current hotkeys.py changes

The CGEvent tap rewrite and all bug fixes in `hotkeys.py` are uncommitted.

**Files:**
- Modify: `hotpaste/hotkeys.py` (already modified, just needs commit)

**Step 1: Commit**

```bash
git add hotpaste/hotkeys.py
git commit -m "fix: replace pynput with CGEvent tap, fix event flags and RDP paste bugs

- Use dedicated CGEventSource instead of None
- Preserve system flags in CGEventSetFlags (fix stripped NX_NONCOALESCED)
- Add keydown-keyup delay in paste events
- RDP: char-by-char typing without clipboard (avoids phantom 'v')
- RDP: relaxed timing (30ms inter-char, 40ms shift delay)
- RDP: set shift flag on character events
- Replace pynput GlobalHotKeys with HID-level CGEvent tap
- CGEvent tap suppresses hotkey keystrokes (prevents leaked number key)
- Suppress both key-down and key-up for hotkey keys"
```

---

### Task 6: Create setup.sh

**Files:**
- Create: `setup.sh`

**Step 1: Write setup script**

```bash
#!/bin/bash
set -e

echo "=== HotPasteExtender Setup ==="

# Check Python 3
PYTHON=$(which python3 2>/dev/null)
if [ -z "$PYTHON" ]; then
    echo "ERROR: python3 not found. Install Python 3 first."
    exit 1
fi
echo "Found Python: $PYTHON"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r hotpaste/requirements.txt

# Generate LaunchAgent plist
SCRIPT_DIR="$(cd "$(dirname "$0")/hotpaste" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/main.py"
PLIST_NAME="com.hotpasteextender.app.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Generating LaunchAgent..."
sed -e "s|__PYTHON_PATH__|$PYTHON|g" \
    -e "s|__SCRIPT_PATH__|$SCRIPT_PATH|g" \
    "hotpaste/$PLIST_NAME" > "$PLIST_DEST"

# Load LaunchAgent
echo "Loading LaunchAgent..."
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "IMPORTANT: Grant Accessibility access to Python:"
echo "  System Preferences > Privacy & Security > Accessibility"
echo "  Add: $PYTHON"
echo ""
echo "HotPasteExtender will start on login. To start now:"
echo "  cd hotpaste && python3 main.py &"
```

**Step 2: Make executable**

Run: `chmod +x setup.sh`

**Step 3: Commit**

```bash
git add setup.sh
git commit -m "feat: add setup.sh for one-command install"
```

---

### Task 7: Create uninstall.sh

**Files:**
- Create: `uninstall.sh`

**Step 1: Write uninstall script**

```bash
#!/bin/bash

echo "=== HotPasteExtender Uninstall ==="

PLIST_NAME="com.hotpasteextender.app.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

# Stop and unload LaunchAgent
if [ -f "$PLIST_PATH" ]; then
    echo "Unloading LaunchAgent..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm "$PLIST_PATH"
    echo "LaunchAgent removed."
else
    echo "No LaunchAgent found."
fi

# Kill running process
pkill -f "hotpaste/main.py" 2>/dev/null && echo "Stopped running process." || true

# Ask about config
echo ""
read -p "Remove config (~/.hotpaste/)? [y/N] " answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm -rf "$HOME/.hotpaste"
    echo "Config removed."
else
    echo "Config kept at ~/.hotpaste/"
fi

echo ""
echo "=== Uninstall Complete ==="
```

**Step 2: Make executable**

Run: `chmod +x uninstall.sh`

**Step 3: Commit**

```bash
git add uninstall.sh
git commit -m "feat: add uninstall.sh for clean removal"
```

---

### Task 8: Add MIT license

**Files:**
- Create: `LICENSE`

**Step 1: Create LICENSE file**

Standard MIT license with copyright `2026 delirious9`.

**Step 2: Commit**

```bash
git add LICENSE
git commit -m "chore: add MIT license"
```

---

### Task 9: Rewrite README.md

**Files:**
- Modify: `hotpaste/README.md`

**Step 1: Rewrite README**

```markdown
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
```

**Step 2: Commit**

```bash
git add hotpaste/README.md
git commit -m "docs: rewrite README for public release"
```

---

### Task 10: Update CLAUDE.md and CODEBASE_MAP.md

**Files:**
- Modify: `CLAUDE.md` — rename HotPaste -> HotPasteExtender throughout
- Modify: `docs/CODEBASE_MAP.md` — rename HotPaste -> HotPasteExtender, update plist filename references

**Step 1: Rename references in CLAUDE.md**

Replace all occurrences of `HotPaste` with `HotPasteExtender` (except in paths like `~/.hotpaste/` which stay as-is per design).
Update plist references from `com.hotpaste.app` to `com.hotpasteextender.app`.

**Step 2: Rename references in CODEBASE_MAP.md**

Same renames. Update plist filename in directory tree. Update class name reference to `HotPasteExtenderApp` if changed, or keep as `HotPasteApp` noting the display name is `HotPasteExtender`.

**Step 3: Commit**

```bash
git add CLAUDE.md docs/CODEBASE_MAP.md
git commit -m "docs: rename HotPaste to HotPasteExtender in docs"
```

---

### Task 11: Stage all untracked docs and plan files

**Files:**
- Add: `docs/plans/*.md`, `CLAUDE.md`, `instructions.md`

**Step 1: Add and commit docs**

```bash
git add CLAUDE.md docs/ instructions.md
git commit -m "docs: add CLAUDE.md, codebase map, design docs, and original instructions"
```

---

### Task 12: Create GitHub repo and push

**Step 1: Create repo on GitHub**

Run: `gh repo create delirious9/hotpasteextender --public --source=. --remote=origin --description "macOS menu bar app for instant text pasting via global hotkeys"`

If `gh` is not installed: create the repo manually at https://github.com/new, then:
```bash
git remote add origin https://github.com/delirious9/hotpasteextender.git
```

**Step 2: Push**

```bash
git push -u origin main
```

**Step 3: Tag v1.0.0**

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

### Task 13: Create Homebrew tap repo

**Step 1: Create the tap repo on GitHub**

Run: `gh repo create delirious9/homebrew-hotpasteextender --public --clone --description "Homebrew tap for HotPasteExtender"`

**Step 2: Get the tarball SHA256**

Run: `curl -sL https://github.com/delirious9/hotpasteextender/archive/refs/tags/v1.0.0.tar.gz | shasum -a 256`

**Step 3: Create the formula**

Create `Formula/hotpasteextender.rb` in the tap repo:

```ruby
class Hotpasteextender < Formula
  include Language::Python::Virtualenv

  desc "macOS menu bar app for instant text pasting via global hotkeys"
  homepage "https://github.com/delirious9/hotpasteextender"
  url "https://github.com/delirious9/hotpasteextender/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "__SHA256__"
  license "MIT"

  depends_on "python@3.11"
  depends_on :macos

  def install
    venv = virtualenv_create(libexec, "python3.11")
    venv.pip_install_and_link buildpath/"hotpaste/requirements.txt"

    # Install app files
    libexec.install "hotpaste/main.py"
    libexec.install "hotpaste/config.py"
    libexec.install "hotpaste/hotkeys.py"

    # Generate launcher script
    (bin/"hotpasteextender").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python3" "#{libexec}/main.py" "$@"
    EOS

    # Install plist template
    prefix.install "hotpaste/com.hotpasteextender.app.plist"
  end

  def post_install
    # Generate LaunchAgent with correct paths
    plist_src = prefix/"com.hotpasteextender.app.plist"
    plist_dest = Pathname.new("#{Dir.home}/Library/LaunchAgents/com.hotpasteextender.app.plist")
    plist_content = plist_src.read
      .gsub("__PYTHON_PATH__", "#{libexec}/bin/python3")
      .gsub("__SCRIPT_PATH__", "#{libexec}/main.py")
    plist_dest.write(plist_content)
  end

  def caveats
    <<~EOS
      IMPORTANT: Grant Accessibility access to:
        #{libexec}/bin/python3

      System Preferences > Privacy & Security > Accessibility

      To start now:
        launchctl load ~/Library/LaunchAgents/com.hotpasteextender.app.plist

      It will auto-start on login.
    EOS
  end

  def uninstall
    system "launchctl", "unload",
      "#{Dir.home}/Library/LaunchAgents/com.hotpasteextender.app.plist"
    rm_f "#{Dir.home}/Library/LaunchAgents/com.hotpasteextender.app.plist"
  end
end
```

Replace `__SHA256__` with the hash from Step 2.

**Step 4: Commit and push the tap**

```bash
cd homebrew-hotpasteextender
git add Formula/hotpasteextender.rb
git commit -m "feat: add hotpasteextender formula v1.0.0"
git push -u origin main
```

**Step 5: Test the tap**

```bash
brew tap delirious9/hotpasteextender
brew install hotpasteextender
```

---

### Task 14: Final verification

**Step 1: Verify brew install works**

Run: `brew install delirious9/hotpasteextender/hotpasteextender`
Expected: installs cleanly, prints caveats about Accessibility

**Step 2: Verify manual install works**

```bash
cd /tmp
git clone https://github.com/delirious9/hotpasteextender.git
cd hotpasteextender
./setup.sh
```
Expected: installs deps, generates plist, loads LaunchAgent

**Step 3: Verify app runs**

Click 📋 in menu bar, edit a slot, press Ctrl+Alt+1.
Expected: text is pasted into focused app.
