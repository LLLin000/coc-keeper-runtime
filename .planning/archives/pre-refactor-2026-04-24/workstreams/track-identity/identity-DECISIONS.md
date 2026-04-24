# Identity Gray Area Decisions

Decided: 2026-04-03

---

## D-01: Heuristic vs Model-Guided Builder

**Decision: C — Model primary + Heuristic fallback**

Builder components (`InterviewPlanner`, `ArchiveSemanticExtractor`, `CharacterSheetSynthesizer`) use model-guided implementation as primary path. Heuristic implementations exist as explicit fallback when model fails or is unavailable.

**Failure trigger definition**: Model-guided path fails when:
- Model returns malformed/unparseable output after N retries
- Model confidence score is below threshold
- Router model is unavailable

**Rule**: Model output must be auditable — logged in full for debugging, not silently swallowed.

---

## D-02: Campaign-Local vs Archive State Boundary

**Decision: A — Panel is pure session mirror, with explicit checkpoint writes**

**Immutable during session (never writeback to archive):**
- SAN, HP, MP, Luck (current and max)
- Derived stats: damage bonus, build, move rate
- Characteristics: STR, CON, DEX, APP, POW, INT, SIZ, EDU

**Writable to archive via explicit post-session checkpoint (player-confirmed):**
- Adventure experiences / narrative journal entries
- Skill improvements (after post-session improvement rolls)
- Character arc notes / development
- Significant possessions or status changes (narrative-level, not stat-level)

**Checkpoint flow:**
1. Session ends or reaches natural breakpoint
2. System presents checkpoint summary: "以下变化将写入角色档案：[...]
3. Player reviews, edits, confirms
4. Archive updated with confirmed changes only

---

## D-03: Character Import Priority

**Decision: C — Manual paste import with AI-assisted parsing**

**Scope for v1.0:**
- User pastes character sheet text (from any text source)
- AI parses into `CharacterRecord` / `COCInvestigatorProfile`
- User reviews and corrects parsed result before saving to archive

**Not in scope for v1.0:**
- Live Dicecloud API (requires OAuth/token, external dependency)
- PDF character sheet extraction (format diversity too high)
- Direct D&D Beyond import

**Import format spec**: Defined in `v1.0-SPEC.md`.

---

## D-04: Archive Schema Migration

**Decision: B — Lightweight incremental migration**

**Activation trigger**: First non-test user profile created in production.

**Migration design:**
- Each schema version has a forward-only migration: `migrate_v{N}_to_v{N+1}()`
- Migration applied automatically on archive load if `schema_version < current`
- Old migrations are never deleted; registry tracks applied migrations per profile
- Before first real user data: schema is open for changes with documentation

**Migration execution**: On `load_from_persistence()`, detect version mismatch, apply pending migrations in order, write back with new version.

---

## D-05: Builder Flow Length

**Decision: C — Two-tier builder**

**Fast Path** (target: ~5 minutes to complete):
1. Choose occupation from template list
2. Answer 3 questions: core_belief, weakness, key_past_event
3. Auto-generate rest from occupation template + answers
4. Review generated sheet, adjust skill allocation (occupation points pre-filled)
5. Finalize with COC validation warning

**Full Path** (target: 15-20 minutes, roleplay immersion):
1. Conversational interview (existing flow)
2. Dynamic question generation based on occupation and answers
3. Full backstory extraction across all biographic fields
4. Skill allocation with full point pools
5. Portrait summary and finalize

**User choice**: Presented at builder entry — "快速建卡" vs "深度塑造"

---

## D-06: Skill Naming Convention

**Decision: A — English keys in archive, name_cn for display**

Archive `skills` dict keys are always English (`spot_hidden`, `psychology`, `accounting`), matching `COC_SKILLS` definitions in `rules/coc/skills.py`.

Display layer (`InvestigatorPanel`, `DiscordCardRenderer`) uses `SkillDefinition.name_cn` via `get_skill_display_name()` for Chinese presentation.

**Rationale**: Archive is the canonical truth for rules resolution; display localization is a presentation concern only.

---

## D-07: Soft Delete vs Hard Delete

**Decision: B — Soft delete 7-day grace + user-controlled permanent delete**

**7-day grace period** (existing behavior):
- `status="deleted"`, `deleted_at` timestamp set
- `purge_expired_deleted()` runs on load
- Player can recover within 7 days via `/recover-character`

**After 7 days (expired but not purged):**
- Profile marked `status="expired"` 
- Retained for potential recovery but not shown in active list
- Purged only by explicit user action or admin operation

**Permanent delete command**: `/delete-character --permanent <profile_id>`
- Requires confirmation step
- Irreversible; results in hard delete from persistence
- Logs permanent deletion event for audit

---

## D-08: COC-Legal Validation at Finalize

**Decision: B — Soft warning with enforced rules on characteristics/derived stats**

**Characteristics and derived stats (enforced — cannot be overridden by player):**
- STR, CON, DEX, APP, POW, INT, SIZ, EDU (generated by 3d6*5 / formula, not user-set)
- HP, MP, SAN (derived from characteristics, not user-set beyond initial generation)
- Luck (3d6*5, not user-set)
- Damage bonus, build, move rate (derived, not user-set)

**Skill points and allocations (soft warning — can be overridden):**
- Occupation skill points and interest skill points have COC-defined pools
- Warning issued if total exceeds规则允许范围, but player can confirm and proceed
- This supports "有趣的角色构建" that intentionally踩线

**Other validation (soft warning):**
- SAN range (0-99) — warn if out of range, allow override with confirmation
- Skill values > 100 — warn, allow override
- Age-inappropriate derived stats — warn, allow override

**Finalize flow:**
1. Present validation report
2. Flag hard violations (characteristics/derived stats) — these cannot be changed at finalize, must regenerate
3. Flag soft violations with warning and "确认override" option
4. Player confirms or overrides
