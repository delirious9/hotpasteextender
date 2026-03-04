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
