# Roadmap: Track B - 人物构建与管理层

## Completed Milestones

**vB.1.1** - B1 Archive And Builder Normalization
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Tighten archive-builder mapping with better AI summarization during builder flow, aligned with standard COC character sheet sections
- **Status:** Completed

---

## Active Milestone

**vB.1.4** - B4 Identity Projection And Character Ownership
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Strengthen Discord-user-to-character ownership so multiplayer campaign membership and role projection stay explicit, auditable, and immune to admin/owner identity bleed
- **Status:** Complete ✓

---

## vB.1.1 Phases

- [x] **Phase 40: Foundation** - Pydantic contracts, AnswerNormalizer, schema versioning
- [x] **Phase 41: Core Synthesis** - CharacterSheetSynthesizer, SectionNormalizer
- [x] **Phase 42: Integration** - Connect to builder, backward compatibility, archive-projection sync
- [x] **Phase 43: Polish** - Expand COC 7e sections, validation, playtest

### Phase 40: Foundation

**Goal:** Establish Pydantic contracts and schema versioning before building synthesis logic to prevent integration breakage later.

**Depends on:** Nothing (first phase of vB.1.1)

**Requirements:** BC-01, BC-02, FN-05

**Success Criteria** (what must be TRUE):
  1. Developer can import synthesis contracts and see clear Pydantic schemas for builder-to-archive communication
  2. AnswerNormalizer component can clean raw user input (Chinese variations) to canonical slot format
  3. New archive schema fields are nullable with defaults, preserving backward compatibility with existing profiles
  4. Existing profile queries continue to work without modification after schema changes

**Plans:** `40-01`

### Phase 41: Core Synthesis

**Goal:** Build the core AI summarization that transforms raw builder answers into cohesive COC character profiles instead of copying verbatim.

**Depends on:** Phase 40

**Requirements:** AI-01, BC-03, BC-04, BC-05

**Success Criteria** (what must be TRUE):
  1. User completing builder interview receives a synthesized character profile that reads as cohesive narrative, not copied input
  2. CharacterSheetSynthesizer uses structured output (instructor + Pydantic) to generate narrative from normalized answers
  3. SectionNormalizer maps synthesis output to standard COC 7e character sheet sections
  4. ArchiveProfileFactory creates valid ArchiveProfile instances from synthesis output
  5. Synthesis respects COC 7e rules - no invented skills or occupations appear in output

**Plans:** TBD

### Phase 42: Integration

**Goal:** Connect new synthesis components to existing builder flow with backward compatibility and archive-projection synchronization.

**Depends on:** Phase 41

**Requirements:** AI-02, AI-03, AI-04, FN-01, FN-02, FN-03, FN-04, BC-06, PS-01, PS-02, PS-03

**Success Criteria** (what must be TRUE):
  1. ConversationalCharacterBuilder uses new synthesis flow end-to-end without breaking existing users
  2. Fallback from synthesis to heuristic extraction works when synthesis produces invalid output
  3. Existing "life_goal", "weakness", "key_past_event" fields map to standard COC backstory sections
  4. New COC 7e fields (Birthplace, Residence, Family, Education) are added and populated
  5. Archive normalization updates automatically propagate to campaign projections
  6. Diagnostic command shows sync status between archive and projection
  7. Single active profile governance continues to work after normalization changes
  8. User sees confirmation step before AI overwrites their explicit character choices

**Plans:** TBD

### Phase 43: Polish

**Goal:** Validate with real playtest data and expand COC 7e section coverage before declaring milestone complete.

**Depends on:** Phase 42

**Requirements:** (validation-focused - all vB.1.1 requirements should be tested)

**Success Criteria** (what must be TRUE):
  1. At least one playtest session creates characters using the new synthesis flow
  2. Created characters display correctly in /profile_detail with all COC 7e sections
  3. Archive-to-projection sync works correctly for playtest characters
  4. No synthesis failures that crash the builder flow - fallback handles edge cases gracefully
  5. Validation rules confirm occupation skills match COC 7e allowed lists

**Plans:** TBD

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 40. Foundation | 1/1 | Completed | 2026-03-28 |
| 41. Core Synthesis | 1/1 | Completed | 2026-03-28 |
| 42. Integration | 1/1 | Completed | 2026-03-28 |
| 43. Polish | 1/1 | Completed | 2026-03-28 |

---

## vB.1.2 Phases

