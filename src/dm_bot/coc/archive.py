from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from dm_bot.characters.models import COCAttributes, COCInvestigatorProfile


class ArchiveFinishingRecommendation(BaseModel):
    recommended_occupation_skills: list[str] = Field(default_factory=list)
    recommended_interest_skills: list[str] = Field(default_factory=list)
    allowed_adjustments: list[str] = Field(default_factory=list)
    rules_note: str = ""


class InvestigatorArchiveProfile(BaseModel):
    schema_version: int = 2
    profile_id: str
    user_id: str
    name: str
    occupation: str
    age: int
    concept: str = ""
    occupation_detail: str = ""
    specialty: str = ""
    background: str = ""
    career_arc: str = ""
    key_past_event: str = ""
    core_belief: str = ""
    life_goal: str = ""
    material_desire: str = ""
    weakness: str = ""
    fear_or_taboo: str = ""
    important_tie: str = ""
    birthplace: str = ""
    residence: str = ""
    family: str = ""
    education_background: str = ""
    important_person: str = ""
    significant_location: str = ""
    treasured_possession: str = ""
    trait_notes: str = ""
    scars_and_injuries: str = ""
    phobias_and_manias: str = ""
    disposition: str = ""
    favored_skills: list[str] = Field(default_factory=list)
    portrait_summary: str = ""
    status: str = "active"
    finishing: ArchiveFinishingRecommendation = Field(
        default_factory=ArchiveFinishingRecommendation
    )
    coc: COCInvestigatorProfile

    def summary_line(self) -> str:
        goal = self.life_goal or "未记录目标"
        goal = goal[:20] + ("…" if len(goal) > 20 else "")
        return f"{self.profile_id} | {self.name} | {self.coc.occupation} | SAN {self.coc.san} | {self.status} | 目标 {goal}"

    def card_view(self) -> list[tuple[str, str]]:
        """Return archive profile as a list of (section_title, section_content) tuples.

        Each section is designed to fit within Discord's 1024-character embed field limit.
        Long-lived archive data only — campaign-local state (SAN, HP, MP, Luck from
        InvestigatorPanel) is shown separately.

        Returns:
            List of 6 sections: 档案, 身份, 人物, 塑造, 数值, 技能与收束
        """
        sections: list[tuple[str, str]] = []

        # Section 1: Header with 长期档案 label
        header = (
            f"**{self.name}** | {self.coc.occupation} | {self.age}岁 | {self.status}\n"
            f"📁 长期档案 — 以下内容属于长期调查员档案，不包含当前模组里的临时状态。"
        )
        sections.append(("📋 调查员档案", header))

        # Section 2: 身份
        identity_lines = [
            f"骨架：{self.concept or '未记录'}",
            f"出生地：{self.birthplace or '未记录'}",
            f"现居地：{self.residence or '未记录'}",
            f"家庭：{self.family or '未记录'}",
            f"教育：{self.education_background or '未记录'}",
        ]
        sections.append(("🏷️ 身份", "\n".join(identity_lines)))

        # Section 3: 人物
        person_lines = [
            f"职业：{self.occupation_detail or self.occupation or '未记录'}",
            f"专长：{self.specialty or '未记录'}",
            f"职业轨迹：{self.career_arc or self.background or '未记录'}",
        ]
        sections.append(("💼 人物", "\n".join(person_lines)))

        # Section 4: 塑造
        important_person = self.important_person or self.important_tie or "未记录"
        shaping_lines = [
            f"关键过往：{self.key_past_event or '未记录'}",
            f"核心信念：{self.core_belief or '未记录'}",
            f"人生目标：{self.life_goal or '未记录'}",
            f"物质欲望：{self.material_desire or '未记录'}",
            f"弱点：{self.weakness or '未记录'}",
            f"特质：{self.trait_notes or self.disposition or '未记录'}",
            f"重要之人：{important_person}",
            f"重要场所：{self.significant_location or '未记录'}",
            f"珍贵之物：{self.treasured_possession or '未记录'}",
            f"恐惧/禁忌：{self.fear_or_taboo or '未记录'}",
            f"伤口与疤痕：{self.scars_and_injuries or '未记录'}",
            f"恐惧症/躁狂症：{self.phobias_and_manias or '未记录'}",
            f"处事方式：{self.disposition or '未记录'}",
        ]
        sections.append(("🎭 塑造", "\n".join(shaping_lines)))

        # Section 5: 数值 with emoji indicators
        attrs = self.coc.attributes
        stats_lines = [
            f"STR {attrs.str} / CON {attrs.con} / DEX {attrs.dex} / APP {attrs.app}",
            f"POW {attrs.pow} / SIZ {attrs.siz} / INT {attrs.int} / EDU {attrs.edu}",
            f"🧠 SAN {self.coc.san} / ❤️ HP {self.coc.hp} / 💧 MP {self.coc.mp} / 🍀 LUCK {self.coc.luck}",
            f"MOV {self.coc.move_rate} / 体格 {self.coc.build} / 伤害加值 {self.coc.damage_bonus}",
        ]
        sections.append(("📊 数值", "\n".join(stats_lines)))

        # Section 6: 技能与收束
        favored = "、".join(self.favored_skills) if self.favored_skills else "未记录"
        occ_skills = (
            "、".join(self.finishing.recommended_occupation_skills)
            if self.finishing.recommended_occupation_skills
            else "未记录"
        )
        interest_skills = (
            "、".join(self.finishing.recommended_interest_skills)
            if self.finishing.recommended_interest_skills
            else "未记录"
        )
        adjustments = (
            "；".join(self.finishing.allowed_adjustments)
            if self.finishing.allowed_adjustments
            else "无"
        )
        skills_lines = [
            f"偏好技能：{favored}",
            f"职业技能建议：{occ_skills}",
            f"兴趣技能建议：{interest_skills}",
            f"允许的规则内收束：{adjustments}",
            f"规则说明：{self.finishing.rules_note or '未记录'}",
        ]
        sections.append(("📚 技能与收束", "\n".join(skills_lines)))

        return sections

    def detail_view(self) -> str:
        favored = "、".join(self.favored_skills) if self.favored_skills else "未记录"
        occ_skills = (
            "、".join(self.finishing.recommended_occupation_skills)
            if self.finishing.recommended_occupation_skills
            else "未记录"
        )
        interest_skills = (
            "、".join(self.finishing.recommended_interest_skills)
            if self.finishing.recommended_interest_skills
            else "未记录"
        )
        adjustments = (
            "；".join(self.finishing.allowed_adjustments)
            if self.finishing.allowed_adjustments
            else "无"
        )
        important_person = self.important_person or self.important_tie or "未记录"
        lines = [
            "【调查员档案】",
            f"{self.name} / {self.coc.occupation} / {self.age}岁 / {self.status}",
            "以下内容属于长期档案，不包含当前模组里的临时 SAN、伤势、装备和秘密状态。",
            "",
            "【身份】",
            f"骨架：{self.concept or '未记录'}",
            f"出生地：{self.birthplace or '未记录'}",
            f"现居地：{self.residence or '未记录'}",
            f"家庭：{self.family or '未记录'}",
            f"教育：{self.education_background or '未记录'}",
            "",
            "【人物】",
            f"职业细化：{self.occupation_detail or self.occupation or '未记录'}",
            f"专长：{self.specialty or '未记录'}",
            f"职业轨迹：{self.career_arc or self.background or '未记录'}",
            "",
            "【塑造】",
            f"关键过往：{self.key_past_event or '未记录'}",
            f"核心信念：{self.core_belief or '未记录'}",
            f"人生目标：{self.life_goal or '未记录'}",
            f"物质欲望：{self.material_desire or '未记录'}",
            f"弱点：{self.weakness or '未记录'}",
            f"特质：{self.trait_notes or self.disposition or '未记录'}",
            f"重要之人：{important_person}",
            f"重要场所：{self.significant_location or '未记录'}",
            f"珍贵之物：{self.treasured_possession or '未记录'}",
            f"恐惧/禁忌：{self.fear_or_taboo or '未记录'}",
            f"伤口与疤痕：{self.scars_and_injuries or '未记录'}",
            f"恐惧症/躁狂症：{self.phobias_and_manias or '未记录'}",
            f"处事方式：{self.disposition or '未记录'}",
            "",
            "【数值】",
            f"STR {self.coc.attributes.str} / CON {self.coc.attributes.con} / DEX {self.coc.attributes.dex} / APP {self.coc.attributes.app}",
            f"POW {self.coc.attributes.pow} / SIZ {self.coc.attributes.siz} / INT {self.coc.attributes.int} / EDU {self.coc.attributes.edu}",
            f"SAN {self.coc.san} / HP {self.coc.hp} / MP {self.coc.mp} / LUCK {self.coc.luck} / MOV {self.coc.move_rate}",
            f"体格 {self.coc.build} / 伤害加值 {self.coc.damage_bonus}",
            "",
            "【技能与收束】",
            f"偏好技能：{favored}",
            f"职业技能建议：{occ_skills}",
            f"兴趣技能建议：{interest_skills}",
            f"允许的规则内收束：{adjustments}",
            f"规则说明：{self.finishing.rules_note or '未记录'}",
        ]
        return "\n".join(lines)


