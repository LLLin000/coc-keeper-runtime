# Roadmap: Track B - 人物构建与管理层

## Completed Milestones

**vB.1.1** - B1 Archive And Builder Normalization
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Tighten archive-builder mapping with better AI summarization during builder flow, aligned with standard COC character sheet sections
- **Status:** Completed

---

## Active Milestone

**vB.1.2** - B2 Investigator Archive Card Completion
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Expand archive and profile presentation toward a fuller COC investigator card, aligned with `charSheetGenerator`-style sections while preserving local COC rule truth
- **Status:** Completed

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
*Last updated: 2026-03-28 for milestones vB.1.1 and vB.1.2*
