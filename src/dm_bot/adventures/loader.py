import json
from importlib import resources
from pathlib import Path

from dm_bot.adventures.models import AdventurePackage


def load_adventure(adventure_id: str, *, base_path: Path | None = None) -> AdventurePackage:
    if base_path is None:
        resource = resources.files("dm_bot.adventures").joinpath(f"{adventure_id}.json")
        with resource.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        path = Path(base_path) / f"{adventure_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
    return AdventurePackage.model_validate(payload)
