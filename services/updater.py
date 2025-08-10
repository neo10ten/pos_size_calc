# services/updater.py

import json
from packaging.version import Version
from kivy.clock import Clock
from kivy.app import App

from .prompts import prompt_manual_rate,show_update_prompt
from ..config.core.constants import REMOTE_VERSION_URL
from ..config.core.paths import ASSETS_JSONS
from ..utils.network import session,online_status,fetch_rate
from ..utils.threads import run_in_executor
import requests

from .version_checker import (
    read_local_version,
    fetch_remote_version,
    is_update_available,
)
from .downloader import download_all_assets


def check_for_version_update():
    """
    Kick off version check in a background thread.
    On success: if update available → prompt user; otherwise do nothing.
    On error: prompt for manual retry/rate.
    """
    run_in_executor(_background_check)


def _background_check():
    try:
        local_ver = read_local_version(ASSETS_JSONS / "asset_version.json")
        remote_ver = fetch_remote_version(REMOTE_VERSION_URL, timeout=5)

        if is_update_available(local_ver, remote_ver):
            # Schedule prompt in main (UI) thread
            Clock.schedule_once(
                lambda dt: show_update_prompt(local_ver, remote_ver, download_assets), 0
            )

    except Exception as exc:
        app = App.get_running_app()
        Clock.schedule_once(lambda dt: prompt_manual_rate(app), 0)


def download_assets(remote_version: str) -> None:
    """
    Download and install all updated JSON assets.
    Runs in background thread; schedules UI callbacks on completion or failure.
    """
    def _do_download():
        try:
            success = download_all_assets(
                base_url=REMOTE_VERSION_URL.rsplit("/", 1)[0],
                target_dir=ASSETS_JSONS,
                file_list=[
                    "asset_version.json",
                    "currencies.json",
                    "pairs_split.json",
                    "oanda_inst2.json",
                ],
            )

            if success:
                logger.info("Assets updated to version %s", remote_version)
            else:
                logger.warning("Some assets failed to download")

        except Exception as e:
            logger.error("Asset download failed", exc_info=True)
        finally:
            # In a real app, you might inform the user of success/failure here
            pass

    run_in_executor(_do_download)



def update_assets(controller):
    # download new JSONs to assets/assets_jsons
    # ...
    # once done - clear cache
    Clock.schedule_once(lambda dt: controller.refresh_assets_and_ui())

##########################################################################################

# services/updater.py

from packaging.version import Version
from kivy.clock import Clock
from kivy.app import App

from .prompts import prompt_manual_rate, show_update_prompt
from ..config.core.constants import REMOTE_VERSION_URL
from ..config.core.paths import ASSETS_JSONS
from ..utils.threads import run_in_executor
from .version_checker import (
    read_local_version,
    fetch_remote_version,
    is_update_available,
)
from .downloader import download_all_assets


def check_for_version_update(asset_controller):
    """
    Start a background thread to compare versions.
    If an update is available, schedule the UI prompt
    which will in turn call asset_controller.update_assets().
    """
    run_in_executor(lambda: _background_check(asset_controller))


def _background_check(asset_controller):
    try:
        local_ver = read_local_version(ASSETS_JSONS / "asset_version.json")
        remote_ver = fetch_remote_version(REMOTE_VERSION_URL, timeout=5)

        if is_update_available(local_ver, remote_ver):
            Clock.schedule_once(
                lambda dt: show_update_prompt(
                    local_ver,
                    remote_ver,
                    lambda: _start_download(asset_controller, remote_ver),
                ),
                0,
            )

    except Exception:
        app = App.get_running_app()
        Clock.schedule_once(lambda dt: prompt_manual_rate(app), 0)


def _start_download(asset_controller, remote_version: str):
    """
    Kick off the download in a background thread, then refresh UI.
    """
    def _do_download():
        try:
            download_all_assets(
                base_url=REMOTE_VERSION_URL.rsplit("/", 1)[0],
                target_dir=ASSETS_JSONS,
                file_list=[
                    "asset_version.json",
                    "currencies.json",
                    "pairs_split.json",
                    "oanda_inst2.json",
                ],
            )
        finally:
            Clock.schedule_once(
                lambda dt: asset_controller.refresh_assets_and_ui(), 0
            )

    run_in_executor(_do_download)