from os.path import isfile

from re import search

from automonkey import ALL_ACTIONS

from .constants import COORDS_REGEX

def _clean_steps(steps: dict) -> dict:
    """Prepare steps for automonkey chain."""
    cleaned = {}
    for key, value in steps.items():
        if not isfile(value["target"]) and search(COORDS_REGEX, value["target"]):
            step = {value["action"]: tuple(map(int, value["target"].split(",")))}
        else:
            step = {value["action"]: value["target"]}
        for key2, value2 in value.items():
            if key2 not in ("", "skip", "action", "target") + ALL_ACTIONS and value2 not in ("", "action", "target") + ALL_ACTIONS:
                step[key2] = int(value2)
            elif key2 == "skip":
                step[key2] = eval(value2)
        cleaned[key] = step
    return cleaned
