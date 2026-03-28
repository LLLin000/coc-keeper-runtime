# Requirements: Discord AI Keeper - Track B

**Defined:** 2026-03-28
**Core Value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, enforce investigation-heavy rules flow, and keep canonical module state without constant manual bookkeeping.

## vB.1.1 Requirements (Track B)

Milestone: Archive And Builder Normalization

### AI Summarization (核心修复)

- [ ] **AI-01**: User completes builder interview, AI synthesizes cohesive character profile from raw answers instead of copying verbatim
- [ ] **AI-02**: AI summarization respects COC 7e rules - no invented skills or occupations
- [ ] **AI-03**: Summarization distinguishes derived fields (calculated by rules) from intent fields (user's explicit choices)
- [ ] **AI-04**: Confirmation step before AI overwrites user's explicit character choices

### Archive Field Normalization

- [ ] **FN-01**: Existing "life_goal" field maps to standard COC backstory section
- [ ] **FN-02**: Existing "weakness" field maps to standard COC backstory section
- [ ] **FN-03**: Existing "key past event" field maps to standard COC backstory section
- [ ] **FN-04**: New fields follow COC 7e character sheet structure (Birthplace, Residence, Family, Education)
- [ ] **FN-05**: Schema versioning - new fields are nullable with defaults for backward compatibility

### Builder-Archive Contracts

- [ ] **BC-01**: Pydantic contracts define builder-to-archive communication schema
- [ ] **BC-02**: AnswerNormalizer component cleans raw user input to canonical slot format
- [ ] **BC-03**: CharacterSheetSynthesizer component transforms normalized answers into cohesive narrative
- [ ] **BC-04**: SectionNormalizer maps synthesis output to COC 7e character sheet sections
- [ ] **BC-05**: ArchiveProfileFactory creates profiles from synthesis output
- [ ] **BC-06**: Fallback from synthesis to heuristic extraction for robustness

### Archive-Projection Sync

- [ ] **PS-01**: Archive normalization updates automatically propagate to campaign projections
- [ ] **PS-02**: Diagnostic command shows sync status between archive and projection
- [ ] **PS-03**: Single active profile governance still works after normalization changes

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AI-01 | Phase 41 | Pending |
| AI-02 | Phase 42 | Pending |
| AI-03 | Phase 42 | Pending |
| AI-04 | Phase 42 | Pending |
| FN-01 | Phase 42 | Pending |
| FN-02 | Phase 42 | Pending |
| FN-03 | Phase 42 | Pending |
| FN-04 | Phase 42 | Pending |
| FN-05 | Phase 40 | Pending |
| BC-01 | Phase 40 | Pending |
| BC-02 | Phase 40 | Pending |
| BC-03 | Phase 41 | Pending |
| BC-04 | Phase 41 | Pending |
| BC-05 | Phase 41 | Pending |
| BC-06 | Phase 42 | Pending |
| PS-01 | Phase 42 | Pending |
| PS-02 | Phase 42 | Pending |
| PS-03 | Phase 42 | Pending |

**Coverage:**
- vB.1.1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 for vB.1.1*
