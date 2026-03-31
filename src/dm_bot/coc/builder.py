from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Protocol

from pydantic import BaseModel, Field

from dm_bot.coc.archive import InvestigatorArchiveProfile, InvestigatorArchiveRepository
from dm_bot.models.schemas import ModelRequest


@dataclass
class BuilderQuestionChoice:
    slot: str
    question: str


@dataclass
class BuilderSession:
    user_id: str
    visibility: str = "private"
    stage: str = "interview"
    raw_answers: dict[str, str] = field(default_factory=dict)
    answers: dict[str, str] = field(default_factory=dict)
    current_slot: str = "name"
    asked_slots: list[str] = field(default_factory=lambda: ["name"])
    portrait_summary: str = ""
    pending_writeback: ArchiveWritebackPayload | None = None


class NormalizedBuilderAnswers(BaseModel):
    name: str = ""
    concept: str = ""
    age: str = ""
    occupation: str = ""
    key_past_event: str = ""
    life_goal: str = ""
    weakness: str = ""
    core_belief: str = ""
    important_person: str = ""
    significant_location: str = ""
    treasured_possession: str = ""
    disposition: str = ""
    favored_skills: list[str] = Field(default_factory=list)


class ArchiveWritebackPayload(BaseModel):
    name: str
    occupation: str
    age: int
    background: str
    portrait_summary: str = ""
    concept: str = ""
    occupation_detail: str = ""
    specialty: str = ""
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


class AnswerNormalizer:
    def normalize_slot(
        self, *, slot: str, raw: str, current_answers: dict[str, str] | None = None
    ) -> dict[str, str]:
        current_answers = current_answers or {}
        text = _normalize_free_text(raw)
        if slot == "name":
            return {"name": text}
        if slot == "concept":
            payload = {"concept": text}
            payload.update(_extract_concept_fields(text))
            return payload
        if slot == "age":
            return {"age": _normalize_age(text)}
        if slot == "occupation":
            return {"occupation": _normalize_occupation(text)}
        if slot == "favored_skills":
            skills = _normalize_skill_list(text)
            return {"favored_skills": ", ".join(skills)}
        return {slot: text}

    def normalized_contract(self, answers: dict[str, str]) -> NormalizedBuilderAnswers:
        return NormalizedBuilderAnswers(
            name=answers.get("name", ""),
            concept=answers.get("concept", ""),
            age=answers.get("age", ""),
            occupation=answers.get("occupation", ""),
            key_past_event=answers.get("key_past_event", ""),
            life_goal=answers.get("life_goal", ""),
            weakness=answers.get("weakness", ""),
            core_belief=answers.get("core_belief", ""),
            important_person=answers.get("important_person", ""),
            significant_location=answers.get("significant_location", ""),
            treasured_possession=answers.get("treasured_possession", ""),
            disposition=answers.get("disposition", ""),
            favored_skills=_normalize_skill_list(answers.get("favored_skills", "")),
        )

    def writeback_payload(
        self,
        *,
        answers: dict[str, str],
        semantic_fields: dict[str, str],
    ) -> ArchiveWritebackPayload:
        normalized = self.normalized_contract(answers)
        return ArchiveWritebackPayload(
            name=normalized.name,
            occupation=normalized.occupation,
            age=int(normalized.age),
            background=_build_background(answers),
            occupation_detail=semantic_fields.get("occupation_detail", ""),
            specialty=semantic_fields.get("specialty", ""),
            career_arc=semantic_fields.get("career_arc", ""),
            core_belief=normalized.core_belief
            or semantic_fields.get("core_belief", ""),
            material_desire=semantic_fields.get("material_desire", ""),
            fear_or_taboo=semantic_fields.get("fear_or_taboo", ""),
            important_tie=semantic_fields.get("important_tie", ""),
            birthplace="",
            residence="",
            family="",
            education_background="",
            important_person=normalized.important_person
            or semantic_fields.get("important_person", ""),
            significant_location=normalized.significant_location
            or semantic_fields.get("significant_location", ""),
            treasured_possession=normalized.treasured_possession
            or semantic_fields.get("treasured_possession", ""),
            trait_notes=semantic_fields.get("trait_notes", ""),
            scars_and_injuries=semantic_fields.get("scars_and_injuries", ""),
            phobias_and_manias=semantic_fields.get("phobias_and_manias", ""),
            disposition=normalized.disposition,
            favored_skills=normalized.favored_skills,
            portrait_summary=_build_portrait_summary(answers),
            concept=normalized.concept,
            life_goal=normalized.life_goal,
            weakness=normalized.weakness,
            key_past_event=normalized.key_past_event,
        )


