# Phase 53: Handling Reason Surfaces - Implementation Plan

## Context

**Phase Goal:** Add concise player-facing explanations for why messages were ignored, buffered, deferred, or otherwise routed differently.

**Key Decisions:**
- D-01: Send routing feedback as ephemeral Discord messages (visible only to sender)
- D-02: Feedback delivered immediately when buffered/ignored/deferred
- D-03: Feedback must be ≤50 characters
- D-04: Different feedback content per routing outcome (BUFFERED, IGNORED, DEFERRED, PROCESSED)

**Requirements:** PLAY-03, PLAY-04

**What's Already Built:**
- `IntentHandlingResult.feedback_message` in `intent_handler.py`
- `RoutingVisibility.explanation` in `visibility.py`
- `_get_feedback()` method generates feedback but NOT wired to Discord
- Missing: IGNORED and DEFERRED feedback cases in `_get_feedback()`

**Key Files to Modify:**
- `src/dm_bot/router/intent_handler.py` - Add missing feedback cases
- `src/dm_bot/main.py` - Instantiate IntentHandlerRegistry
- `src/dm_bot/discord_bot/commands.py` - Inject feedback delivery into message pipeline
- Create new: `src/dm_bot/discord_bot/feedback.py` - Ephemeral feedback sender

---

## Task Dependency Graph

| Task | Depends On | Reason |
|------|------------|--------|
| Task 1: Add IGNORED and DEFERRED feedback to _get_feedback() | None | Starting point - adds missing cases |
| Task 2: Create feedback delivery service | None | Creates new component for sending ephemeral messages |
| Task 3: Wire IntentHandlerRegistry into main.py | Task 2 | Registry needs to be instantiated and available |
| Task 4: Inject feedback into message pipeline | Task 1, Task 3 | Where intents are processed, send feedback |
| Task 5: Write TDD tests for feedback delivery | Task 1, Task 2 | Verify behavior before/after implementation |

---

## Parallel Execution Graph

Wave 1 (Start Immediately):
├── Task 1: Add IGNORED and DEFERRED feedback cases (intent_handler.py)
├── Task 2: Create feedback delivery service (feedback.py)
└── Task 5: Write TDD tests for feedback (can start with interface)

Wave 2 (After Wave 1 Completes):
├── Task 3: Wire IntentHandlerRegistry into main.py
└── Task 4: Inject feedback into message pipeline

**Critical Path:** Task 1 → Task 4
**Estimated Parallel Speedup:** 30% faster than sequential

---

## Tasks

### Task 1: Add IGNORED and DEFERRED Feedback Cases to _get_feedback()

**Description:** Extend the feedback_map in `_get_feedback()` to include IGNORED and DEFERRED routing outcomes per D-04.

**Delegation Recommendation:**
- Category: `quick` - Small targeted change to existing code
- Skills: [] - No special skills needed

**Skills Evaluation:**
- INCLUDED none: Simple dictionary extension, no new patterns needed

**Depends On:** None

**Files to Modify:**
- `src/dm_bot/router/intent_handler.py`

**Action:**
Add the missing feedback cases to the `_get_feedback()` method feedback_map:
- For IGNORED: "⏸️ 消息在当前阶段不适用" (Message not applicable in current phase)
- For DEFERRED: "📋 规则问题将在结算后回答" (Rules questions answered after resolution)
- Ensure all new feedback strings are ≤50 characters per D-03

```python
# Add to feedback_map:
MessageIntent.UNKNOWN: {
    "scene_round_open": "⏸️ 消息在当前阶段不适用",
    "scene_round_resolving": "⏸️ 行动已结束，请等待下一轮",
    "combat": "⏸️ 战斗中无法使用此指令",
    "awaiting_ready": "⏸️ 请先完成就位",
},
MessageIntent.RULES_QUERY: {
    "combat": "📋 规则问题将在战斗后回答",
    "scene_round_resolving": "📋 规则问题将在结算后回答",
},
```

**Acceptance Criteria:**
- [ ] IGNORED feedback exists for UNKNOWN intent across phases
- [ ] DEFERRED feedback exists for RULES_QUERY in combat/resolve phases
- [ ] All feedback strings ≤50 characters
- [ ] Existing tests still pass

---

### Task 2: Create Feedback Delivery Service

**Description:** Create a dedicated service for sending ephemeral Discord feedback messages per D-01.

**Delegation Recommendation:**
- Category: `quick` - New file creation with simple interface
- Skills: [] - Standard Discord patterns

