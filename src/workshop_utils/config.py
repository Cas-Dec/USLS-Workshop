# workshop_utils/config.py

from pathlib import Path

def get_workshop_root():
    if Path("/content/drive").exists():
        return Path("/content/drive/MyDrive/biology-workshop")
    else:
        return Path.cwd() / "biology-workshop"

WORKSHOP_ROOT = get_workshop_root()

DATA_DIR = WORKSHOP_ROOT / "data"
FIGURES_DIR = WORKSHOP_ROOT / "figures"
RESULTS_DIR = WORKSHOP_ROOT / "results"