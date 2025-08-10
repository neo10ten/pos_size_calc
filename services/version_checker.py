# services/version_checker.py

import json
from pathlib import Path

import requests
from packaging.version import Version, InvalidVersion

def read_local_version(path: Path) -> Version:
    """
    Reads the local asset_version.json and returns a Version instance.
    """
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    version_str = data.get("version")
    if not version_str:
        raise ValueError("Missing 'version' field in local asset_version.json")
    try:
        return Version(version_str)
    except InvalidVersion as e:
        raise ValueError(f"Invalid local version string: {version_str}") from e

def fetch_remote_version(url: str, timeout: int = 5) -> Version:
    """
    Downloads remote asset_version.json, parses it, and returns its Version.
    """
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    version_str = data.get("version")
    if not version_str:
        raise ValueError("Missing 'version' field in remote asset_version.json")
    try:
        return Version(version_str)
    except InvalidVersion as e:
        raise ValueError(f"Invalid remote version string: {version_str}") from e

def is_update_available(local_ver: Version, remote_ver: Version) -> bool:
    """
    Returns True if remote_ver is strictly greater than local_ver.
    """
    return remote_ver > local_ver