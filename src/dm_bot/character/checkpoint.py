"""Post-session character checkpoint processing."""

from pydantic import BaseModel, Field

from dm_bot.character.sheet import CharacterSheet
from dm_bot.rules.coc.experience import roll_all_skill_improvements


class CheckpointResult(BaseModel):
    """Result of a session checkpoint."""

    skills_tried: int = 0
    skills_improved: int = 0
    improved_skills: list[str] = Field(default_factory=list)
    updated_sheet: CharacterSheet | None = None


class SessionCheckpoint:
    """Processes post-session character evolution."""

    def process(
        self,
        sheet: CharacterSheet,
        skills_used: list[str],
        improvement_rolls: dict[str, int] | None = None,
    ) -> CheckpointResult:
        if not skills_used:
            return CheckpointResult(updated_sheet=sheet)

        results = roll_all_skill_improvements(skills_used, sheet.skills, improvement_rolls)
        improved = [r for r in results if r.improved]

        new_skills = dict(sheet.skills)
        for r in improved:
            new_skills[r.skill_key] = r.new_value

        new_sheet = sheet.model_copy(update={"skills": new_skills})
        return CheckpointResult(
            skills_tried=len(results),
            skills_improved=len(improved),
            improved_skills=[r.skill_key for r in improved],
            updated_sheet=new_sheet,
        )
