# config/core/paths.py

from pathlib import Path

# Project root:
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Assets directory and subfolders
ASSETS_DIR     = PROJECT_ROOT / "assets"
ASSETS_JSONS   = ASSETS_DIR  / "assets_jsons"

# Add more as needed:
# REPORTS_DIR   = PROJECT_ROOT / "reports"
# CACHE_DIR     = PROJECT_ROOT / "cache"