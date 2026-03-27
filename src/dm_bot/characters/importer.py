from dm_bot.characters.models import CharacterRecord


class CharacterImporter:
    def __init__(self, *, sources: dict[str, object]) -> None:
        self._sources = sources

    def import_character(self, provider: str, external_id: str) -> CharacterRecord:
        if provider not in self._sources:
            raise KeyError(f"unknown character source provider: {provider}")
        source = self._sources[provider]
        return source.fetch(external_id)
