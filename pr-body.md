## Summary
- Merge tanlearner123/pr/clean-export COC rules engine into master
- Adds COC 7e rules: skills, combat (Shooting/Brawl/Grapple/Dodge), SAN, magic, derived stats, experience
- Adds intent routing pipeline + onboarding system
- Adds adventure reaction engine and intent validators
- Adds +826 lines of COC rules engine tests

## Breaking Changes Fixed
- Reverted CharacterRecord.skills and COCInvestigatorProfile.skills from list[SkillEntry] back to dict[str, int] (preserves existing API)
- Fixed coc_sanity_check return: uses outcome.success, keeps san_loss as string expression, adds san_loss_value and sanity_loss for compat
- Fixed intent_handler feedback message length and emoji

## Code Quality Fixes Applied
- Moved all inline 'import d20' to top-level in engine.py, combat.py, sanity.py
- Fixed regex character class bug in intent_parser.py: [并且|然后|...] changed to (?:并且|然后|...)

## Tests
- 458 passing (vs 434 before merge)
- 30 pre-existing failures in test_v18_archive_builder.py (unrelated to this merge)

## Verification
uv run pytest -q  ->  458 passed, 3 warnings
