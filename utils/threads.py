# utils/threads.py

import threading
from concurrent.futures import ThreadPoolExecutor
from kivy.clock import Clock

# Shared executor for pre-warming or batch jobs
executor = ThreadPoolExecutor(max_workers=10)


def run_in_thread(fn, *args, **kwargs):
    """
    Fire off fn(*args, **kwargs) in a daemon thread.
    Useful for non-blocking one-off calls.
    """
    t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t


def run_in_executor(fn, callback=None, *args, **kwargs):
    """
    Submit fn(*args, **kwargs) to the shared executor.
    If callback is provided, schedule callback(result) on the Kivy main loop.
    """
    future = executor.submit(fn, *args, **kwargs)
    if callback:
        def _cb(fut):
            result = fut.result()
            Clock.schedule_once(lambda dt: callback(result))
        future.add_done_callback(_cb)
    return future