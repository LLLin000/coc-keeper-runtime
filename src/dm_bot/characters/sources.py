from dm_bot.characters.models import (
    AbilityScores,
    AttackProfile,
    CharacterRecord,
    COCAttributes,
    COCInvestigatorProfile,
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


class COCInvestigatorSource:
    provider = "coc_pregen"
    label = CharacterSourceLabel.COC_PREGEN

    def __init__(self, *, fixtures: dict[str, dict[str, object]]) -> None:
        self._fixtures = fixtures

    def fetch(self, external_id: str) -> CharacterRecord:
        payload = self._fixtures[external_id]
        coc_payload = {
            "occupation": str(payload.get("occupation", "")),
            "age": int(payload.get("age", 0)),
            "san": int(payload.get("san", 0)),
            "hp": int(payload.get("hp", 0)),
            "mp": int(payload.get("mp", 0)),
            "luck": int(payload.get("luck", 0)),
            "build": int(payload.get("build", 0)),
            "damage_bonus": str(payload.get("damage_bonus", "0")),
            "move_rate": int(payload.get("move_rate", 0)),
            "attributes": COCAttributes.model_validate(payload.get("attributes", {})),
            "skills": {key: int(value) for key, value in dict(payload.get("skills", {})).items()},
        }
        return CharacterRecord(
            source=CharacterSourceInfo(provider=self.provider, label=self.label),
            external_id=str(payload["id"]),
            name=str(payload["name"]),
            species="human",
            hp=HitPoints(current=int(payload.get("hp", 0)), maximum=int(payload.get("hp", 0)), temporary=0),
            coc=COCInvestigatorProfile.model_validate(coc_payload),
            skills={key: int(value) for key, value in dict(payload.get("skills", {})).items()},
        )
