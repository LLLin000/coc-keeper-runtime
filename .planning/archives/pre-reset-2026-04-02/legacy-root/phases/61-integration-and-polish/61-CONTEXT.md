# Phase 61: Integration And Polish - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning

<domain>
## Phase Boundary

End-to-end integration testing and presentation polish for the vB.1.5 Character Lifecycle milestone.

This phase delivers:
- PV-02: `/profile_detail` shows the selected profile's full archive card
- PV-04: User cannot ready without a valid active character instance
- Full lifecycle verification: create → archive → activate → select → ready

</domain>

<decisions>
## Implementation Decisions

### D-01: Ready Gate Validation (PV-04)
- **Decision:** 更新为使用实例模型
- `validate_ready()` should check `character_instances[user_id].status == "active"` instead of `selected_profile_id OR active_character_name`
- Consistent with Phase 58 architecture where instances have explicit status

### D-02: Profile Detail Status (PV-02)
- **Decision:** 显示实例上下文
- `detail_view()` should also show if the profile is currently active in a campaign and what its instance status is

### D-03: Test Scope
- **Decision:** E2E生命周期测试
- Full lifecycle test: create → archive → activate → select → ready
- Verifies all Phase 58/59/60 wiring works end-to-end

</decisions>

<prior_decisions>
## Prior Decisions (from Phases 52-60)

### Phase 58: Instance Management
- Instance status field added: `status = "active" | "retired"`
- `get_active_instances_for_user()` checks `status == "active" and character_name`

### Phase 56: Archive Lifecycle Operations
- `archive_profile()` sets status="archived"
- Detailed transition messages follow D-01 pattern

### Phase 55: Profile List
- Profile status icons: 🟢 active, ⚪ archived/inactive, 🔴 deleted
- `/profiles` shows all user profiles with status
</prior_decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Files
- `src/dm_bot/orchestrator/session_store.py` — `validate_ready()` (line 407), `CampaignCharacterInstance` model
- `src/dm_bot/coc/archive.py` — `detail_view()` (line 66), `InvestigatorArchiveProfile` model
- `src/dm_bot/discord_bot/commands.py` — `profile_detail` handler (line 497), `ready` handler (line 1611)

### Test Files
- `tests/test_ready_gate.py` — Existing ready gate tests
- `tests/test_instance_management.py` — Instance lifecycle tests
- `tests/test_archive_delete_recover.py` — Archive delete/recover tests

### Requirements
- `.planning/workstreams/track-b/REQUIREMENTS.md` — PV-02, PV-04 definitions
- `.planning/workstreams/track-b/ROADMAP.md` — Phase 61 description
</canonical_refs>

<codebase_context>
## Existing Code Insights

### Reusable Assets
- `CampaignCharacterInstance.status` — Phase 58 field, ready for validation use
- `detail_view()` — Already shows full archive card with all sections
- `session.character_instances[user_id]` — Instance lookup pattern exists

### Established Patterns
- Profile lifecycle: `active` → `archived` → `deleted`
- Instance lifecycle: `active` → `retired`
- Governance events: All operations append to `event_log`

### Integration Points
- `validate_ready()` in `session_store.py` gates the ready flow
- `ready` command in `commands.py` calls `validate_ready()` before allowing ready
- `profile_detail` shows `profile.detail_view()`

</codebase_context>

<specifics>
## Specific Ideas

No specific examples mentioned yet — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — Phase 61 is focused on integration and polish within existing scope.

</deferred>

---

*Phase: 61-integration-and-polish*
*Context gathered: 2026-04-01*