class InterviewPlanner(Protocol):
    async def next_question(self, session: BuilderSession) -> BuilderQuestionChoice: ...


class ArchiveSemanticExtractor(Protocol):
    async def extract(self, session: BuilderSession) -> dict[str, str]: ...


class CharacterSheetSynthesis(BaseModel):
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
    disposition: str = ""
    favored_skills: list[str] = Field(default_factory=list)
    portrait_summary: str = ""
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


class CharacterSheetSynthesizer(Protocol):
    async def synthesize(
        self, session: BuilderSession, semantic_fields: dict[str, str]
    ) -> CharacterSheetSynthesis: ...


class HeuristicInterviewPlanner:
    async def next_question(self, session: BuilderSession) -> BuilderQuestionChoice:
        concept = session.answers.get("concept", "")
        occupation = session.answers.get("occupation", "")
        if "key_past_event" not in session.answers:
            return BuilderQuestionChoice(
                slot="key_past_event",
                question=_past_event_question(concept, occupation),
            )
        if "life_goal" not in session.answers:
            return BuilderQuestionChoice(
                slot="life_goal",
                question="如果这一切还没把他压垮，他现在最想达成的人生目标是什么？",
            )
        if "weakness" not in session.answers:
            return BuilderQuestionChoice(
                slot="weakness",
                question="他最致命的弱点、劣势或坏习惯是什么？",
            )
        if "core_belief" not in session.answers:
            return BuilderQuestionChoice(
                slot="core_belief",
                question="如果别人说这一切都是他的错，他会怎么替自己辩护？",
            )
        return BuilderQuestionChoice(
            slot="important_person",
            question="如果还要再补一笔人物关系，在他心里最重要的那个人是谁？",
        )


class ModelGuidedInterviewPlanner:
    def __init__(
        self, *, model_client, fallback: InterviewPlanner | None = None
    ) -> None:
        self._model_client = model_client
        self._fallback = fallback or HeuristicInterviewPlanner()

    async def next_question(self, session: BuilderSession) -> BuilderQuestionChoice:
        missing_slots = [
            slot for slot in REQUIRED_INTERVIEW_SLOTS if not session.answers.get(slot)
        ]
        if not missing_slots:
            return BuilderQuestionChoice(
                slot="important_person",
                question="如果还要再补一笔人物关系，在他心里最重要的那个人是谁？",
            )
        request = ModelRequest(
            system_prompt=(
                "你是克苏鲁的呼唤的 Keeper，正在引导一位新调查员完成建卡访谈。"
                "基于已知的人物信息，选择下一条最有价值的追问。"
                "一次只问一个问题，像 Keeper 了解角色那样自然地提问——不要重复已知信息，不要谈属性数值，不要输出解释。"
                "只返回 JSON，键为 slot 和 question。"
                f"slot 必须是这些候选之一: {', '.join(missing_slots)}。"
            ),
            user_prompt=(
                "已知信息:\n"
                f"{json.dumps(session.answers, ensure_ascii=False)}\n"
                f"当前缺失槽位: {json.dumps(missing_slots, ensure_ascii=False)}"
            ),
            response_format={"type": "json_object"},
        )
        try:
            response = await self._model_client.call_router(request)
            payload = json.loads(response.content)
            slot = str(payload.get("slot", "")).strip()
            question = str(payload.get("question", "")).strip()
            if slot in missing_slots and question:
                return BuilderQuestionChoice(slot=slot, question=question)
        except Exception:
            pass
        return await self._fallback.next_question(session)


