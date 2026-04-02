# Feature Research

**Domain:** COC Character Archive & Builder Normalization (Track B - 人物构建与管理层)
**Researched:** 2026-03-28
**Confidence:** HIGH
**Milestone:** v2.3 B1 Archive And Builder Normalization

## Feature Landscape

### Table Stakes (Users Expect These)

Core COC character sheet sections that must be present in archive schema. These represent the standard investigator fields from Chaosium's official character sheet (7th edition).

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Core Attributes** | STR, CON, SIZ, DEX, APP, INT, POW, EDU — the seven characteristics that define every COC investigator | LOW | Already implemented in v1.8+ with COC attribute generation |
| **Derived Statistics** | HP, MP, SAN (max + current), Idea, Luck, Know, Move Rate, Build, Damage Bonus | LOW | Calculated from core attributes per COC 7th edition rules — deterministic formulas |
| **Occupation & Skills** | Each occupation provides skill point pools (Occupation Points + Personal Interest Points) | MEDIUM | Need structured occupation selection + skill allocation tracking |
| **Physical Description** | Age, sex, height, weight, hair, eyes — basic identity markers | LOW | Part of richer identity fields in v1.9 |
| **Backstory Fields** | Birthplace, Residence, Family, Education — anchor investigator in 1920s/Modern era | MEDIUM | Currently in "key past event" and "life goal" but not normalized to standard COC sections |
| **Status Tracking** | HP, MP, SAN current values, major wounds, temporary/long-term insanity | LOW | Campaign-specific projection, not archive-level (designed correctly in v1.8) |
| **Equipment & Finances** | Cash, assets, belongings, weapons | LOW | Simple inventory tracking, deferred to v2.3.x initially |

### Differentiators (Competitive Advantage)

Features that set the Discord AI Keeper apart from generic character builders. These leverage the AI-native architecture and local model constraints.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Conversational Builder Interview** | Natural language intake instead of form-filling — players describe their investigator conversationally | MEDIUM | Already built in v1.9 (Dynamic Builder Interview Engine). Key issue is output quality. |
| **AI Summarization Synthesis** | Transform raw user responses into cohesive character profiles that read like a Keeper wrote them | HIGH | **CRITICAL GAP - MAIN FOCUS OF v2.3**: Currently AI copies user input verbatim instead of synthesizing. Must fix to make archive useful. |
| **Archive-Campaign Separation** | Long-lived archive profile vs. campaign-specific projection — reuse investigators across modules | LOW | Already implemented in v1.8+ — correct architecture |
| **Adaptive Interview Flow** | Builder adjusts questions based on user responses — not a rigid form | MEDIUM | Built in v1.9 but needs refinement in question synthesis |
| **Rich Identity Fields** | Life goal, weakness, key past event — deeper than stock COC backstory | LOW | Added in v1.9, needs normalization into standard COC backstory sections |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem valuable but create problems in this specific context.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Live D&D Beyond Sync** | Players want automatic character import | Creates API dependencies, rate limits, auth complexity, moving target | Import adapters (one-time load) instead of live sync — already noted in STACK.md |
| **Full Rulebook Database In-Bot** | Comprehensive rules reference seems useful | Bloats the bot, better handled by external tools, training data staleness | Reference 5e-srd-api equivalent pattern for COC (SRD data) |
| **Real-Time Multiplayer Sheet Updates** | Everyone wants to see HP/SAN change live | Discord message volatility, edit spam, context window bloat | Campaign-specific panel summaries on demand instead of real-time edits |
| **Infinite Campaign Storage Per Character** | Players want to keep every module instance | Data bloat, privacy confusion, query performance degradation | Archive (permanent identity) vs. Projection (module-specific) separation handles this correctly |
| **Auto-Generate Full Backstory** | AI generating everything sounds powerful | Produces generic, uninteresting investigators that don't feel like player's own | AI *synthesizes* user input into narrative, doesn't replace user creativity |

## Feature Dependencies

```
[Core Attributes] ──required──> [Derived Statistics]

[Occupation Selection] ──required──> [Skill Point Allocation]

[Archive Profile] ──required──> [Campaign Projection]
        │
        └──requires──> [AI Summarization Synthesis]

[AI Summarization] ──enhances──> [Conversational Builder]
                         └───inputs──> [Richer Identity Fields]

[Normalize Archive Fields] ──enables──> [Profile Detail View]
                          └───enables──> [Character Panel Export]
```

