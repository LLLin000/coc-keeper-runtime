from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from dm_bot.characters.models import COCAttributes, COCInvestigatorProfile


class InvestigatorArchiveProfile(BaseModel):
    profile_id: str
    user_id: str
    name: str
    occupation: str
    age: int
    background: str = ""
    disposition: str = ""
    favored_skills: list[str] = Field(default_factory=list)
    portrait_summary: str = ""
    coc: COCInvestigatorProfile


class InvestigatorArchiveRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, InvestigatorArchiveProfile]] = {}

    def create_profile(
        self,
        *,
        user_id: str,
        name: str,
        occupation: str,
        age: int,
        background: str,
        disposition: str,
        favored_skills: list[str],
        generation: dict[str, int],
    ) -> InvestigatorArchiveProfile:
        attributes = COCAttributes(
            str=int(generation["str"]),
            con=int(generation["con"]),
            dex=int(generation["dex"]),
            app=int(generation["app"]),
            pow=int(generation["pow"]),
            siz=int(generation["siz"]),
            int=int(generation["int"]),
            edu=int(generation["edu"]),
        )
        favored = [skill.strip() for skill in favored_skills if skill.strip()]
        skills = {skill: 50 for skill in favored}
        profile = InvestigatorArchiveProfile(
            profile_id=str(uuid4()),
            user_id=user_id,
            name=name,
            occupation=occupation,
            age=age,
            background=background,
            disposition=disposition,
            favored_skills=favored,
            portrait_summary=f"{occupation}。{background} 性格上{disposition}",
            coc=COCInvestigatorProfile(
                occupation=occupation,
                age=age,
                san=attributes.pow,
                hp=(attributes.con + attributes.siz) // 10,
                mp=max(0, attributes.pow // 5),
                luck=int(generation["luck"]),
                build=_build_for(attributes.str + attributes.siz),
                damage_bonus=_damage_bonus_for(attributes.str + attributes.siz),
                move_rate=_move_rate_for(attributes.str, attributes.dex, attributes.siz, age),
                attributes=attributes,
                skills=skills,
            ),
        )
        self._profiles.setdefault(user_id, {})[profile.profile_id] = profile
        return profile

    def list_profiles(self, user_id: str) -> list[InvestigatorArchiveProfile]:
        return list(self._profiles.get(user_id, {}).values())

    def get_profile(self, user_id: str, profile_id: str) -> InvestigatorArchiveProfile:
        return self._profiles[user_id][profile_id]

    def export_state(self) -> dict[str, object]:
        return {
            user_id: {profile_id: profile.model_dump() for profile_id, profile in profiles.items()}
            for user_id, profiles in self._profiles.items()
        }

    def import_state(self, payload: dict[str, object]) -> None:
        self._profiles = {}
        for user_id, raw_profiles in payload.items():
            bucket: dict[str, InvestigatorArchiveProfile] = {}
            for profile_id, raw in dict(raw_profiles).items():
                bucket[profile_id] = InvestigatorArchiveProfile.model_validate(raw)
            self._profiles[str(user_id)] = bucket


def _build_for(total: int) -> int:
    if total < 65:
        return -2
    if total < 85:
        return -1
    if total < 125:
        return 0
    if total < 165:
        return 1
    if total < 205:
        return 2
    return 3


def _damage_bonus_for(total: int) -> str:
    if total < 65:
        return "-2"
    if total < 85:
        return "-1"
    if total < 125:
        return "0"
    if total < 165:
        return "+1d4"
    if total < 205:
        return "+1d6"
    return "+2d6"


def _move_rate_for(str_value: int, dex_value: int, siz_value: int, age: int) -> int:
    if str_value < siz_value and dex_value < siz_value:
        base = 7
    elif str_value > siz_value and dex_value > siz_value:
        base = 9
    else:
        base = 8
    if age >= 40:
        base -= 1
    return max(5, base)
