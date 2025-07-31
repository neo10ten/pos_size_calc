# utils/network.py

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import socket
import time

def create_session(retries=3, backoff_factor=1,
                   status_forcelist=None) -> requests.Session:
    """Return a Session with a mounted retry strategy."""
    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]

    session = requests.Session()
    retry = Retry(total=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

# one shared session for your app
session = create_session()

def online_status(host="8.8.8.8", port=53, timeout=3):
    """
    Quick check if network is up by opening a socket to a public DNS.
    """
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

_rate_cache = {}
CACHE_TTL = 300  # seconds

def fetch_rate(base: str, quote: str):
    """
    Return the FX rate base→quote, caching results for CACHE_TTL seconds.
    """
    key = (base, quote)
    now = time.time()

    if key in _rate_cache:
        ts, cached = _rate_cache[key]
        if now - ts < CACHE_TTL:
            return cached

    resp = session.get(
        "https://api.frankfurter.app/latest",
        params={"from": base, "to": quote},
        timeout=5,
    )
    resp.raise_for_status()
    rate = resp.json().get("rates", {}).get(quote)
    if rate is None:
        raise ValueError(f"No rate for {base}/{quote}")

    _rate_cache[key] = (now, rate)
    return float(rate)
