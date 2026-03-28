# Requirements: Discord AI Keeper - Track B

**Defined:** 2026-03-28
**Core Value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, enforce investigation-heavy rules flow, and keep canonical module state without constant manual bookkeeping.

## vB.1.1 Requirements (Track B)

Milestone: Archive And Builder Normalization

### AI Summarization (核心修复)

- [x] **AI-01**: User completes builder interview, AI synthesizes cohesive character profile from raw answers instead of copying verbatim
- [x] **AI-02**: AI summarization respects COC 7e rules - no invented skills or occupations
- [x] **AI-03**: Summarization distinguishes derived fields (calculated by rules) from intent fields (user's explicit choices)
- [x] **AI-04**: Confirmation step before AI overwrites user's explicit character choices

### Archive Field Normalization

- [x] **FN-01**: Existing "life_goal" field maps to standard COC backstory section
- [x] **FN-02**: Existing "weakness" field maps to standard COC backstory section
- [x] **FN-03**: Existing "key past event" field maps to standard COC backstory section
- [x] **FN-04**: New fields follow COC 7e character sheet structure (Birthplace, Residence, Family, Education)
- [x] **FN-05**: Schema versioning - new fields are nullable with defaults for backward compatibility

### Builder-Archive Contracts

- [x] **BC-01**: Pydantic contracts define builder-to-archive communication schema
- [x] **BC-02**: AnswerNormalizer component cleans raw user input to canonical slot format
- [x] **BC-03**: CharacterSheetSynthesizer component transforms normalized answers into cohesive narrative
- [x] **BC-04**: SectionNormalizer maps synthesis output to COC 7e character sheet sections
- [x] **BC-05**: ArchiveProfileFactory creates profiles from synthesis output
- [x] **BC-06**: Fallback from synthesis to heuristic extraction for robustness

### Archive-Projection Sync

- [x] **PS-01**: Archive normalization updates automatically propagate to campaign projections
- [x] **PS-02**: Diagnostic command shows sync status between archive and projection
- [x] **PS-03**: Single active profile governance still works after normalization changes

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AI-01 | Phase 41 | Completed |
| AI-02 | Phase 42 | Completed |
| AI-03 | Phase 42 | Completed |
| AI-04 | Phase 42 | Completed |
| FN-01 | Phase 42 | Completed |
| FN-02 | Phase 42 | Completed |
| FN-03 | Phase 42 | Completed |
| FN-04 | Phase 42 | Completed |
| FN-05 | Phase 40 | Completed |
| BC-01 | Phase 40 | Completed |
| BC-02 | Phase 40 | Completed |
| BC-03 | Phase 41 | Completed |
| BC-04 | Phase 41 | Completed |
| BC-05 | Phase 41 | Completed |
| BC-06 | Phase 42 | Completed |
| PS-01 | Phase 42 | Completed |
| PS-02 | Phase 42 | Completed |
| PS-03 | Phase 42 | Completed |

**Coverage:**
- vB.1.1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 for vB.1.1*

---

## vB.1.2 Requirements (Track B)

Milestone: Investigator Archive Card Completion

### Archive Card Completeness

- [ ] **AC-01**: Long-lived archive schema covers a broader set of COC-style investigator card sections inspired by `charSheetGenerator`
- [ ] **AC-02**: New card sections remain backward compatible with old archive payloads
- [ ] **AC-03**: New card sections are explicitly classified as long-lived archive truth, not campaign-local state

### Builder Writeback Quality

- [ ] **BW-01**: Builder interview answers write back into richer card sections instead of only background summaries
- [ ] **BW-02**: AI enrichment can extend card sections without silently overriding explicit player-provided answers
- [ ] **BW-03**: Builder writeback still respects local COC rules and does not invent illegal rule-facing values

### Presentation

- [ ] **PR-01**: `/profile_detail` presents richer card sections with clear grouping and readability
- [ ] **PR-02**: Archive-channel `/sheet` shows the long-lived card in a fuller investigator-card layout
- [ ] **PR-03**: Card presentation surfaces enough detail that collaborators can understand a character without reading raw builder transcripts

### Archive / Projection Boundary

- [ ] **AP-01**: Richer archive cards do not cause module-local state to leak back into long-lived archives
- [ ] **AP-02**: Projection sync still works after archive schema expansion
- [ ] **AP-03**: Diagnostics or documentation clearly explain archive vs projection boundaries for new card fields

## vB.1.2 Traceability

| Requirement | Planned Phase |
|-------------|---------------|
| AC-01 | Phase 44 |
| AC-02 | Phase 44 |
| AC-03 | Phase 47 |
| BW-01 | Phase 45 |
| BW-02 | Phase 45 |
| BW-03 | Phase 45 |
| PR-01 | Phase 46 |
| PR-02 | Phase 46 |
| PR-03 | Phase 46 |
| AP-01 | Phase 47 |
| AP-02 | Phase 47 |
| AP-03 | Phase 47 |
