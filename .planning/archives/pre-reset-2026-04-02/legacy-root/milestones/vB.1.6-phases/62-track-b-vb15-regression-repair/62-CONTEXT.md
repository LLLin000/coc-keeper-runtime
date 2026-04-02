# Phase 62: vB.1.5 Regression Repair And Contract Reconciliation - Context

**Gathered:** 2026-04-02
**Status:** Ready for execution

<domain>
## Phase Boundary

Repair the merged Track B regressions that broke the previously shipped vB.1.5 lifecycle and governance contracts.

This phase restores:
- Archive delete/recover/purge semantics and deleted presentation
- Campaign instance lifecycle and governance event logging
- Ready gate, profile detail, admin command, and scenario integration against the instance model
- A green repository gate (`pytest` and `smoke-check`)

</domain>

<root_causes>
## Root Cause Summary

### RC-01: Archive lifecycle contract drift
- `InvestigatorArchiveProfile` no longer exposes the `deleted_at` state expected by tests and command surfaces
- `delete_profile`, `recover_profile`, and `purge_expired_deleted` contracts are missing or incomplete
- `replace_active_with` regressed from archived replacement semantics to `replaced`

### RC-02: Session instance/governance contract drift
- `CampaignCharacterInstance` lost the explicit `status` field expected by lifecycle tests
- `SessionStore` is missing instance lifecycle APIs and GovernanceEventLog wiring
- `validate_ready()` still uses pre-instance membership fields instead of current instance truth

### RC-03: Command and scenario integration drift
- `commands.py` now assumes archive/session methods that are not implemented
- `/profile_detail` presentation no longer matches the sectioned contract asserted by tests
- Scenario and contract tests depend on phase transitions that are blocked by the broken ready/onboarding lifecycle

</root_causes>

<canonical_refs>
## Canonical References

- `src/dm_bot/coc/archive.py`
- `src/dm_bot/orchestrator/session_store.py`
- `src/dm_bot/orchestrator/governance_event_log.py`
- `src/dm_bot/discord_bot/commands.py`
- `tests/test_archive_delete_recover.py`
- `tests/test_instance_management.py`
- `tests/test_ready_gate.py`
- `tests/test_e2e_lifecycle.py`
- `tests/test_v18_archive_builder.py`
- `tests/test_ai_contract.py`
- `tests/test_scenarios.py`

</canonical_refs>

<strategy>
## Repair Strategy

1. Restore archive repository/model behavior against the Track B delete/recover tests.
2. Restore explicit instance lifecycle and governance event wiring in `SessionStore`.
3. Reconcile command handlers and presentation surfaces to the restored contracts.
4. Re-run targeted scenario/contract suites, then the full repository gate.

</strategy>