class HeuristicArchiveSemanticExtractor:
    async def extract(self, session: BuilderSession) -> dict[str, str]:
        answers = session.answers
        return {
            "occupation_detail": _build_occupation_detail(answers),
            "specialty": _infer_specialty(answers),
            "career_arc": _infer_career_arc(answers),
            "core_belief": _infer_core_belief(answers),
            "material_desire": _infer_material_desire(answers),
            "fear_or_taboo": _infer_fear_or_taboo(answers),
            "important_tie": _infer_important_tie(answers),
            "important_person": answers.get("important_person", "")
            or _infer_important_person(answers),
            "significant_location": answers.get("significant_location", "")
            or _infer_significant_location(answers),
            "treasured_possession": answers.get("treasured_possession", "")
            or _infer_treasured_possession(answers),
            "trait_notes": _infer_trait_notes(answers),
            "scars_and_injuries": _infer_scars_and_injuries(answers),
            "phobias_and_manias": _infer_phobias_and_manias(answers),
        }


class ModelGuidedArchiveSemanticExtractor:
    def __init__(
        self, *, model_client, fallback: ArchiveSemanticExtractor | None = None
    ) -> None:
        self._model_client = model_client
        self._fallback = fallback or HeuristicArchiveSemanticExtractor()

    async def extract(self, session: BuilderSession) -> dict[str, str]:
        request = ModelRequest(
            system_prompt=(
                "你是克苏鲁的呼唤的 Keeper，正在为刚刚完成访谈的调查员整理长期档案。"
                "根据采访答案，提取适合长期档案保存的人物语义字段。"
                "不要编造采访里完全不存在的事实。"
                "可以做适度归纳，但必须忠于原意。"
                "只返回 JSON，不要解释。"
                "返回键限定为: occupation_detail, specialty, career_arc, core_belief, material_desire, fear_or_taboo, important_tie, "
                "important_person, significant_location, treasured_possession, trait_notes, scars_and_injuries, phobias_and_manias。"
                "值必须是简洁中文字符串；没有把握就返回空字符串。"
            ),
            user_prompt=f"采访答案:\n{json.dumps(session.answers, ensure_ascii=False)}",
            response_format={"type": "json_object"},
        )
        try:
            response = await self._model_client.call_router(request)
            payload = json.loads(response.content)
            allowed = {
                "occupation_detail",
                "specialty",
                "career_arc",
                "core_belief",
                "material_desire",
                "fear_or_taboo",
                "important_tie",
                "important_person",
                "significant_location",
                "treasured_possession",
                "trait_notes",
                "scars_and_injuries",
                "phobias_and_manias",
            }
            normalized = {
                key: str(payload.get(key, "") or "").strip() for key in allowed
            }
            if any(normalized.values()):
                return normalized
        except Exception:
            pass
        return await self._fallback.extract(session)


class HeuristicCharacterSheetSynthesizer:
    async def synthesize(
        self, session: BuilderSession, semantic_fields: dict[str, str]
    ) -> CharacterSheetSynthesis:
        answers = session.answers
        return CharacterSheetSynthesis(
            occupation_detail=semantic_fields.get("occupation_detail", "")
            or _build_occupation_detail(answers),
            specialty=semantic_fields.get("specialty", "") or _infer_specialty(answers),
            background=_build_background_summary(answers),
            career_arc=semantic_fields.get("career_arc", "")
            or _infer_career_arc(answers),
            key_past_event=answers.get("key_past_event", ""),
            core_belief=semantic_fields.get("core_belief", "")
            or _infer_core_belief(answers),
            life_goal=answers.get("life_goal", ""),
            material_desire=semantic_fields.get("material_desire", "")
            or _infer_material_desire(answers),
            weakness=answers.get("weakness", ""),
            fear_or_taboo=semantic_fields.get("fear_or_taboo", "")
            or _infer_fear_or_taboo(answers),
            important_tie=semantic_fields.get("important_tie", "")
            or _infer_important_tie(answers),
            important_person=semantic_fields.get("important_person", "")
            or answers.get("important_person", ""),
            significant_location=semantic_fields.get("significant_location", "")
            or answers.get("significant_location", ""),
            treasured_possession=semantic_fields.get("treasured_possession", "")
            or answers.get("treasured_possession", ""),
            trait_notes=semantic_fields.get("trait_notes", "")
            or _infer_trait_notes(answers),
            scars_and_injuries=semantic_fields.get("scars_and_injuries", "")
            or _infer_scars_and_injuries(answers),
            phobias_and_manias=semantic_fields.get("phobias_and_manias", "")
            or _infer_phobias_and_manias(answers),
            disposition=answers.get("disposition", ""),
            favored_skills=_normalize_skill_list(answers.get("favored_skills", "")),
            portrait_summary=_build_portrait_summary(answers),
        )


