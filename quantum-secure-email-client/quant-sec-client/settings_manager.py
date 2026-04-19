import json
import os

DEFAULT_SETTINGS = {
    "security": {
        "encryption_algorithm": "AES",
        "digital_signature": True,
        "hash_algorithm": "SHA-256",
        "key_size": "256"
    },
    "ui": {
        "theme": "Dark",
        "font_size": "Medium",
        "layout": "Comfortable"
    },
    "system": {
        "server_url": "http://127.0.0.1:8000",
        "auto_decrypt": True,
        "enable_logging": True,
        "blockchain_logging": False
    }
}

CONFIG_FILE = "config.json"

def load_settings():
    """Loads settings from the JSON config file."""
    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Saves settings to the JSON config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