class InvestigatorArchiveRepository:
    def __init__(self, persistence_store=None) -> None:
        self._profiles: dict[str, dict[str, InvestigatorArchiveProfile]] = {}
        self._persistence = persistence_store

    def create_profile(
        self,
        *,
        user_id: str,
        name: str,
        occupation: str,
        age: int,
        background: str,
        portrait_summary: str = "",
        concept: str = "",
        occupation_detail: str = "",
        specialty: str = "",
        career_arc: str = "",
        key_past_event: str = "",
        core_belief: str = "",
        life_goal: str = "",
        material_desire: str = "",
        weakness: str = "",
        fear_or_taboo: str = "",
        important_tie: str = "",
        birthplace: str = "",
        residence: str = "",
        family: str = "",
        education_background: str = "",
        important_person: str = "",
        significant_location: str = "",
        treasured_possession: str = "",
        trait_notes: str = "",
        scars_and_injuries: str = "",
        phobias_and_manias: str = "",
        disposition: str,
        favored_skills: list[str],
        generation: dict[str, int],
    ) -> InvestigatorArchiveProfile:
        if self.active_profile(user_id) is not None:
            raise ValueError("已有激活档案，请先归档或替换当前主角色。")
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
        finishing = _build_finishing_recommendation(
            occupation=occupation,
            age=age,
            favored_skills=favored,
            specialty=specialty,
            concept=concept,
        )
        profile = InvestigatorArchiveProfile(
            schema_version=3,
            profile_id=str(uuid4()),
            user_id=user_id,
            name=name,
            occupation=occupation,
            age=age,
            concept=concept,
            occupation_detail=occupation_detail or occupation,
            specialty=specialty,
            background=background,
            career_arc=career_arc,
            key_past_event=key_past_event,
            core_belief=core_belief,
            life_goal=life_goal,
            material_desire=material_desire,
            weakness=weakness,
            fear_or_taboo=fear_or_taboo,
            important_tie=important_tie,
            birthplace=birthplace,
            residence=residence,
            family=family,
            education_background=education_background,
            important_person=important_person,
            significant_location=significant_location,
            treasured_possession=treasured_possession,
            trait_notes=trait_notes,
            scars_and_injuries=scars_and_injuries,
            phobias_and_manias=phobias_and_manias,
            disposition=disposition,
            favored_skills=favored,
            portrait_summary=portrait_summary
            or f"{occupation}。{background} 性格上{disposition}",
            status="active",
            finishing=finishing,
            coc=COCInvestigatorProfile(
                occupation=occupation,
                age=age,
                san=attributes.pow,
                hp=(attributes.con + attributes.siz) // 10,
                mp=max(0, attributes.pow // 5),
                luck=int(generation["luck"]),
                build=_build_for(attributes.str + attributes.siz),
                damage_bonus=_damage_bonus_for(attributes.str + attributes.siz),
                move_rate=_move_rate_for(
                    attributes.str, attributes.dex, attributes.siz, age
                ),
                attributes=attributes,
                skills=skills,
            ),
        )
        self._profiles.setdefault(user_id, {})[profile.profile_id] = profile
        return profile

    def list_profiles(self, user_id: str) -> list[InvestigatorArchiveProfile]:
        profiles = list(self._profiles.get(user_id, {}).values())
        return sorted(profiles, key=lambda item: (item.status != "active", item.name))

    def list_all_profiles(self) -> list[InvestigatorArchiveProfile]:
        return [
            profile
            for profiles in self._profiles.values()
            for profile in profiles.values()
        ]

    def get_profile(self, user_id: str, profile_id: str) -> InvestigatorArchiveProfile:
        return self._profiles[user_id][profile_id]

    def latest_profile(self, user_id: str) -> InvestigatorArchiveProfile | None:
        profiles = list(self._profiles.get(user_id, {}).values())
        return profiles[-1] if profiles else None

    def active_profile(self, user_id: str) -> InvestigatorArchiveProfile | None:
        for profile in self._profiles.get(user_id, {}).values():
            if profile.status == "active":
                return profile
        return None

    def archive_profile(
        self, *, user_id: str, profile_id: str
    ) -> InvestigatorArchiveProfile:
        profile = self.get_profile(user_id, profile_id)
        profile.status = "archived"
        return profile

    def replace_active_with(
        self, *, user_id: str, profile_id: str
    ) -> InvestigatorArchiveProfile:
        active = self.active_profile(user_id)
        if active is not None and active.profile_id != profile_id:
            active.status = "replaced"
        profile = self.get_profile(user_id, profile_id)
        profile.status = "active"
        return profile

    def update_profile(
        self,
        *,
        user_id: str,
        profile_id: str,
        **updates,
    ) -> InvestigatorArchiveProfile:
        """Update an existing profile.

        Args:
            user_id: The user ID
            profile_id: The profile ID to update
            **updates: Fields to update (only updatable fields)

        Returns:
            The updated profile

        Raises:
            ValueError: If profile not found or invalid updates
        """
        profile = self.get_profile(user_id, profile_id)

        # Fields that cannot be updated
        read_only = {"profile_id", "user_id", "coc", "schema_version"}

        # Validate updates
        invalid = set(updates.keys()) & read_only
        if invalid:
            raise ValueError(f"Cannot update read-only fields: {invalid}")

        # Apply updates
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
            else:
                raise ValueError(f"Unknown field: {key}")

        # Update in storage
        self._profiles[user_id][profile_id] = profile

        return profile

    def update_coc_stats(
        self,
        *,
        user_id: str,
        profile_id: str,
        **coc_updates,
    ) -> InvestigatorArchiveProfile:
        """Update COC-specific stats.

        Args:
            user_id: The user ID
            profile_id: The profile ID
            **coc_updates: Updates to COCInvestigatorProfile

        Returns:
            The updated profile
        """
        profile = self.get_profile(user_id, profile_id)

        # Update COC fields
        for key, value in coc_updates.items():
            if hasattr(profile.coc, key):
                setattr(profile.coc, key, value)
            else:
                raise ValueError(f"Unknown COC field: {key}")

        self._profiles[user_id][profile_id] = profile
        return profile

    def update_skills(
        self,
        *,
        user_id: str,
        profile_id: str,
        skills: dict[str, int],
    ) -> InvestigatorArchiveProfile:
        """Update character skills.

        Args:
            user_id: The user ID
            profile_id: The profile ID
            skills: Dict of skill_name -> skill_value

        Returns:
            The updated profile
        """
        profile = self.get_profile(user_id, profile_id)

        for skill, value in skills.items():
            profile.coc.skills[skill] = value

        self._profiles[user_id][profile_id] = profile
        return profile

    def delete_profile(self, *, user_id: str, profile_id: str) -> None:
        self._profiles.get(user_id, {}).pop(profile_id, None)

    def export_state(self) -> dict[str, object]:
        return {
            user_id: {
                profile_id: profile.model_dump()
                for profile_id, profile in profiles.items()
            }
            for user_id, profiles in self._profiles.items()
        }

    def import_state(self, payload: dict[str, object]) -> None:
        self._profiles = {}
        for user_id, raw_profiles in payload.items():
            bucket: dict[str, InvestigatorArchiveProfile] = {}
            for profile_id, raw in dict(raw_profiles).items():
                bucket[profile_id] = InvestigatorArchiveProfile.model_validate(raw)
            self._profiles[str(user_id)] = bucket

    def save_to_persistence(self, user_id: str, profile_id: str) -> None:
        """Save a profile to persistent storage.

        Args:
            user_id: The user ID
            profile_id: The profile ID
        """
        if not self._persistence:
            return

        profile = self.get_profile(user_id, profile_id)
        self._persistence.save_profile(user_id, profile.model_dump())

    def load_from_persistence(self, user_id: str) -> list[InvestigatorArchiveProfile]:
        """Load all profiles for a user from persistent storage.

        Args:
            user_id: The user ID

        Returns:
            List of loaded profiles
        """
        if not self._persistence:
            return []

        profiles_data = self._persistence.load_user_profiles(user_id)
        profiles = []

        for data in profiles_data:
            profile = InvestigatorArchiveProfile.model_validate(data)
            profiles.append(profile)

            # Add to memory
            if user_id not in self._profiles:
                self._profiles[user_id] = {}
            self._profiles[user_id][profile.profile_id] = profile

        return profiles

    def persist_all(self) -> None:
        """Save all profiles to persistent storage."""
        if not self._persistence:
            return

        for user_id, profiles in self._profiles.items():
            for profile_id, profile in profiles.items():
                self._persistence.save_profile(user_id, profile.model_dump())


def _build_finishing_recommendation(
    *,
    occupation: str,
    age: int,
    favored_skills: list[str],
    specialty: str,
    concept: str,
) -> ArchiveFinishingRecommendation:
    occupation_skills = _occupation_skill_suggestions(
        occupation=occupation, specialty=specialty
    )
    interest_skills = list(dict.fromkeys([skill for skill in favored_skills if skill]))
    allowed_adjustments = [
        "按职业与兴趣技能点分配来体现人物采访结果",
        "允许在职业细化范围内重新排序推荐技能",
    ]
    if age >= 40:
        allowed_adjustments.append("按本地规则书应用年龄相关修正")
    if "落魄" in concept or "失意" in concept:
        allowed_adjustments.append(
            "只通过信用评级、资源叙述和技能倾向体现落魄感，不直接改核心属性"
        )
    return ArchiveFinishingRecommendation(
        recommended_occupation_skills=occupation_skills,
        recommended_interest_skills=interest_skills,
        allowed_adjustments=allowed_adjustments,
        rules_note="采访结果只能影响规则允许的职业/兴趣技能倾向与合法修正，不能直接发明属性加值。",
    )


def _occupation_skill_suggestions(*, occupation: str, specialty: str) -> list[str]:
    base = occupation + " " + specialty
    if "医生" in base or "医学" in base:
        return ["医学", "急救", "科学(生物学)", "心理学"]
    if "记者" in base:
        return ["图书馆使用", "心理学", "说服", "侦查"]
    if "警察" in base or "侦探" in base:
        return ["侦查", "法律", "心理学", "聆听"]
    return ["图书馆使用", "聆听", "心理学"]


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
