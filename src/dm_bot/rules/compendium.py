from dm_bot.rules.actions import LookupAction


class FixtureCompendium:
    def __init__(self, *, baseline: str, fixtures: dict[tuple[str, str], dict[str, object]]) -> None:
        self._baseline = baseline
        self._fixtures = fixtures

    def lookup(self, action: LookupAction) -> dict[str, object]:
        if action.baseline != self._baseline:
            raise ValueError(f"unsupported rules baseline: {action.baseline}")
        key = (action.kind, action.slug)
        if key not in self._fixtures:
            raise KeyError(f"missing compendium entry: {key}")
        return self._fixtures[key]
