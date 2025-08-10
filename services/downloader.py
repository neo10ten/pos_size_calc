# services/downloader.py

from pathlib import Path
import requests

def download_all_assets(
    base_url: str,
    target_dir: Path,
    file_list: list[str]
) -> bool:
    """
    Downloads each filename from base_url/<filename> into target_dir.
    Returns True if all downloads succeed; False otherwise.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    success = True

    for fname in file_list:
        url = f"{base_url}/{fname}"
        dest = target_dir / fname

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            dest.write_text(resp.text, encoding="utf-8")
        except Exception:
            success = False

    return success