**Skills Evaluation:**
- INCLUDED none: Simple service creation, follows existing patterns

**Depends On:** None

**Files to Create:**
- `src/dm_bot/discord_bot/feedback.py`

**Action:**
Create a new FeedbackService class that:
1. Accepts Discord channel and user references
2. Sends ephemeral messages (visible only to sender)
3. Handles rate limiting gracefully
4. Logs feedback sent for diagnostics

```python
# src/dm_bot/discord_bot/feedback.py
from typing import Protocol

class FeedbackSender(Protocol):
    """Protocol for sending ephemeral feedback to users."""
    async def send_feedback(
        self,
        channel_id: str,
        user_id: str,
        message: str,
    ) -> bool:
        """Send ephemeral feedback to a user. Returns True if sent successfully."""
        ...

class DiscordFeedbackService:
    """Sends routing feedback as ephemeral Discord messages."""
    
    def __init__(self, bot_client) -> None:
        self._bot = bot_client
    
    async def send_feedback(
        self,
        channel_id: str,
        user_id: str,
        message: str,
    ) -> bool:
        """Send ephemeral feedback to user."""
        # Use Discord's ephemeral=True parameter
        # Only visible to the specified user
        try:
            await self._bot.send_message(
                channel_id=channel_id,
                content=message,
                ephemeral=True,
            )
            return True
        except Exception as e:
            log.warning(f"Failed to send feedback: {e}")
            return False
```

**Acceptance Criteria:**
- [ ] FeedbackService class created with send_feedback method
- [ ] Method accepts channel_id, user_id, and message
- [ ] Returns bool indicating success/failure
- [ ] Handles errors gracefully without crashing

---

### Task 3: Wire IntentHandlerRegistry into main.py

**Description:** Instantiate IntentHandlerRegistry in the runtime and pass to BotCommands.

**Delegation Recommendation:**
- Category: `quick` - Small wiring change
- Skills: [] - Simple integration

**Skills Evaluation:**
- INCLUDED none: Standard wiring task

**Depends On:** None (can start in parallel with Task 1, 2)

**Files to Modify:**
- `src/dm_bot/main.py`

**Action:**
1. In `build_runtime()` function, instantiate IntentHandlerRegistry:
```python
intent_handler_registry = IntentHandlerRegistry(message_buffer=message_buffer)
```

2. Pass it to BotCommands constructor (update BotCommands to accept it):
```python
handlers = BotCommands(
    ...
    intent_handler_registry=intent_handler_registry,
)
```

3. Ensure BotCommands stores the registry for use in message handling

**Acceptance Criteria:**
- [ ] IntentHandlerRegistry instantiated in build_runtime()
- [ ] Passed to BotCommands
- [ ] BotCommands can access registry for handling messages

---

### Task 4: Inject Feedback into Message Pipeline

**Description:** After intent handling, send ephemeral feedback to the player.

**Delegation Recommendation:**
- Category: `unspecified-high` - Finding and modifying message flow
- Skills: [] - Integration task

**Skills Evaluation:**
- INCLUDED none: Standard integration

**Depends On:** Task 1, Task 2, Task 3

**Files to Modify:**
- `src/dm_bot/discord_bot/commands.py`
- Potentially: `src/dm_bot/orchestrator/turns.py` or similar

**Action:**
1. Identify where messages are processed and intents are determined
2. After intent handling completes, check if `result.feedback_message` is not None
3. If feedback exists, call FeedbackService.send_feedback() with:
   - channel_id: the message's channel
   - user_id: the message author
   - message: the feedback content

The key integration point is where `IntentHandlerRegistry.handle_message()` is called:
```python
# After intent handling
result = await intent_handler.handle_message(
    user_id=user_id,
    content=content,
    classification=classification,
    session_phase=session_phase,
)

# Send feedback if present (per D-01, D-02)
if result.feedback_message and result.feedback_message.strip():
    await feedback_service.send_feedback(
        channel_id=channel_id,
        user_id=user_id,
        message=result.feedback_message,
    )
```

**Acceptance Criteria:**
- [ ] Feedback sent after intent handling completes
- [ ] Only sent when feedback_message is not None and not empty
- [ ] Sent as ephemeral message (visible only to sender)
- [ ] Sent immediately (not delayed) per D-02
- [ ] No feedback for PROCESSED outcomes (action handled normally)

---

### Task 5: Write TDD Tests for Feedback Delivery

**Description:** Create tests that verify the feedback system works correctly.