- [x] **Phase 44: Archive Card Schema Expansion** - Add richer long-lived investigator card fields and backward-compatible defaults
- [x] **Phase 45: Builder Writeback To Card Sections** - Map interview answers into clearer card sections instead of generic summaries
- [x] **Phase 46: Rich Card Presentation** - Improve `/profile_detail` and archive `/sheet` to feel like full investigator cards
- [x] **Phase 47: Archive And Projection Boundary Audit** - Reassert which fields remain long-lived vs campaign/module-local

### Phase 44: Archive Card Schema Expansion

**Goal:** Expand long-lived archive schema so it can represent more of a COC investigator card without confusing those fields with module state.

**Depends on:** vB.1.1 completion

**Focus:**
  1. Add richer card sections inspired by `charSheetGenerator`
  2. Keep new fields nullable and backward compatible
  3. Clearly separate long-lived fields from campaign overlays

### Phase 45: Builder Writeback To Card Sections

**Goal:** Make builder interviews populate richer card sections directly, not just compress into background and portrait summaries.

**Depends on:** Phase 44

**Focus:**
  1. Map interview answers into more explicit card fields
  2. Preserve explicit player intent when AI enriches card sections
  3. Keep writeback aligned with local COC rule boundaries

### Phase 46: Rich Card Presentation

**Goal:** Present long-lived archive cards in Discord as fuller investigator cards instead of thin archive summaries.

**Depends on:** Phase 45

**Focus:**
  1. Upgrade `/profile_detail`
  2. Upgrade archive-channel `/sheet`
  3. Make card sections more readable for players and collaborators

### Phase 47: Archive And Projection Boundary Audit

**Goal:** Reconfirm that richer archive cards still do not leak campaign or module state into long-lived identity truth.

**Depends on:** Phase 46

**Focus:**
  1. Audit archive vs projection boundaries
  2. Verify module-local mutations still remain projection-local
  3. Document which card sections are long-lived and which are campaign-only

## Progress Table (vB.1.2)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 44. Archive Card Schema Expansion | 1/1 | Completed | 2026-03-28 |
| 45. Builder Writeback To Card Sections | 1/1 | Completed | 2026-03-28 |
| 46. Rich Card Presentation | 1/1 | Completed | 2026-03-28 |
| 47. Archive And Projection Boundary Audit | 1/1 | Completed | 2026-03-28 |

---

## vB.1.3 Phases

- [x] **Phase 48: Interview Planner And Slot Coverage** - Make builder questioning smaller, more adaptive, and aligned with richer card sections
- [x] **Phase 49: Structured Character Portrait Synthesis** - Summarize interview results into a reusable person-level portrait before card generation
- [x] **Phase 50: COC-Bounded Rule Mapping And Dice Finalization** - Convert portrait into legal sheet recommendations and finalize via rules and dice
- [x] **Phase 51: Builder Flow Integration And UX Polish** - Integrate the two-stage flow into archive channels without breaking existing archive operations

### Phase 48: Interview Planner And Slot Coverage

**Goal:** Replace oversized or generic builder prompts with a controlled dynamic interview that asks smaller, more human questions and covers the richer archive/card sections systematically.

**Depends on:** vB.1.2 completion

**Focus:**
  1. Start from one-line concept and derive missing interview targets
  2. Ask adaptive follow-ups without repeating or over-questioning
  3. Stop when the person feels sufficiently shaped rather than when a fixed form is exhausted

### Phase 49: Structured Character Portrait Synthesis

**Goal:** Turn interview answers into a structured person-level portrait that is richer than raw notes and cleaner than freeform transcript text.

**Depends on:** Phase 48

**Focus:**
  1. Summarize who this person is before generating a card
  2. Capture long-lived identity, contradictions, desires, and weaknesses in reusable structure
  3. Keep the portrait distinct from numeric card truth

### Phase 50: COC-Bounded Rule Mapping And Dice Finalization

**Goal:** Introduce a formal finalization stage where COC rules and dice convert a shaped person into a legal investigator card.

**Depends on:** Phase 49

**Focus:**
  1. Map portrait to occupation/skill/finishing hints without inventing rules
  2. Define what interview answers may influence versus what must come from rules and dice
  3. Produce a card finalization contract that other tracks can consume safely

### Phase 51: Builder Flow Integration And UX Polish

**Goal:** Fit the new two-stage flow back into Discord archive operations so the experience feels coherent to players and maintainers.