class ModelGuidedCharacterSheetSynthesizer:
    def __init__(
        self, *, model_client, fallback: CharacterSheetSynthesizer | None = None
    ) -> None:
        self._model_client = model_client
        self._fallback = fallback or HeuristicCharacterSheetSynthesizer()

    async def synthesize(
        self, session: BuilderSession, semantic_fields: dict[str, str]
    ) -> CharacterSheetSynthesis:
        request = ModelRequest(
            system_prompt=(
                "你是克苏鲁的呼唤的 Keeper，正在将一位新调查员的访谈内容整理为完整的角色档案。"
                "根据采访答案和已有语义字段，把人物整理为更连贯的长期档案。"
                "不要编造采访里没有的具体事实，不要发明新职业，不要改动明确给出的年龄和职业。"
                "输出必须是 JSON，对每个字段给出简洁中文；不确定就留空。"
                "favored_skills 必须是字符串数组。"
            ),
            user_prompt=(
                "采访答案:\n"
                f"{json.dumps(session.answers, ensure_ascii=False)}\n"
                "已有语义字段:\n"
                f"{json.dumps(semantic_fields, ensure_ascii=False)}\n"
                "请输出这些字段：occupation_detail, specialty, background, career_arc, key_past_event, "
                "core_belief, life_goal, material_desire, weakness, fear_or_taboo, important_tie, disposition, "
                "favored_skills, portrait_summary, birthplace, residence, family, education_background, "
                "important_person, significant_location, treasured_possession, trait_notes, scars_and_injuries, phobias_and_manias。"
            ),
            response_format={"type": "json_object"},
        )
        try:
            response = await self._model_client.call_router(request)
            payload = json.loads(response.content)
            normalized = {
                key: payload.get(key, [] if key == "favored_skills" else "")
                for key in CharacterSheetSynthesis.model_fields
            }
            if isinstance(normalized["favored_skills"], str):
                normalized["favored_skills"] = _normalize_skill_list(
                    normalized["favored_skills"]
                )
            elif isinstance(normalized["favored_skills"], list):
                normalized["favored_skills"] = [
                    str(item).strip()
                    for item in normalized["favored_skills"]
                    if str(item).strip()
                ]
            synthesis = CharacterSheetSynthesis.model_validate(normalized)
            if (
                synthesis.background
                or synthesis.career_arc
                or synthesis.portrait_summary
            ):
                return synthesis
        except Exception:
            pass
        return await self._fallback.synthesize(session, semantic_fields)


class SectionNormalizer:
    def to_writeback(
        self,
        *,
        answers: dict[str, str],
        synthesis: CharacterSheetSynthesis,
        answer_normalizer: AnswerNormalizer,
    ) -> ArchiveWritebackPayload:
        normalized = answer_normalizer.normalized_contract(answers)
        explicit_skills = normalized.favored_skills
        return ArchiveWritebackPayload(
            name=normalized.name,
            occupation=normalized.occupation,
            age=int(normalized.age),
            background=synthesis.background or _build_background_summary(answers),
            occupation_detail=synthesis.occupation_detail,
            specialty=synthesis.specialty,
            career_arc=synthesis.career_arc,
            key_past_event=normalized.key_past_event or synthesis.key_past_event,
            core_belief=synthesis.core_belief,
            life_goal=normalized.life_goal or synthesis.life_goal,
            material_desire=synthesis.material_desire,
            weakness=normalized.weakness or synthesis.weakness,
            fear_or_taboo=synthesis.fear_or_taboo,
            important_tie=synthesis.important_tie,
            important_person=normalized.important_person
            or synthesis.important_person
            or synthesis.important_tie,
            significant_location=normalized.significant_location
            or synthesis.significant_location,
            treasured_possession=normalized.treasured_possession
            or synthesis.treasured_possession,
            trait_notes=synthesis.trait_notes
            or normalized.disposition
            or synthesis.disposition,
            scars_and_injuries=synthesis.scars_and_injuries,
            phobias_and_manias=synthesis.phobias_and_manias,
            disposition=normalized.disposition or synthesis.disposition,
            favored_skills=explicit_skills or synthesis.favored_skills,
            portrait_summary=synthesis.portrait_summary
            or _build_portrait_summary(answers),
            concept=normalized.concept,
            birthplace=synthesis.birthplace,
            residence=synthesis.residence,
            family=synthesis.family,
            education_background=synthesis.education_background,
        )