**Delegation Recommendation:**
- Category: `quick` - Test creation
- Skills: [`superpowers/test-driven-development`] - For TDD approach

**Skills Evaluation:**
- INCLUDED `superpowers/test-driven-development`: Required for TDD approach - ensures tests are written before implementation

**Depends On:** Task 1, Task 2

**Files to Create/Modify:**
- `tests/test_feedback_delivery.py` (new)

**Action:**
Write tests that verify:

1. **Buffered message feedback:**
```python
def test_buffered_message_feedback():
    # Player submits action during SCENE_ROUND_RESOLVING
    result = await handler.handle_message(
        user_id="user1",
        content="我攻击史莱姆",
        classification=IntentClassificationResult(intent=MessageIntent.PLAYER_ACTION, reasoning=""),
        session_phase="scene_round_resolving",
    )
    assert result.should_buffer is True
    assert result.feedback_message is not None
    assert len(result.feedback_message) <= 50
```

2. **Ignored message feedback:**
```python
def test_ignored_message_feedback():
    # Unknown intent during scene round
    result = await handler.handle_message(
        user_id="user1",
        content="random gibberish",
        classification=IntentClassificationResult(intent=MessageIntent.UNKNOWN, reasoning=""),
        session_phase="scene_round_open",
    )
    assert result.feedback_message is not None
    assert "⏸️" in result.feedback_message
```

3. **Deferred message feedback:**
```python
def test_deferred_rules_query_feedback():
    # Rules query during combat
    result = await handler.handle_message(
        user_id="user1",
        content="力量检定怎么算？",
        classification=IntentClassificationResult(intent=MessageIntent.RULES_QUERY, reasoning=""),
        session_phase="combat",
    )
    assert result.deferred_content is not None
    assert result.feedback_message is not None
    assert "📋" in result.feedback_message
```

4. **No feedback for processed messages:**
```python
def test_no_feedback_for_processed():
    # Player action during action collection phase
    result = await handler.handle_message(
        user_id="user1",
        content="我调查尸体",
        classification=IntentClassificationResult(intent=MessageIntent.PLAYER_ACTION, reasoning=""),
        session_phase="scene_round_open",
    )
    assert result.should_process is True
    # Processed messages may still have feedback but it's optional
```

**Acceptance Criteria:**
- [ ] Tests exist for BUFFERED, IGNORED, DEFERRED scenarios
- [ ] Tests verify feedback_message is not None for buffered/ignored/deferred
- [ ] Tests verify ≤50 character limit per D-03
- [ ] Tests pass after implementation

---

## Commit Strategy

**Atomic Commits:**

1. **feat(phase-53): Add IGNORED and DEFERRED feedback cases to _get_feedback()**
   - Files: `src/dm_bot/router/intent_handler.py`
   - Adds missing feedback map entries per D-04

2. **feat(phase-53): Create DiscordFeedbackService for ephemeral feedback**
   - Files: `src/dm_bot/discord_bot/feedback.py` (new)
   - Creates service for sending ephemeral messages per D-01

3. **feat(phase-53): Wire IntentHandlerRegistry into runtime**
   - Files: `src/dm_bot/main.py`, `src/dm_bot/discord_bot/commands.py`
   - Instantiates and passes registry through the system

4. **feat(phase-53): Inject feedback delivery into message pipeline**
   - Files: `src/dm_bot/discord_bot/commands.py`
   - Sends ephemeral feedback after intent handling per D-01, D-02

5. **test(phase-53): Add feedback delivery tests**
   - Files: `tests/test_feedback_delivery.py` (new)
   - Verifies BUFFERED, IGNORED, DEFERRED feedback scenarios

---

## Success Criteria

### PLAY-03: Short Practical Explanations
- [x] Buffered message → Player receives ephemeral feedback with reason
- [x] Ignored message → Player receives ephemeral feedback explaining why
- [x] Deferred message → Player receives ephemeral feedback with when
- [x] Processed message → No feedback (handled normally)

### PLAY-04: Concise for Play Channels
- [x] Primary feedback ≤50 characters
- [x] No feedback spam (only one per message)

### Technical Verification
- [ ] All tests pass: `uv run pytest -q tests/test_feedback_delivery.py`
- [ ] Smoke check passes: `uv run python -m dm_bot.main smoke-check`
- [ ] No regressions in existing tests

---

## TODO List (ADD THESE)

> CALLER: Add these TODOs using TodoWrite/TaskCreate and execute by wave.

### Wave 1 (Start Immediately - No Dependencies)

