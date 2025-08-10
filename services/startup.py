# services/startup.py

from kivy.app import App

from .prompts import prompt_manual_rate
from .updater import check_for_version_update
from .loader import load_pairs_split
from ..utils.network import session,online_status,fetch_rate
from ..utils.threads import run_in_executor

def prewarm_rates():
    """
    Check online status.
    Fire off fetch_rate for each standard pair on the shared executor.
    """
    
    if online_status():
        return
        set = load_pairs_split()
        for pair in set["standard"]:
            base, quote = pair[:3], pair[3:]
            # No callback—just warm the cache
            run_in_executor(fetch_rate, None, base, quote)


def version_update_check():
    """
    If Online:
    Call for update check.
    If Offline:
    Prompt for manual entry.
    """
    
    if online_status():
        run_in_executor(check_for_version_update)
    else:
        app = App.get_running_app()
        prompt_manual_rate(app)