class ConversationalCharacterBuilder:
    INTRO_QUESTION = "让我先了解一下这位即将踏入黑暗的调查员。请先告诉我他的名字。"
    CONCEPT_QUESTION = "告诉我，这是个什么样的人？用一句话勾勒他的轮廓——比如'38岁的落魄临床医生'，或者'被过去追逐的退伍老兵'。"

    def __init__(
        self,
        *,
        archive_repository: InvestigatorArchiveRepository,
        roll_provider=None,
        interview_planner: InterviewPlanner | None = None,
        semantic_extractor: ArchiveSemanticExtractor | None = None,
        answer_normalizer: AnswerNormalizer | None = None,
        synthesizer: CharacterSheetSynthesizer | None = None,
        section_normalizer: SectionNormalizer | None = None,
    ) -> None:
        self._archive_repository = archive_repository
        self._roll_provider = roll_provider or self._default_roll_provider
        self._interview_planner = interview_planner or HeuristicInterviewPlanner()
        self._semantic_extractor = (
            semantic_extractor or HeuristicArchiveSemanticExtractor()
        )
        self._answer_normalizer = answer_normalizer or AnswerNormalizer()
        self._synthesizer = synthesizer or HeuristicCharacterSheetSynthesizer()
        self._section_normalizer = section_normalizer or SectionNormalizer()
        self._sessions: dict[str, BuilderSession] = {}

    def start(self, *, user_id: str, visibility: str = "private") -> str:
        if self._archive_repository.active_profile(user_id) is not None:
            return "你已有激活档案。请先归档或替换当前主角色，再开始新的建卡。"
        self._sessions[user_id] = BuilderSession(user_id=user_id, visibility=visibility)
        return self.INTRO_QUESTION

    async def answer(
        self, *, user_id: str, answer: str
    ) -> tuple[str, InvestigatorArchiveProfile | None]:
        session = self._sessions[user_id]
        if session.stage == "finalize":
            return await self._finalize_from_portrait(session=session, answer=answer)
        slot = session.current_slot
        answer = answer.strip()
        session.raw_answers[slot] = answer
        session.answers.update(
            self._answer_normalizer.normalize_slot(
                slot=slot, raw=answer, current_answers=session.answers
            )
        )

        if slot == "name":
            session.current_slot = "concept"
            session.asked_slots.append("concept")
            return self.CONCEPT_QUESTION, None

        next_question = await self._next_question(session)
        if next_question is not None:
            session.current_slot = next_question.slot
            session.asked_slots.append(next_question.slot)
            return next_question.question, None

        session.stage = "finalize"
        semantic_fields = await self._semantic_extractor.extract(session)
        synthesis = await self._synthesizer.synthesize(session, semantic_fields)
        payload = self._section_normalizer.to_writeback(
            answers=session.answers,
            synthesis=synthesis,
            answer_normalizer=self._answer_normalizer,
        )
        session.pending_writeback = payload
        session.portrait_summary = _build_interview_portrait(payload)
        return _build_finalization_prompt(session), None

    def has_session(self, user_id: str) -> bool:
        return user_id in self._sessions

    async def _next_question(
        self, session: BuilderSession
    ) -> BuilderQuestionChoice | None:
        if not session.answers.get("age"):
            return BuilderQuestionChoice(
                slot="age",
                question="这位调查员看起来有多大？岁月在他身上留下了什么痕迹？",
            )
        if not session.answers.get("occupation"):
            return BuilderQuestionChoice(
                slot="occupation", question="在成为调查员之前，他以什么为生？"
            )
        missing_dynamic = [
            slot for slot in REQUIRED_INTERVIEW_SLOTS if not session.answers.get(slot)
        ]
        if not missing_dynamic:
            return None
        return await self._interview_planner.next_question(session)

    async def _finalize_from_portrait(
        self, *, session: BuilderSession, answer: str
    ) -> tuple[str, InvestigatorArchiveProfile | None]:
        text = _normalize_free_text(answer)
        if not text:
            return _build_finalization_prompt(session), None

        if _is_finalize_reply(text):
            assert session.pending_writeback is not None
            profile = self._archive_repository.create_profile(
                user_id=session.user_id,
                generation=self._generate_stats(),
                **session.pending_writeback.model_dump(),
            )
            del self._sessions[session.user_id]
            return f"建卡完成：{profile.name} / {profile.coc.occupation}", profile

        if _looks_like_skill_list(text):
            skills = _normalize_skill_list(text)
            session.answers["favored_skills"] = ", ".join(skills)
            if session.pending_writeback is not None:
                session.pending_writeback.favored_skills = skills
            assert session.pending_writeback is not None
            profile = self._archive_repository.create_profile(
                user_id=session.user_id,
                generation=self._generate_stats(),
                **session.pending_writeback.model_dump(),
            )
            del self._sessions[session.user_id]
            return f"建卡完成：{profile.name} / {profile.coc.occupation}", profile

        _apply_finalization_note(session, text)
        semantic_fields = await self._semantic_extractor.extract(session)
        synthesis = await self._synthesizer.synthesize(session, semantic_fields)
        session.pending_writeback = self._section_normalizer.to_writeback(
            answers=session.answers,
            synthesis=synthesis,
            answer_normalizer=self._answer_normalizer,
        )
        session.portrait_summary = _build_interview_portrait(session.pending_writeback)
        return _build_finalization_prompt(session), None

    def _generate_stats(self) -> dict[str, int]:
        return {
            "str": int(self._roll_provider("3d6*5")),
            "con": int(self._roll_provider("3d6*5")),
            "dex": int(self._roll_provider("3d6*5")),
            "app": int(self._roll_provider("3d6*5")),
            "pow": int(self._roll_provider("3d6*5")),
            "siz": int(self._roll_provider("2d6+6*5")),
            "int": int(self._roll_provider("2d6+6*5")),
            "edu": int(self._roll_provider("2d6+6*5")),
            "luck": int(self._roll_provider("luck")),
        }

    def _default_roll_provider(self, expr: str) -> int:
        import random

        if expr == "3d6*5":
            return sum(random.randint(1, 6) for _ in range(3)) * 5
        if expr == "2d6+6*5":
            return (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
        if expr == "luck":
            return sum(random.randint(1, 6) for _ in range(3)) * 5
        raise KeyError(expr)


REQUIRED_INTERVIEW_SLOTS = [
    "key_past_event",
    "life_goal",
    "weakness",
    "core_belief",
]
DOWNFALL_KEYWORDS = (
    "落魄",
    "潦倒",
    "失意",
    "破产",
    "酗酒",
    "停职",
    "离婚",
    "退学",
    "失业",
)


def _extract_concept_fields(concept: str) -> dict[str, str]:
    payload: dict[str, str] = {"concept": concept}
    age_match = re.search(r"(\d{1,2})\s*岁", concept)
    if age_match:
        payload["age"] = age_match.group(1)

    normalized = concept
    normalized = re.sub(r"^\s*我(?:是|想扮演)?(?:一个|一位)?", "", normalized)
    normalized = re.sub(r"\d{1,2}\s*岁(?:的)?", "", normalized)
    normalized = normalized.strip(" ，。；、")
    if "的" in normalized:
        normalized = normalized.split("的")[-1]
    normalized = re.sub(
        r"^(?:落魄|潦倒|失意|疲惫|年轻|年老|酗酒|偏执|孤僻|失业|没落)+", "", normalized
    ).strip()
    if normalized:
        payload["occupation"] = normalized
    return payload


def _normalize_free_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw).strip()