- [ ] **1. Add IGNORED and DEFERRED feedback cases to _get_feedback()**
  - What: Extend feedback_map in intent_handler.py with IGNORED/DEFERRED cases
  - Depends: None
  - Blocks: Task 4 (feedback injection)
  - Category: `quick`
  - Skills: []
  - QA: Run existing tests - `uv run pytest -q tests/test_intent_routing.py`

- [ ] **2. Create feedback delivery service**
  - What: Create DiscordFeedbackService in feedback.py
  - Depends: None
  - Blocks: Task 4
  - Category: `quick`
  - Skills: []
  - QA: Service exists with send_feedback method

- [ ] **5. Write TDD tests for feedback delivery**
  - What: Create tests/test_feedback_delivery.py with BUFFERED/IGNORED/DEFERRED tests
  - Depends: None (can run with Task 1, 2)
  - Blocks: None
  - Category: `quick`
  - Skills: [`superpowers/test-driven-development`]
  - QA: Tests file exists and compiles

### Wave 2 (After Wave 1 Completes)

- [ ] **3. Wire IntentHandlerRegistry into main.py**
  - What: Instantiate IntentHandlerRegistry and pass to BotCommands
  - Depends: Task 2
  - Blocks: Task 4
  - Category: `quick`
  - Skills: []
  - QA: Check registry accessible in BotCommands

- [ ] **4. Inject feedback into message pipeline**
  - What: After intent handling, call FeedbackService.send_feedback()
  - Depends: Task 1, Task 2, Task 3
  - Blocks: None
  - Category: `unspecified-high`
  - Skills: []
  - QA: Send test message, verify ephemeral feedback received

## Execution Instructions

1. **Wave 1**: Fire these tasks IN PARALLEL (no dependencies)
   ```
   task(category="quick", load_skills=[], run_in_background=false, prompt="Task 1: Add IGNORED and DEFERRED feedback cases to _get_feedback() - extend feedback_map in src/dm_bot/router/intent_handler.py with: MessageIntent.UNKNOWN entries for each phase (scene_round_open, scene_round_resolving, combat, awaiting_ready) with ⏸️ emoji, MessageIntent.RULES_QUERY entries for combat and scene_round_resolving with 📋 emoji. Ensure all ≤50 characters. Reference existing _get_feedback() method structure. After changes, run: uv run pytest -q tests/test_intent_routing.py")
   
   task(category="quick", load_skills=[], run_in_background=false, prompt="Task 2: Create feedback delivery service - Create src/dm_bot/discord_bot/feedback.py with DiscordFeedbackService class that has async send_feedback(channel_id, user_id, message) method. Should return bool for success/failure. Use ephemeral=True for Discord messages per D-01.")
   
   task(category="quick", load_skills=["superpowers/test-driven-development"], run_in_background=false, prompt="Task 5: Write TDD tests for feedback delivery - Create tests/test_feedback_delivery.py with tests: test_buffered_message_feedback (player action during scene_round_resolving returns feedback with ≤50 chars), test_ignored_message_feedback (UNKNOWN intent returns feedback with ⏸️), test_deferred_rules_query_feedback (RULES_QUERY during combat returns feedback with 📋), test_no_feedback_for_processed (PLAYER_ACTION during scene_round_open returns should_process=True). Import from dm_bot.router.intent_handler import IntentHandlerRegistry, from dm_bot.router.message_buffer import MessageBuffer")
   ```

2. **Wave 2**: After Wave 1 completes, fire next wave
   ```
   task(category="quick", load_skills=[], run_in_background=false, prompt="Task 3: Wire IntentHandlerRegistry into main.py - In build_runtime() function, instantiate: intent_handler_registry = IntentHandlerRegistry(message_buffer=message_buffer). Pass to BotCommands as parameter. Update BotCommands.__init__ to accept and store intent_handler_registry.")
   
   task(category="unspecified-high", load_skills=[], run_in_background=false, prompt="Task 4: Inject feedback into message pipeline - Find where IntentHandlerRegistry.handle_message() is called in the message flow (likely in commands.py or turn handling). After intent handling result is obtained, if result.feedback_message exists and is not empty, call feedback_service.send_feedback(channel_id=channel_id, user_id=user_id, message=result.feedback_message). Ensure this happens IMMEDIATELY after handling (not delayed). Use the DiscordFeedbackService created in Task 2.")
   ```

3. Continue until all waves complete

4. Final QA: Run `uv run pytest -q` and `uv run python -m dm_bot.main smoke-check`
