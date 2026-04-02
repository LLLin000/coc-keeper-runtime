# Phase 13: Integration & Testing - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Full system integration and verification for COC Core Rules Authority (vA.1.4). Verify all handlers work together, add missing tests, ensure smoke-check passes.
</domain>

<decisions>
## Implementation Decisions

### D-01: Test Coverage Gap
- **Decision:** Add tests for all 6 missing handlers with EXTENDED coverage
  - Each handler: success + failure + critical hit + fumble cases
  - Total: ~24 test cases
  - Using StubPercentileRoller for deterministic outcomes

### D-02: Test Parameter Strategy
- **Decision:** Use COMPLETE parameters for all handler tests
  - Include: dex, fighting, shooting, brawl, dodge, grapple, hp, hp_max, armor, damage_bonus, weapon_name, weapon_type
  - Target stats use `target_` prefix convention
  - Full parameter fidelity to catch edge cases

### D-03: Pre-existing Test Failure
- **Decision:** FIX existing failure in Phase 13
  - `test_rules_engine_executes_coc_sanity_check` expects `san_loss` but handler returns `sanity_loss`
  - Fix test assertion to match actual handler response

### D-04: Smoke Check Scope
- **Decision:** Run FULL smoke check (tests + runtime)
  - `uv run pytest -q` — verify all tests pass
  - `uv run python -m dm_bot.main smoke-check` — verify runtime imports and initialization

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/workstreams/track-a/PROJECT.md` — Track A principles
- `.planning/workstreams/track-a/ROADMAP.md` — Phase 13 scope
- `.planning/workstreams/track-a/phases/12-magic-system/12-01-SUMMARY.md` — Phase 12 summary

### Existing Code (read before implementing)
- `src/dm_bot/rules/engine.py` — RulesEngine with all 8 COC handlers
- `src/dm_bot/rules/coc/combat.py` — resolve_fighting_attack, resolve_shooting_attack, etc.
- `src/dm_bot/rules/coc/magic.py` — resolve_spell_cast, COC_SPELLS
- `tests/test_rules_engine.py` — existing tests with StubPercentileRoller pattern

### COC7 Rules Reference
- COC7 Keeper's Rulebook — combat, magic, skill chapters

</canonical_refs>

<specifics>
## Specific Ideas

### Tests to Add (Extended Coverage)
- test_coc_fighting_attack_success — fighter wins vs dodge
- test_coc_fighting_attack_failure — dodge wins
- test_coc_fighting_attack_critical — rolled 1
- test_coc_fighting_attack_fumble — rolled 100

- test_coc_shooting_attack_success — hit target
- test_coc_shooting_attack_failure — miss target
- test_coc_shooting_attack_critical — rolled 1
- test_coc_shooting_attack_fumble — rolled 96+ with high skill

- test_coc_brawl_attack_success
- test_coc_brawl_attack_failure
- test_coc_brawl_attack_critical
- test_coc_brawl_attack_fumble

- test_coc_dodge_success — successfully dodge attack
- test_coc_dodge_failure — dodge fails
- test_coc_dodge_critical
- test_coc_dodge_fumble

- test_coc_grapple_attack_success
- test_coc_grapple_attack_failure
- test_coc_grapple_attack_critical
- test_coc_grapple_attack_fumble

- test_coc_cast_spell_success — spell succeeds
- test_coc_cast_spell_failure — spell fails (insufficient MP or roll)
- test_coc_cast_spell_critical — rolled 1
- test_coc_cast_spell_fumble — rolled 100 or 96+ with high skill

### Pre-existing Fix
- Fix test assertion: `san_loss` → `sanity_loss` in test_rules_engine.py:188

### Verification
- Run `uv run pytest tests/test_rules_engine.py -v`
- Run `uv run python -m dm_bot.main smoke-check`

</specifics>

<deferred>
## Deferred Ideas

- None — Phase 13 is the final phase of vA.1.4

</deferred>

---

*Decisions confirmed by user: 2026-03-30*
*D-01: B (extended coverage), D-02: B (full params), D-03: A (fix existing), D-04: B (full smoke-check)*

---

*Phase: 13-integration-testing*
*Context gathered: 2026-03-30*
