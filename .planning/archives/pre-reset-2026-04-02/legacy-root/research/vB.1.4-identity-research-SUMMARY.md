# vB.1.4 Research Summary: Identity Projection And Character Ownership

**Date:** 2026-03-29
**Milestone:** vB.1.4
**Track:** Track B - 人物构建与管理层

## Current Identity Chain (Implicit)

There is no explicit `discord_user` or `campaign_character_instance` model. The identity chain is currently implicit and string-keyed:

```
discord_user.user_id (Discord interaction.user.id)
  → InvestigatorArchiveProfile.user_id (long-lived identity)
    → CampaignSession.member_ids (string set)
    → CampaignSession.selected_profiles[channel_id][user_id] = profile_id
      → CampaignSession.active_characters[user_id] = character_name
        → InvestigatorPanel (campaign-facing projection)
```

## Key Files

| File | Role | Key Data Structures |
|------|------|---------------------|
| `src/dm_bot/orchestrator/session_store.py` | Campaign session state | `CampaignSession`, `SessionPhase`, `SessionStore` |
| `src/dm_bot/coc/archive.py` | Long-lived archive profiles | `InvestigatorArchiveProfile`, `InvestigatorArchiveRepository` |
| `src/dm_bot/discord_bot/commands.py` | Command handlers | join/ready/select/archive/activate |
| `src/dm_bot/orchestrator/gameplay.py` | Projection creation | `sync_panel_from_archive_profile()`, `CharacterRegistry` |
| `src/dm_bot/coc/panels.py` | Campaign-facing character state | `InvestigatorPanel` |
| `src/dm_bot/orchestrator/visibility.py` | Ready/admin visibility | `CampaignVisibility`, `PlayerSnapshot` |
| `src/dm_bot/persistence/store.py` | JSON persistence | Campaign sessions + archive profiles |

## Current Flow Analysis

### Join Flow
- `SessionStore.join_campaign()` adds user_id to `member_ids`
- No validation beyond "session exists for this channel"
- No duplicate check, no leave validation
- Any user can join any bound channel

### Ready Flow
- `BotCommands.ready_for_adventure()` binds character via `active_characters[user_id]`
- Does NOT explicitly verify `user_id in member_ids`
- Creates/updates `InvestigatorPanel` via `sync_panel_from_archive_profile()`
- If all members ready → transitions to `AWAITING_ADMIN_START`

### Archive/Profile Linkage
- Long-lived profiles in `InvestigatorArchiveRepository`
- `select_profile()` stores `selected_profiles[channel_id][user_id] = profile_id`
- `sync_panel_from_archive_profile()` copies archive data into `InvestigatorPanel`
- `archive_profile()` / `activate_profile()` are user-global, not campaign-scoped

### Admin Separation
- `_is_admin()` checks guild admin OR `session.owner_id == interaction.user.id`
- `IntentClassifier` receives `is_admin` hint
- No hard enforcement in most command handlers

## Identity Validation Gaps

| Gap | Severity | Current State |
|-----|----------|---------------|
| No `CampaignMember` object | HIGH | Membership is a string set (`member_ids`) |
| `/ready` doesn't verify membership | HIGH | Can mark ready without being in campaign |
| `/select_profile` doesn't verify membership | HIGH | Can select profile without being in campaign |
| No `campaign_character_instance` entity | HIGH | Projection is in-memory `InvestigatorPanel` + session maps |
| No uniqueness/ownership enforcement | MEDIUM | Only `archive_repository.get_profile(user_id, profile_id)` |
| `join_campaign`/`leave_campaign` can KeyError | MEDIUM | No guard for unbound channels |
| Archive status is user-global | LOW | `archive_profile()` affects all campaigns |
| Owner/admin identity bleed | HIGH | No separation between owner admin and player identity |

## Best Mapping for vB.1.4

| Concept | Current Implementation | vB.1.4 Target |
|---------|----------------------|---------------|
| `discord_user` | `interaction.user.id` references | Explicit user identity contract |
| `archive_profile` | `InvestigatorArchiveProfile` | Strengthened with ownership semantics |
| `campaign_member` | `member_ids` string set | Dedicated member model with ready/selection state |
| `campaign_character_instance` | `InvestigatorPanel` + `active_characters` | Explicit projection with ownership chain |

## External Patterns (Librarian Research)

**Schema Scope Question:**
- **Minimal schema**: Fit current Track B patterns, add only what vB.1.4 needs
- **Future-proof identity model**: Design for lifecycle management (vB.1.5), even if it adds migration cost

**Recommendation**: Future-proof design. vB.1.5 will need lifecycle operations (archive/replace/delete/recover), and vB.1.6 will need provenance tracking (canonical vs quick-start). A minimal schema now will require rework in 2 milestones.

## Recommended Seams for vB.1.4

1. **`session_store.py`**: Add `CampaignMember` model, make membership explicit
2. **`archive.py`**: Strengthen ownership semantics, add campaign-binding validation
3. **`commands.py`**: Add membership verification before ready/select
4. **`gameplay.py`**: Make projection creation explicit with ownership chain
5. **New: `campaign_member.py`**: Dedicated campaign member model with ready/selection state
6. **New: `campaign_character_instance.py`**: Explicit projection with ownership chain

## Next Steps

1. Define REQUIREMENTS.md with REQ-IDs for each gap
2. Create roadmap via gsd-roadmapper
3. Design `CampaignMember` and `CampaignCharacterInstance` models
4. Implement ready-gate validation
5. Add admin separation enforcement

## Sources

- Explore agent bg_7d784929: Identity chain code analysis
- Explore agent bg_0dc6303d: Campaign/join flow analysis
- Librarian agent bg_886e27a1: External identity patterns research (incomplete)

---

*Generated by GSD new-milestone workflow for vB.1.4*
