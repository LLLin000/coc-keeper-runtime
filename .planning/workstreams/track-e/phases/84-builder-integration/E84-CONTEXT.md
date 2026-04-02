# Phase E84 Context: Character Builder Integration

## Goal
Wire the character builder into RuntimeTestDriver and validate the full builder flow with E2E tests.

## Background

### Current State
- `builder.py` exists with `ConversationalCharacterBuilder`
- Has interview flow, question generation, profile synthesis
- NOT integrated with RuntimeTestDriver
- NOT wired into gameplay orchestrator

### Current Implementation
```python
class ConversationalCharacterBuilder:
    def start(self, *, user_id: str, visibility: str = "private") -> str
    async def answer(self, *, user_id: str, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]
    def has_session(self, user_id: str) -> bool
```

### Builder Flow
1. `start()` - Begin interview, returns first question
2. `answer()` - Provide answer, get next question or profile
3. Questions: name → concept → age → occupation → dynamic questions
4. Finalization: Review portrait → Confirm or add skills → Create profile

## Design Decisions

### 1. RuntimeTestDriver Integration

**Decision**: Add builder methods to RuntimeTestDriver

```python
def start_character_build(self, user_id: str) -> str:
    """Start character building interview."""
    
def answer_builder_question(self, user_id: str, answer: str) -> dict:
    """Answer a builder question."""
    
def get_builder_session(self, user_id: str) -> dict:
    """Get current builder session state."""
```

### 2. GameplayOrchestrator Integration

**Decision**: Add builder to GameplayOrchestrator

- Store builder instance
- Route builder commands
- Connect to archive repository

### 3. Testing Strategy

**Unit Tests**:
- Interview flow progression
- Answer normalization
- Profile synthesis

**E2E Scenario**:
- Full interview flow
- Profile creation
- Archive integration

## Implementation Requirements

### BUILDER-01: RuntimeTestDriver Integration
- start_character_build method
- answer_builder_question method
- get_builder_session method
- Builder state assertions

### BUILDER-02: Profile Creation
- Builder produces valid profiles
- Profiles saved to archive
- COC stats generated correctly

### BUILDER-03: COC Rules Validation
- Point totals validated
- Skill limits enforced
- Age modifiers applied

### BUILDER-04: E2E Scenario
- Full builder flow in scenario
- Interview → Profile → Archive
- Verification of created character

## Files to Modify

- `src/dm_bot/testing/runtime_driver.py` - Add builder methods
- `src/dm_bot/orchestrator/gameplay.py` - Wire builder
- `tests/coc/test_builder.py` - Unit tests
- `tests/scenarios/acceptance/scen_character_builder.yaml` - E2E

## Success Criteria

- [ ] Character builder accessible through RuntimeTestDriver
- [ ] Builder produces valid archive-compatible profiles
- [ ] Builder validates against COC rules
- [ ] E2E scenario validates full builder → archive → projection flow