**Depends on:** Phase 50

**Focus:**
  1. Preserve current archive compatibility
  2. Show clear transitions between interview and finalization
  3. Keep archive channels usable while preparing for later Track C and Track D improvements

## Progress Table (vB.1.3)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 48. Interview Planner And Slot Coverage | 1/1 | Completed | 2026-03-28 |
| 49. Structured Character Portrait Synthesis | 1/1 | Completed | 2026-03-28 |
| 50. COC-Bounded Rule Mapping And Dice Finalization | 1/1 | Completed | 2026-03-28 |
| 51. Builder Flow Integration And UX Polish | 1/1 | Completed | 2026-03-28 |

---
---

## vB.1.4 Phases

- [x] **Phase 52: Foundational Identity Models** - Explicit CampaignMember and CampaignCharacterInstance models (completed 2026-03-29)
- [x] **Phase 53: Join Flow and Membership Gates** - Enforce channel binding and prevent duplicate joins (completed 2026-03-29)
- [x] **Phase 54: Character Selection and Ready Validation** - Verify profile ownership and membership before ready
  (completed 2026-03-29)

### Phase 52: Foundational Identity Models

**Goal:** Replace primitive sets with structured data models for members and character instances.

**Depends on:** vB.1.3 completion

**Requirements:** REQ-001, REQ-004, REQ-006, REQ-010

**Success Criteria** (what must be TRUE):
  1. `CampaignMember` exists tracking Discord ID and role (owner, admin, member)
  2. `CampaignCharacterInstance` exists representing the active investigator projection
  3. `CampaignSession` stores these structured models instead of string sets
  4. System successfully serializes and deserializes the new objects to/from the JSON store

**What This Does NOT Include:**
  - Enforcing these models in Discord commands (focus is purely on internal data structures)

**Plans:** 1/1 plans complete

### Phase 53: Join Flow and Membership Gates

**Goal:** Secure the entry and exit points of a campaign using the new membership models.

**Depends on:** Phase 52

**Requirements:** REQ-005, REQ-007, REQ-009

**Success Criteria** (what must be TRUE):
  1. A user attempting to `/join` twice receives a clear error message
  2. Running the join command in an unbound channel fails gracefully
  3. A user cannot create a second active character instance in the same campaign

**What This Does NOT Include:**
  - Character selection logic and readiness state

### Phase 54: Character Selection and Ready Validation

**Goal:** Enforce ownership and membership rules before a player can ready up for gameplay.

**Depends on:** Phase 53

**Requirements:** REQ-002, REQ-003, REQ-008

**Success Criteria** (what must be TRUE):
  1. A non-member attempting to select a profile gets rejected with explicit error
  2. A user attempting to select someone else's archive profile gets rejected with explicit error
  3. Running `/ready` fails with explicit error if the user has not selected a profile or is not a member

**What This Does NOT Include:**
  - Modifying gameplay loops, combat resolution, or dice rolling mechanics

**Plans:**
- `54-01` — Validation Logic (TDD) — SelectProfileError/ReadyGateError enums, updated select_archive_profile(), validate_ready()
- `54-02` — Discord Command Wiring — /select_profile and /ready slash commands with validation

## Progress Table (vB.1.4)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 52. Foundational Identity Models | 1/1 | Complete   | 2026-03-29 |
| 53. Join Flow and Membership Gates | 1/1 | Complete    | 2026-03-29 |
| 54. Character Selection and Ready Validation | 2/2 | Complete   | 2026-03-29 |

---

## Queued Milestone

**vB.1.5** - Character Lifecycle And Governance Surface
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Build clearer player/admin governance around active, archived, replaced, and deleted characters once identity ownership is hardened
- **Status:** Queued after vB.1.4

**Planned focus:**
- profile lifecycle clarity
- admin governance surfaces
- ownership visibility and auditability
- archive/campaign instance management UX

**vB.1.6** - COC-Legal Character Finalization And New-Player Modes
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Finalize investigator sheets through explicit COC-legal flows while also supporting a bounded quick-start mode for new players
- **Status:** Queued after vB.1.5

**Planned focus:**
- standard canonical character finalization
- quick-start/new-player creation mode
- profession/skill/item recommendation consumption
- provenance and explanation of where card values came from

---

*Last updated: 2026-03-28 for milestones vB.1.1, vB.1.2, vB.1.3, and planned vB.1.4*
