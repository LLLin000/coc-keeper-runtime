# Roadmap: Track B - 人物构建与管理层

## Active Milestone

**vB.1.1** - B1 Archive And Builder Normalization
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Tighten archive-builder mapping with better AI summarization during builder flow, aligned with standard COC character sheet sections

---

## vB.1.1 Phases

- [ ] **Phase 40: Foundation** - Pydantic contracts, AnswerNormalizer, schema versioning
- [ ] **Phase 41: Core Synthesis** - CharacterSheetSynthesizer, SectionNormalizer
- [ ] **Phase 42: Integration** - Connect to builder, backward compatibility, archive-projection sync
- [ ] **Phase 43: Polish** - Expand COC 7e sections, validation, playtest

### Phase 40: Foundation

**Goal:** Establish Pydantic contracts and schema versioning before building synthesis logic to prevent integration breakage later.

**Depends on:** Nothing (first phase of vB.1.1)

**Requirements:** BC-01, BC-02, FN-05

**Success Criteria** (what must be TRUE):
  1. Developer can import synthesis contracts and see clear Pydantic schemas for builder-to-archive communication
  2. AnswerNormalizer component can clean raw user input (Chinese variations) to canonical slot format
  3. New archive schema fields are nullable with defaults, preserving backward compatibility with existing profiles
  4. Existing profile queries continue to work without modification after schema changes

**Plans:** TBD

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
| 40. Foundation | 0/1 | Not started | - |
| 41. Core Synthesis | 0/1 | Not started | - |
| 42. Integration | 0/1 | Not started | - |
| 43. Polish | 0/1 | Not started | - |

---
*Last updated: 2026-03-28 for milestone vB.1.1*
