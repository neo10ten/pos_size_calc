# assets/updater.py

import logging

REMOTE_VERSION_URL = "https://my.server.com/asset_version.json"

def download_assets(remote_ver: str) -> None:
    """
    Compare local asset version vs. remote_ver and download if newer.
    Stubbed out here—fill in your HTTP+filesystem logic.
    """
    logging.info(f"Would download new assets v{remote_ver}")