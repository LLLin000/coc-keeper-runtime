---
phase: 09-coc-core-rules
plan: '01'
subsystem: rules
tags:
  - skill-system
  - coc7
  - data-model
requires:
  - COC-SKILL-01
  - COC-SKILL-02
provides:
  - SkillCategory enum
  - SkillEntry model
  - COC_SKILLS database
  - CharacterRecord.skills migration
affects:
  - dm_bot.rules.skills
  - dm_bot.characters.models
  - dm_bot.characters.skill_types
tech-stack:
  added:
    - pydantic.BaseModel
    - StrEnum
  patterns:
    - data-model
    - circular-import-resolution
key-files:
  created:
    - src/dm_bot/characters/skill_types.py
    - src/dm_bot/rules/skills.py
  modified:
    - src/dm_bot/characters/models.py
key-decisions:
  - Use list[SkillEntry] instead of dict[str, int] for skills
  - Place skill_types.py in dm_bot.characters to avoid circular imports
  - SkillCategory OTHER for unknown/legacy skills during migration
requirements-completed:
  - COC-SKILL-01
  - COC-SKILL-02
duration: 5 min
completed: 2026-03-30T13:45:00Z
---

# Phase 09 Plan 01: Skill Data Foundation Summary

## What Was Built

Created the COC 7th Edition skill data foundation with:
- `SkillCategory` enum with 9 categories (COMBAT, PERCEPTION, KNOWLEDGE, LANGUAGE, MOTION, COMMUNICATION, CRFT, FIGHTSPEC, OTHER)
- `SkillEntry` Pydantic model with fields: name, value, category, specialization, is_language, is_derived, default_value
- `COC_SKILLS` database with 126 COC7 skills
- `get_skill_by_name()` and `get_skills_by_category()` helper functions
- Migrated `CharacterRecord.skills` and `COCInvestigatorProfile.skills` from `dict[str, int]` to `list[SkillEntry]`
- Added `migrate_skills_from_dict()` method for backward compatibility with existing character data

## Technical Decisions

1. **Circular Import Resolution**: Placed `skill_types.py` in `dm_bot.characters` package to avoid triggering `dm_bot.rules` or `dm_bot.coc` package initialization during import
2. **Skill Data Structure**: Used `list[SkillEntry]` for flexibility (supports specializations, language flags, derived status) over simple dict
3. **Backward Compatibility**: Provided `migrate_skills_from_dict()` helper for migrating existing character data during transition

## Files Changed

| File | Change |
|------|--------|
| `src/dm_bot/characters/skill_types.py` | Created - SkillCategory enum and SkillEntry model |
| `src/dm_bot/rules/skills.py` | Created - COC_SKILLS database and helper functions |
| `src/dm_bot/characters/models.py` | Modified - Updated skills field types, added migration helper |

## Verification

```bash
uv run python -c "from dm_bot.rules.skills import SkillCategory, SkillEntry, COC_SKILLS; print(len(COC_SKILLS))"
# Output: 126

uv run python -c "from dm_bot.characters.models import CharacterRecord; from dm_bot.rules.skills import SkillEntry, SkillCategory; c=CharacterRecord(skills=[SkillEntry(name='test', value=50, category=SkillCategory.PERCEPTION)]); print(type(c.skills).__name__)"
# Output: list
```

## Deviations

- Skill categories expanded to 9 (added OTHER for unknown/legacy skills during migration)
- COC_SKILLS has 126 entries (plan specified 80+, exceeded with Chinese aliases and specializations)

## Next

Ready for plan 09-02: Skill resolution service with D20DiceRoller integration, hybrid trigger parsing, and skill point allocation.
