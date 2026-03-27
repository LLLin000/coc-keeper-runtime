import json
from importlib import resources

from dm_bot.adventures.models import AdventurePackage


def load_adventure(adventure_id: str) -> AdventurePackage:
    resource = resources.files("dm_bot.adventures").joinpath(f"{adventure_id}.json")
    with resource.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return AdventurePackage.model_validate(payload)
