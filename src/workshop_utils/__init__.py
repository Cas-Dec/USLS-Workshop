# __init__.py for workshop_utils package

import pyprojroot

PROJECT_ROOT = pyprojroot.find_root(pyprojroot.criterion.has_file("pyproject.toml"))
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# auto-create the folders whenever the package is imported
for d in [RAW_DIR, PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)