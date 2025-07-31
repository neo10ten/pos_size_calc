# assets/loader.py

import json
from .paths import ASSETS_JSONS

# Generic json loader from assets/assets_jsons
def load_json(name):
    path = ASSETS_JSONS / name
    with open(path, 'r') as f:
        return json.load(f)

# Specific json loader for currencies file only
def load_currencies():
    path = ASSETS_JSONS / "currencies.json"
    with open(path, 'r') as f:
        return json.load(f)

# Specific json loader for standard-other split file only
def load_pairs_split():
    path = ASSETS_JSONS / "pairs_split.json"
    with open(path, 'r') as f:
        ps = json.load(f)
    return set(ps["standard"]), set(ps["other"])

def load_other_instruments():
        path = ASSETS_JSONS / "oanda_inst2.json"
        with open(path, 'r') as f:
            data = json.load(f)
        instruments = data["instruments"]
        other_insts = [instruments[i]["displayName"] for i in range(len(instruments)) if instruments[i]["type"] != "CURRENCY"]
        return other_insts