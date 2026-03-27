from dm_bot.characters.models import (
    AbilityScores,
    AttackProfile,
    CharacterRecord,
    CharacterSourceInfo,
    CharacterSourceLabel,
    HitPoints,
    SpellcastingSummary,
)


class DicecloudSnapshotSource:
    provider = "dicecloud_snapshot"
    label = CharacterSourceLabel.SNAPSHOT

    def __init__(self, *, fixtures: dict[str, dict[str, object]]) -> None:
        self._fixtures = fixtures

    def fetch(self, external_id: str) -> CharacterRecord:
        payload = self._fixtures[external_id]
        spellcasting = payload.get("spellcasting")
        return CharacterRecord(
            source=CharacterSourceInfo(provider=self.provider, label=self.label),
            external_id=str(payload["id"]),
            name=str(payload["name"]),
            species=str(payload["species"]),
            classes=list(payload.get("classes", [])),
            proficiency_bonus=int(payload["proficiency_bonus"]),
            armor_class=int(payload["armor_class"]),
            speed=int(payload["speed"]),
            hp=HitPoints.model_validate(payload["hp"]),
            abilities=AbilityScores.model_validate(payload["abilities"]),
            skills={key: int(value) for key, value in dict(payload.get("skills", {})).items()},
            attacks=[AttackProfile.model_validate(item) for item in list(payload.get("attacks", []))],
            spellcasting=SpellcastingSummary.model_validate(spellcasting) if spellcasting else None,
            resources={key: int(value) for key, value in dict(payload.get("resources", {})).items()},
        )