def _normalize_age(raw: str) -> str:
    match = re.search(r"(\d{1,2})", raw)
    return match.group(1) if match else raw.strip()


def _normalize_occupation(raw: str) -> str:
    normalized = _normalize_free_text(raw)
    normalized = re.sub(r"^\s*我(?:是|想扮演)?(?:一个|一位)?", "", normalized)
    normalized = normalized.strip(" ，。；、")
    return normalized


def _normalize_skill_list(raw: str) -> list[str]:
    text = _normalize_free_text(raw)
    if not text:
        return []
    text = (
        text.replace("，", ",").replace("、", ",").replace("；", ",").replace("/", ",")
    )
    return [item.strip() for item in text.split(",") if item.strip()]


def _past_event_question(concept: str, occupation: str) -> str:
    if any(keyword in concept for keyword in DOWNFALL_KEYWORDS):
        return "你为什么会落到这一步？最近究竟发生了什么，把他拖进了现在的困境？"
    if "医生" in occupation:
        return "在他的行医生涯里，哪件事最深地改变了他，甚至让他开始怀疑自己？"
    if "记者" in occupation:
        return "哪次采访或报道最深地改变了他，甚至让他付出了代价？"
    if "警察" in occupation or "侦探" in occupation:
        return "哪件旧案一直卡在他心里，直到现在都没真正过去？"
    return "过去到底发生过什么，才让他变成了今天这个样子？"


