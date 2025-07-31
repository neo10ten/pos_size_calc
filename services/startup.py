# pos_size_calc/services/startup.py

import os, json, logging
from packaging.version import Version

from ..assets import CURRENCIES,STANDARD_SET,REMOTE_VERSION_URL,ASSETS_JSONS
from ..utils import run_in_executor,session,fetch_rate


def prewarm_rates():
    """
    Fire off fetch_rate for each standard pair on the shared executor.
    """
    for pair in STANDARD_SET:
        base, quote = pair[:3], pair[3:]
        # No callback—just warm the cache
        run_in_executor(fetch_rate, None, base, quote)


def check_for_update(callback):
    """
    Do version check in background; call `callback((local, remote))` on the Kivy main thread if update needed.
    """
    def _check():
        try:
            fn = os.path.join(ASSETS_JSONS, "asset_version.json")
            local = json.load(open(fn))["asset_version"]
            resp  = session.get(REMOTE_VERSION_URL, timeout=5)
            resp.raise_for_status()
            remote = resp.json().get("asset_version")
            if Version(remote) > Version(local):
                return (local, remote)
        except Exception as e:
            logging.info(f"Version check skipped: {e}")
        return None

    # Pass the result to callback on the Kivy thread
    run_in_executor(_check, callback)