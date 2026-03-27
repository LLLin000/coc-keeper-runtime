from __future__ import annotations

from dataclasses import dataclass, field

from dm_bot.coc.archive import InvestigatorArchiveProfile, InvestigatorArchiveRepository


@dataclass
class BuilderSession:
    user_id: str
    visibility: str = "private"
    answers: dict[str, str] = field(default_factory=dict)
    step_index: int = 0


class ConversationalCharacterBuilder:
    STEPS: list[tuple[str, str]] = [
        ("name", "先给这位调查员起个名字。"),
        ("occupation", "他的职业是什么？尽量用 COC 里能落地的现实职业描述。"),
        ("age", "他的年龄是多少？"),
        ("background", "用一句话描述他的生活背景或过往经历。"),
        ("disposition", "再用一句话说说他的性格或处事方式。"),
        ("favored_skills", "列出 2-4 个你最希望他擅长的技能，用逗号分隔。"),
    ]

    def __init__(self, *, archive_repository: InvestigatorArchiveRepository, roll_provider=None) -> None:
        self._archive_repository = archive_repository
        self._roll_provider = roll_provider or self._default_roll_provider
        self._sessions: dict[str, BuilderSession] = {}

    def start(self, *, user_id: str, visibility: str = "private") -> str:
        self._sessions[user_id] = BuilderSession(user_id=user_id, visibility=visibility)
        return self.STEPS[0][1]

    def answer(self, *, user_id: str, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]:
        session = self._sessions[user_id]
        key, _ = self.STEPS[session.step_index]
        session.answers[key] = answer.strip()
        session.step_index += 1
        if session.step_index < len(self.STEPS):
            return self.STEPS[session.step_index][1], None

        profile = self._archive_repository.create_profile(
            user_id=user_id,
            name=session.answers["name"],
            occupation=session.answers["occupation"],
            age=int(session.answers["age"]),
            background=session.answers["background"],
            disposition=session.answers["disposition"],
            favored_skills=[item.strip() for item in session.answers["favored_skills"].split(",") if item.strip()],
            generation=self._generate_stats(),
        )
        del self._sessions[user_id]
        return f"建卡完成：{profile.name} / {profile.coc.occupation}", profile

    def has_session(self, user_id: str) -> bool:
        return user_id in self._sessions

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