def _build_background(answers: dict[str, str]) -> str:
    snippets = [answers.get("concept", ""), answers.get("key_past_event", "")]
    return " ".join(part.strip() for part in snippets if part and part.strip())


def _build_background_summary(answers: dict[str, str]) -> str:
    concept = answers.get("concept", "").strip()
    event = answers.get("key_past_event", "").strip()
    goal = answers.get("life_goal", "").strip()
    if concept and event and goal:
        return f"{concept}。曾因{event}而被推到人生的低谷，如今仍想{goal}"
    if concept and event:
        return f"{concept}。他的命运被这样一件事改写：{event}"
    return _build_background(answers)


def _build_occupation_detail(answers: dict[str, str]) -> str:
    concept = answers.get("concept", "")
    occupation = answers.get("occupation", "")
    if occupation and occupation not in concept:
        return occupation
    return concept or occupation


def _infer_specialty(answers: dict[str, str]) -> str:
    occupation = answers.get("occupation", "")
    favored = answers.get("favored_skills", "")
    source = " ".join(
        [
            occupation,
            answers.get("key_past_event", ""),
            favored,
            answers.get("concept", ""),
        ]
    )
    if "脑" in source or "神经" in source:
        return "神经外科"
    if "医生" in occupation or "医学" in favored:
        return "临床医学"
    if "记者" in occupation:
        return "调查报道"
    if "侦探" in occupation or "警察" in occupation:
        return "刑事调查"
    return ""


def _infer_career_arc(answers: dict[str, str]) -> str:
    concept = answers.get("concept", "")
    event = answers.get("key_past_event", "")
    if concept and event:
        return f"{concept}；后来因为{event}"
    return event or concept


def _infer_core_belief(answers: dict[str, str]) -> str:
    combined = " ".join(answers.values())
    if "不是我的错" in combined or "我是在救人" in combined:
        return "结果比规则更重要，我首先是在救人。"
    if "真相" in combined:
        return "真相值得追到底。"
    return ""


def _infer_material_desire(answers: dict[str, str]) -> str:
    goal = answers.get("life_goal", "")
    if "钱" in goal or "发财" in goal:
        return goal
    return ""


def _infer_fear_or_taboo(answers: dict[str, str]) -> str:
    weakness = answers.get("weakness", "")
    if "酗酒" in weakness:
        return "害怕再次在失控中毁掉别人，也害怕承认自己已经失控。"
    return ""


def _infer_important_tie(answers: dict[str, str]) -> str:
    event = answers.get("key_past_event", "")
    if "病人" in event or "患者" in event:
        return "那位改变他职业命运的病人与其家属。"
    return ""


