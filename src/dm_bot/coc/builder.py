from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Protocol

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
    answers: dict[str, str] = field(default_factory=dict)
    current_slot: str = "name"
    asked_slots: list[str] = field(default_factory=lambda: ["name"])


class InterviewPlanner(Protocol):
    async def next_question(self, session: BuilderSession) -> BuilderQuestionChoice: ...


class ArchiveSemanticExtractor(Protocol):
    async def extract(self, session: BuilderSession) -> dict[str, str]: ...


class HeuristicInterviewPlanner:
    async def next_question(self, session: BuilderSession) -> BuilderQuestionChoice:
        concept = session.answers.get("concept", "")
        occupation = session.answers.get("occupation", "")
        if "key_past_event" not in session.answers:
            return BuilderQuestionChoice(slot="key_past_event", question=_past_event_question(concept, occupation))
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
        if "disposition" not in session.answers:
            return BuilderQuestionChoice(
                slot="disposition",
                question="别人通常会怎么评价他的处事方式？",
            )
        return BuilderQuestionChoice(
            slot="favored_skills",
            question="列出 2-4 个他最拿手的技能，用逗号分隔。",
        )


class ModelGuidedInterviewPlanner:
    def __init__(self, *, model_client, fallback: InterviewPlanner | None = None) -> None:
        self._model_client = model_client
        self._fallback = fallback or HeuristicInterviewPlanner()

    async def next_question(self, session: BuilderSession) -> BuilderQuestionChoice:
        missing_slots = [slot for slot in DYNAMIC_SLOT_ORDER if not session.answers.get(slot)]
        if not missing_slots:
            return BuilderQuestionChoice(slot="favored_skills", question="列出 2-4 个他最拿手的技能，用逗号分隔。")
        request = ModelRequest(
            system_prompt=(
                "你是克苏鲁的呼唤建卡采访器。"
                "基于已知角色信息，选择下一条最有价值的追问。"
                "一次只能问一个问题。不要重复已知信息，不要谈属性数值，不要输出解释。"
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
        }


class ModelGuidedArchiveSemanticExtractor:
    def __init__(self, *, model_client, fallback: ArchiveSemanticExtractor | None = None) -> None:
        self._model_client = model_client
        self._fallback = fallback or HeuristicArchiveSemanticExtractor()

    async def extract(self, session: BuilderSession) -> dict[str, str]:
        request = ModelRequest(
            system_prompt=(
                "你是克苏鲁的呼唤人物档案归档器。"
                "根据采访答案，提取适合长期档案保存的人物语义字段。"
                "不要编造采访里完全不存在的事实。"
                "可以做适度归纳，但必须忠于原意。"
                "只返回 JSON，不要解释。"
                '返回键限定为: occupation_detail, specialty, career_arc, core_belief, material_desire, fear_or_taboo, important_tie。'
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
            }
            normalized = {
                key: str(payload.get(key, "") or "").strip()
                for key in allowed
            }
            if any(normalized.values()):
                return normalized
        except Exception:
            pass
        return await self._fallback.extract(session)


class ConversationalCharacterBuilder:
    INTRO_QUESTION = "先给这位调查员起个名字。"
    CONCEPT_QUESTION = "用一句短话描述这个人的人物骨架，例如“38岁的落魄临床医生”。"

    def __init__(
        self,
        *,
        archive_repository: InvestigatorArchiveRepository,
        roll_provider=None,
        interview_planner: InterviewPlanner | None = None,
        semantic_extractor: ArchiveSemanticExtractor | None = None,
    ) -> None:
        self._archive_repository = archive_repository
        self._roll_provider = roll_provider or self._default_roll_provider
        self._interview_planner = interview_planner or HeuristicInterviewPlanner()
        self._semantic_extractor = semantic_extractor or HeuristicArchiveSemanticExtractor()
        self._sessions: dict[str, BuilderSession] = {}

    def start(self, *, user_id: str, visibility: str = "private") -> str:
        self._sessions[user_id] = BuilderSession(user_id=user_id, visibility=visibility)
        return self.INTRO_QUESTION

    async def answer(self, *, user_id: str, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]:
        session = self._sessions[user_id]
        slot = session.current_slot
        answer = answer.strip()
        session.answers[slot] = answer

        if slot == "name":
            session.current_slot = "concept"
            session.asked_slots.append("concept")
            return self.CONCEPT_QUESTION, None

        if slot == "concept":
            session.answers.update(_extract_concept_fields(answer))

        next_question = await self._next_question(session)
        if next_question is not None:
            session.current_slot = next_question.slot
            session.asked_slots.append(next_question.slot)
            return next_question.question, None

        semantic_fields = await self._semantic_extractor.extract(session)
        profile = self._archive_repository.create_profile(
            user_id=user_id,
            name=session.answers["name"],
            occupation=session.answers["occupation"],
            age=int(session.answers["age"]),
            background=_build_background(session.answers),
            occupation_detail=semantic_fields.get("occupation_detail", ""),
            specialty=semantic_fields.get("specialty", ""),
            career_arc=semantic_fields.get("career_arc", ""),
            core_belief=semantic_fields.get("core_belief", ""),
            material_desire=semantic_fields.get("material_desire", ""),
            fear_or_taboo=semantic_fields.get("fear_or_taboo", ""),
            important_tie=semantic_fields.get("important_tie", ""),
            disposition=session.answers.get("disposition", ""),
            favored_skills=[item.strip() for item in session.answers.get("favored_skills", "").split(",") if item.strip()],
            portrait_summary=_build_portrait_summary(session.answers),
            concept=session.answers.get("concept", ""),
            life_goal=session.answers.get("life_goal", ""),
            weakness=session.answers.get("weakness", ""),
            key_past_event=session.answers.get("key_past_event", ""),
            generation=self._generate_stats(),
        )
        del self._sessions[user_id]
        return f"建卡完成：{profile.name} / {profile.coc.occupation}", profile

    def has_session(self, user_id: str) -> bool:
        return user_id in self._sessions

    async def _next_question(self, session: BuilderSession) -> BuilderQuestionChoice | None:
        if not session.answers.get("age"):
            return BuilderQuestionChoice(slot="age", question="他的年龄是多少？")
        if not session.answers.get("occupation"):
            return BuilderQuestionChoice(slot="occupation", question="他的职业是什么？尽量用 COC 里能落地的现实职业描述。")
        missing_dynamic = [slot for slot in DYNAMIC_SLOT_ORDER if not session.answers.get(slot)]
        if not missing_dynamic:
            return None
        return await self._interview_planner.next_question(session)

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


DYNAMIC_SLOT_ORDER = ["key_past_event", "life_goal", "weakness", "disposition", "favored_skills"]
DOWNFALL_KEYWORDS = ("落魄", "潦倒", "失意", "破产", "酗酒", "停职", "离婚", "退学", "失业")


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
    normalized = re.sub(r"^(?:落魄|潦倒|失意|疲惫|年轻|年老|酗酒|偏执|孤僻|失业|没落)+", "", normalized).strip()
    if normalized:
        payload["occupation"] = normalized
    return payload


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


def _build_occupation_detail(answers: dict[str, str]) -> str:
    concept = answers.get("concept", "")
    occupation = answers.get("occupation", "")
    if occupation and occupation not in concept:
        return occupation
    return concept or occupation


def _infer_specialty(answers: dict[str, str]) -> str:
    occupation = answers.get("occupation", "")
    favored = answers.get("favored_skills", "")
    source = " ".join([occupation, answers.get("key_past_event", ""), favored, answers.get("concept", "")])
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