### Dependency Notes

- **Core Attributes require Derived Statistics:** HP = (CON + SIZ)/10, SAN = POW×5, etc. This is deterministic COC math and already working.
- **Archive Profile requires AI Summarization:** The builder interview collects freeform responses; without synthesis, the archive just stores raw Q&A transcripts instead of usable character data. This is the v2.3 core problem.
- **AI Summarization enhances Conversational Builder:** Good summarization makes the builder feel like it "understood" the player, not just recorded their answers.
- **Normalize Archive Fields enables Profile Detail View:** Standardized sections make `/profile_detail` output consistent and complete.

## MVP Definition

### Launch With (v2.3)

The core fix for v2.3 — archive-builder normalization with working AI summarization:

- [x] Core attributes and derived stats — already working
- [x] Occupation with basic skill allocation — partially working
- [x] Archive-campaign separation — already working correctly
- [ ] **AI Summarization Synthesis** — **THE KEY GAP** to fix. Must synthesize user interview responses into cohesive profile text.
- [ ] Archive field normalization — align existing "life goal/weakness/key past event" with standard COC backstory sections
- [ ] Basic backstory fields — Birthplace, Residence, Family, Education mapping to standard COC sheet sections

### Add After Validation (v2.3.x)

Features to add once summarization is working:

- [ ] Full skill-by-skill allocation UI in profile detail view
- [ ] Equipment/inventory tracking per campaign projection
- [ ] Spell and magic item tracking for investigators
- [ ] Injury/scars/tome accumulation tracking

### Future Consideration (v3+)

Features to defer until core is solid:

- [ ] Rich UI panels (beyond Discord message format)
- [ ] Character sheet export (PDF-style output)
- [ ] Multi-era support (1920s, Modern, Dark Ages)
- [ ] Pulp Cthulhu rules variant

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| **AI Summarization Synthesis** | HIGH | HIGH | P1 |
| Archive Field Normalization | HIGH | MEDIUM | P1 |
| Backstory Section Mapping | HIGH | LOW | P1 |
| Occupation-Skill Tracking | MEDIUM | MEDIUM | P2 |
| Equipment Tracking | MEDIUM | LOW | P2 |
| Profile Detail View Polish | MEDIUM | LOW | P2 |
| Spell/Magic Item Tracking | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for v2.3 completion (archive-builder normalization)
- P2: Should have, add when summarization is validated
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Avrae (D&D) | Roll20/Foundry VTT | Quest Portal | Our Approach |
|---------|-------------|--------------------|--------------|--------------|
| Character Import | D&D Beyond API sync | Manual entry, JSON import | Built-in import | Import adapters only — no live sync |
| Conversational Builder | No — command-based | No — form-based | Partial — guided forms | **Our differentiator**: Full conversational interview |
| AI Summarization | None | None | None | **Our key gap**: Synthesize interview into profile |
| Long-lived Archive | Per-server, limited | Per-campaign | Per-account | Archive-campaign separation (already built) |
| Campaign Projection | No | Character sheets | Characters | Already implemented correctly |

**Key insight:** No competitor combines:
1. Conversational intake (not form-based)
2. AI synthesis (not just data storage)
3. Archive-projection separation (long-lived identity across campaigns)
4. Discord-native delivery

This is the differentiation space. The critical missing piece is AI summarization — without it, the conversational builder just records transcripts instead of producing usable character data.

## Sources

- Chaosium official COC 7th edition character sheet PDF (https://www.chaosium.com/content/FreePDFs/CoC/Character%20Sheets/)
- cthulhuclub.com character sheet generator (Chinese community reference)
- Avrae Discord bot — character management patterns (design reference, not integration) (https://avrae.readthedocs.io/)
- Project's existing v1.8-v1.9 builder implementation
- STACK.md — confirms 5e-srd-api pattern for COC rules data

---

*Feature research for: COC Archive & Builder Normalization*
*Milestone: v2.3 B1*
*Researched: 2026-03-28*
