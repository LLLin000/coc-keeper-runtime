# Requirements Archive: vC.1.1

**Milestone:** C1 Channel Governance And Command Discipline Hardening
**Shipped:** 2026-03-28
**Track:** Track C - Discord 交互层

---

## Requirements Status

### Channel Discipline

- [x] **CHAN-01**: Archive channel commands should only work in designated archive channels — ✅ IMPLEMENTED
- [x] **CHAN-02**: Admin channel commands should only work in designated admin channels — ✅ IMPLEMENTED
- [x] **CHAN-03**: Game hall commands should be blocked or redirected in non-game channels — ✅ IMPLEMENTED
- [x] **CHAN-04**: Wrong-channel commands show clear redirect message to correct channel — ✅ IMPLEMENTED

### Command Guidance

- [x] **GUIDE-01**: Command help text includes recommended channel for usage — ✅ IMPLEMENTED
- [x] **GUIDE-02**: Channel-specific commands show contextual guidance — ✅ IMPLEMENTED
- [x] **GUIDE-03**: New users get welcome message with channel structure explanation — ✅ IMPLEMENTED

### Command Clutter Reduction

- [x] **CLUTTER-01**: Long command outputs use ephemeral or follow-up modes — ✅ IMPLEMENTED
- [x] **CLUTTER-02**: Diagnostic commands prefer trace/admin channels — ✅ IMPLEMENTED
- [x] **CLUTTER-03**: Gameplay narration stays in game halls, not cross-posted — ✅ IMPLEMENTED

### Command Stability (Deferred)

- [ ] **STABLE-01**: Commands with in-progress state detect duplicate invocations — DEFERRED
- [ ] **STABLE-02**: Command state is persisted — DEFERRED
- [ ] **STABLE-03**: Users can cancel/abort in-progress commands — DEFERRED

### UX Improvements (Deferred)

- [ ] **UX-01**: Commands show confirmation prompts before destructive actions — DEFERRED
- [ ] **UX-02**: Error messages are friendly — DEFERRED
- [ ] **UX-03**: Loading/processing states are visible — DEFERRED
- [ ] **UX-04**: Success messages confirm what happened — DEFERRED

---

## Traceability Table

| Requirement | Phase | Final Status |
|-------------|-------|--------------|
| CHAN-01 | 44 | ✅ Implemented |
| CHAN-02 | 44 | ✅ Implemented |
| CHAN-03 | 44 | ✅ Implemented |
| CHAN-04 | 45 | ✅ Implemented |
| GUIDE-01 | 45 | ✅ Implemented |
| GUIDE-02 | 45 | ✅ Implemented |
| GUIDE-03 | 46 | ✅ Implemented |
| CLUTTER-01 | 46 | ✅ Implemented |
| CLUTTER-02 | 46 | ✅ Implemented |
| CLUTTER-03 | 46 | ✅ Implemented |
| STABLE-01 | - | Deferred |
| STABLE-02 | - | Deferred |
| STABLE-03 | - | Deferred |
| UX-01 | - | Deferred |
| UX-02 | - | Deferred |
| UX-03 | - | Deferred |
| UX-04 | - | Deferred |

---

## Summary

- **Shipped:** 10 requirements
- **Deferred:** 8 requirements (STABLE and UX categories)
- **Coverage:** 55.6%

---

_Archived from .planning/workstreams/track-c/REQUIREMENTS.md_