def _infer_important_person(answers: dict[str, str]) -> str:
    return answers.get("important_person", "")


def _infer_significant_location(answers: dict[str, str]) -> str:
    return answers.get("significant_location", "")


def _infer_treasured_possession(answers: dict[str, str]) -> str:
    return answers.get("treasured_possession", "")


def _infer_trait_notes(answers: dict[str, str]) -> str:
    disposition = answers.get("disposition", "").strip()
    weakness = answers.get("weakness", "").strip()
    if disposition and weakness:
        return f"{disposition}；同时也{weakness}"
    return disposition or ""


def _infer_scars_and_injuries(answers: dict[str, str]) -> str:
    event = answers.get("key_past_event", "")
    if any(
        keyword in event
        for keyword in ("手术", "枪", "爆炸", "车祸", "烧伤", "断", "伤")
    ):
        return "可能留下与那段过往有关的旧伤，但调查员本人并不愿主动提起。"
    return ""


def _infer_phobias_and_manias(answers: dict[str, str]) -> str:
    combined = " ".join(answers.values())
    if "酗酒" in combined:
        return "在压力或愧疚下容易借酒失控。"
    if "真相" in combined and "执" in combined:
        return "对某些真相有近乎偏执的追逐倾向。"
    return ""


def _build_portrait_summary(answers: dict[str, str]) -> str:
    fragments = [answers.get("occupation", "调查员")]
    if answers.get("concept"):
        fragments.append(answers["concept"])
    if answers.get("life_goal"):
        fragments.append(f"人生目标：{answers['life_goal']}")
    if answers.get("weakness"):
        fragments.append(f"弱点：{answers['weakness']}")
    if answers.get("disposition"):
        fragments.append(f"处事方式：{answers['disposition']}")
    return "。".join(item.strip("。 ") for item in fragments if item).strip()


def _build_interview_portrait(payload: ArchiveWritebackPayload) -> str:
    lines = [
        "【人物画像】",
        f"{payload.name} / {payload.occupation} / {payload.age}岁",
        f"人物骨架：{payload.concept or '未记录'}",
        f"关键过往：{payload.key_past_event or '未记录'}",
        f"人生目标：{payload.life_goal or '未记录'}",
        f"弱点：{payload.weakness or '未记录'}",
        f"核心信念：{payload.core_belief or '未记录'}",
    ]
    if payload.important_person:
        lines.append(f"重要之人：{payload.important_person}")
    if payload.specialty:
        lines.append(f"专长倾向：{payload.specialty}")
    return "\n".join(lines)


def _build_finalization_prompt(session: BuilderSession) -> str:
    return (
        f"{session.portrait_summary}\n\n"
        "访谈到此告一段落。这就是你即将带入黑暗的调查员。\n"
        "如果这份人物画像没问题，回复 `定卡` 或 `按人物来`。\n"
        "如果你想直接指定这人最擅长的 2-4 项技能，直接回复技能名并用逗号分隔。\n"
        "如果你还想补一笔人物信息，直接回复那一句，我会先更新人物画像。"
    )


def _is_finalize_reply(text: str) -> bool:
    return text in {"定卡", "继续定卡", "确认", "按人物来", "开始定卡"}


def _looks_like_skill_list(text: str) -> bool:
    lowered = text.lower()
    if lowered.startswith("技能:") or lowered.startswith("技能："):
        return True
    if not any(sep in text for sep in (",", "，", "、", ";", "；", "/")):
        return False
    items = _normalize_skill_list(text)
    if not 2 <= len(items) <= 4:
        return False
    return all(
        len(item) <= 8
        and not any(
            token in item for token in ("。", "！", "？", " ", "我", "他", "她")
        )
        for item in items
    )


def _apply_finalization_note(session: BuilderSession, text: str) -> None:
    if not session.answers.get("important_person"):
        session.answers["important_person"] = text
        return
    if not session.answers.get("significant_location"):
        session.answers["significant_location"] = text
        return
    if not session.answers.get("treasured_possession"):
        session.answers["treasured_possession"] = text
        return
    existing = session.answers.get("trait_notes", "")
    session.answers["trait_notes"] = f"{existing}；{text}".strip("；")
