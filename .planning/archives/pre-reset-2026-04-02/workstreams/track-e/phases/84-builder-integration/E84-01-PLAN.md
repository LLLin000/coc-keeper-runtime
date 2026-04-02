---
phase: E84-builder-integration
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/testing/runtime_driver.py
  - src/dm_bot/orchestrator/gameplay.py
  - tests/coc/test_builder.py
  - tests/scenarios/acceptance/scen_character_builder.yaml
autonomous: true
requirements:
  - BUILDER-01
  - BUILDER-02
  - BUILDER-03
  - BUILDER-04

must_haves:
  truths:
    - "Character builder is accessible through RuntimeTestDriver"
    - "Builder produces valid archive-compatible profiles"
    - "Builder validates against COC rules (point totals, skill limits)"
    - "E2E scenario validates full builder → archive → projection flow"
  artifacts:
    - path: "src/dm_bot/testing/runtime_driver.py"
      provides: "Builder methods: start_character_build, answer_builder_question"
      exports: ["start_character_build", "answer_builder_question"]
    - path: "src/dm_bot/orchestrator/gameplay.py"
      provides: "Builder integration with archive"
      exports: ["character_builder"]
    - path: "tests/coc/test_builder.py"
      provides: "Builder flow unit tests"
      min_lines: 80
  key_links:
    - from: "runtime_driver.py"
      to: "builder.py"
      via: "character_builder instance"
    - from: "builder.py"
      to: "archive.py"
      via: "archive_repository.create_profile"
---

<objective>
Wire character builder into RuntimeTestDriver and validate full builder flow.

Purpose: Enable character creation through conversational interview in tests.
Output: Builder integrated with RuntimeTestDriver and E2E scenario.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@src/dm_bot/coc/builder.py
@src/dm_bot/coc/archive.py
@src/dm_bot/orchestrator/gameplay.py
@src/dm_bot/testing/runtime_driver.py

## Key Types from Existing Code

From builder.py:
```python
class ConversationalCharacterBuilder:
    def start(self, *, user_id: str, visibility: str = "private") -> str
    async def answer(self, *, user_id: str, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]
    def has_session(self, user_id: str) -> bool
```

From archive.py:
```python
class InvestigatorArchiveProfile(BaseModel):
    profile_id: str
    name: str
    occupation: str
    coc: COCInvestigatorProfile
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Wire builder into GameplayOrchestrator</name>
  <files>src/dm_bot/orchestrator/gameplay.py</files>
  <action>
Add character builder to GameplayOrchestrator:

```python
# Add to GameplayOrchestrator class

from dm_bot.coc.builder import ConversationalCharacterBuilder
from dm_bot.coc.archive import InvestigatorArchiveRepository

def __init__(
    self,
    importer: CharacterImporter,
    registry: CharacterRegistry,
    rules_engine: RulesEngine,
    archive_repository: InvestigatorArchiveRepository | None = None,
) -> None:
    self.importer = importer
    self.registry = registry
    self.rules_engine = rules_engine
    self.archive_repository = archive_repository
    
    # Initialize character builder if archive available
    self.character_builder: ConversationalCharacterBuilder | None = None
    if archive_repository:
        self.character_builder = ConversationalCharacterBuilder(
            archive_repository=archive_repository,
        )

def get_builder(self) -> ConversationalCharacterBuilder | None:
    """Get the character builder instance."""
    return self.character_builder
```

Update _build_commands in runtime_driver.py to pass archive_repository:
```python
def _build_commands(...):
    # ... existing code ...
    
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    archive_repository = InvestigatorArchiveRepository()
    
    gameplay = GameplayOrchestrator(
        importer=...,
        registry=...,
        rules_engine=...,
        archive_repository=archive_repository,
    )
    
    # ... rest of the code ...
```
  </action>
  <verify>
    <automated>grep -n "character_builder\|archive_repository" src/dm_bot/orchestrator/gameplay.py | head -10</automated>
  </verify>
  <done>Character builder wired into GameplayOrchestrator</done>
</task>

<task type="auto">
  <name>Task 2: Add builder methods to RuntimeTestDriver</name>
  <files>src/dm_bot/testing/runtime_driver.py</files>
  <action>
Add builder methods to RuntimeTestDriver:

```python
async def start_character_build(self, user_id: str) -> dict:
    """Start character building interview.
    
    Args:
        user_id: The user starting the build
        
    Returns:
        Dict with question and session info
    """
    if not self._gameplay:
        raise RuntimeError("Gameplay not initialized")
    
    builder = self._gameplay.get_builder()
    if not builder:
        raise RuntimeError("Character builder not available")
    
    question = builder.start(user_id=user_id)
    
    return {
        "started": True,
        "question": question,
        "user_id": user_id,
        "has_session": builder.has_session(user_id),
    }

async def answer_builder_question(
    self,
    user_id: str,
    answer: str,
) -> dict:
    """Answer a builder question.
    
    Args:
        user_id: The user answering
        answer: The answer text
        
    Returns:
        Dict with next question or completed profile
    """
    if not self._gameplay:
        raise RuntimeError("Gameplay not initialized")
    
    builder = self._gameplay.get_builder()
    if not builder:
        raise RuntimeError("Character builder not available")
    
    if not builder.has_session(user_id):
        raise RuntimeError(f"No builder session for user {user_id}")
    
    next_question, profile = await builder.answer(
        user_id=user_id,
        answer=answer,
    )
    
    result = {
        "answered": True,
        "question": next_question,
        "has_profile": profile is not None,
    }
    
    if profile:
        result["profile"] = profile.model_dump()
        result["profile_id"] = profile.profile_id
    
    return result

def get_builder_session(self, user_id: str) -> dict:
    """Get current builder session state.
    
    Args:
        user_id: The user to check
        
    Returns:
        Session state dict
    """
    if not self._gameplay:
        return {"error": "Gameplay not initialized"}
    
    builder = self._gameplay.get_builder()
    if not builder:
        return {"error": "Character builder not available"}
    
    return {
        "has_session": builder.has_session(user_id),
        "user_id": user_id,
    }

def cancel_builder_session(self, user_id: str) -> dict:
    """Cancel a builder session.
    
    Args:
        user_id: The user to cancel for
        
    Returns:
        Result dict
    """
    if not self._gameplay:
        return {"error": "Gameplay not initialized"}
    
    builder = self._gameplay.get_builder()
    if not builder:
        return {"error": "Character builder not available"}
    
    # Remove session if exists
    if builder.has_session(user_id):
        del builder._sessions[user_id]
        return {"cancelled": True}
    
    return {"cancelled": False, "reason": "No active session"}
```
  </action>
  <verify>
    <automated>grep -n "def start_character_build\|def answer_builder_question" src/dm_bot/testing/runtime_driver.py</automated>
  </verify>
  <done>RuntimeTestDriver builder methods added</done>
</task>

<task type="auto">
  <name>Task 3: Create builder unit tests</name>
  <files>tests/coc/test_builder.py</files>
  <action>
Create builder unit tests:

```python
"""Tests for character builder."""

import pytest

from dm_bot.coc.builder import (
    ConversationalCharacterBuilder,
    BuilderSession,
    AnswerNormalizer,
)
from dm_bot.coc.archive import InvestigatorArchiveRepository


class TestBuilderSession:
    """Test builder session management."""
    
    def test_start_interview(self):
        """Test starting an interview."""
        repo = InvestigatorArchiveRepository()
        builder = ConversationalCharacterBuilder(archive_repository=repo)
        
        question = builder.start(user_id="user1")
        
        assert "名字" in question or "name" in question.lower()
        assert builder.has_session("user1")
    
    def test_interview_flow(self):
        """Test basic interview flow."""
        repo = InvestigatorArchiveRepository()
        builder = ConversationalCharacterBuilder(archive_repository=repo)
        
        # Start
        q1 = builder.start(user_id="user1")
        
        # Answer name
        q2, _ = builder.answer(user_id="user1", answer="张三")
        
        # Answer concept
        q3, _ = builder.answer(user_id="user1", answer="38岁的落魄医生")
        
        # Should have more questions
        assert q3 is not None
        assert len(q3) > 0
    
    def test_answer_normalization(self):
        """Test answer normalization."""
        normalizer = AnswerNormalizer()
        
        # Test name normalization
        result = normalizer.normalize_slot(slot="name", raw="  张三  ")
        assert result["name"] == "张三"
        
        # Test age normalization
        result = normalizer.normalize_slot(slot="age", raw="我今年38岁")
        assert result["age"] == "38"
    
    def test_cannot_start_with_active_profile(self):
        """Test that user cannot start if they have active profile."""
        repo = InvestigatorArchiveRepository()
        
        # Create an active profile first
        repo.create_profile(
            user_id="user1",
            name="Existing",
            occupation="Doctor",
            age=30,
            background="Test",
            portrait_summary="Test",
            concept="Test",
            disposition="冷静",
            favored_skills=["医学"],
            generation={
                "str": 50, "con": 50, "dex": 50, "app": 50,
                "pow": 50, "siz": 50, "int": 50, "edu": 50, "luck": 50,
            },
        )
        
        builder = ConversationalCharacterBuilder(archive_repository=repo)
        
        result = builder.start(user_id="user1")
        
        assert "已有激活档案" in result


class TestBuilderProfileCreation:
    """Test profile creation through builder."""
    
    @pytest.mark.asyncio
    async def test_complete_interview_creates_profile(self):
        """Test that completing interview creates a profile."""
        repo = InvestigatorArchiveRepository()
        builder = ConversationalCharacterBuilder(archive_repository=repo)
        
        # Complete interview
        builder.start(user_id="user1")
        builder.answer(user_id="user1", answer="张三")
        builder.answer(user_id="user1", answer="38岁的落魄医生")
        builder.answer(user_id="user1", answer="38")
        builder.answer(user_id="user1", answer="医生")
        
        # Answer dynamic questions until finalization
        # This will take several iterations
        question, profile = builder.answer(user_id="user1", answer="过去发生了医疗事故")
        
        while profile is None and question:
            # Answer with something reasonable
            if "目标" in question:
                answer = "重建声誉"
            elif "弱点" in question:
                answer = "酗酒"
            elif "信念" in question:
                answer = "我是在救人"
            else:
                answer = "继续"
            
            question, profile = builder.answer(user_id="user1", answer=answer)
        
        # Finalize
        if profile is None:
            question, profile = builder.answer(user_id="user1", answer="定卡")
        
        assert profile is not None
        assert profile.name == "张三"
        assert profile.occupation == "医生"
        assert profile.coc.san > 0
    
    def test_profile_has_coc_stats(self):
        """Test that created profile has COC stats."""
        # This would require completing a full interview
        # For now, just verify the structure
        pass


class TestBuilderValidation:
    """Test builder validation."""
    
    def test_skill_list_parsing(self):
        """Test parsing skill lists."""
        from dm_bot.coc.builder import _normalize_skill_list
        
        # Test various formats
        assert _normalize_skill_list("医学, 急救") == ["医学", "急救"]
        assert _normalize_skill_list("医学、急救、侦查") == ["医学", "急救", "侦查"]
        assert _normalize_skill_list("") == []
```
  </action>
  <verify>
    <automated>uv run pytest tests/coc/test_builder.py -v</automated>
  </verify>
  <done>Builder unit tests</done>
</task>

<task type="auto">
  <name>Task 4: Create E2E builder scenario</name>
  <files>tests/scenarios/acceptance/scen_character_builder.yaml</files>
  <action>
Create E2E builder scenario:

```yaml
# Character Builder E2E Scenario
# Validates: interview flow → profile creation → archive storage

scenario:
  id: scen_character_builder
  name: "Character Builder Flow"
  description: "Validates complete character creation through builder"
  
actors:
  - id: p1
    role: player
    name: "测试玩家"

initial_state:
  dice_mode: seeded
  dice_seed: 12345
  
steps:
  # Start builder
  - actor: p1
    action: command
    name: start_character_build
    args:
      user_id: "p1"
      
  - actor: system
    action: assert
    assertions:
      builder_started:
        started: true
        has_session: true
        question:
          contains: ["名字", "name"]
          
  # Answer: Name
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "李明"
      
  - actor: system
    action: assert
    assertions:
      question_received:
        question:
          contains: ["骨架", "concept"]
          
  # Answer: Concept
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "42岁的落魄记者"
      
  # Answer: Age (extracted from concept, but confirm)
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "42"
      
  # Answer: Occupation
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "记者"
      
  # Answer: Key past event
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "报道失误导致无辜者入狱"
      
  # Answer: Life goal
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "揭露真相平反冤案"
      
  # Answer: Weakness
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "酗酒麻痹愧疚"
      
  # Answer: Core belief
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "真相值得追到底"
      
  # Finalize: Should get portrait
  - actor: p1
    action: command
    name: answer_builder_question
    args:
      user_id: "p1"
      answer: "定卡"
      
  - actor: system
    action: assert
    assertions:
      profile_created:
        has_profile: true
        profile:
          name: "李明"
          occupation: "记者"
          age: 42
          coc:
            san: "> 0"
            hp: "> 0"
            attributes:
              str: "> 0"
              
  # Verify in archive
  - actor: p1
    action: command
    name: list_profiles
    args:
      user_id: "p1"
      
  - actor: system
    action: assert
    assertions:
      profile_in_archive:
        count: 1
        profiles:
          - name: "李明"
            occupation: "记者"
            status: "active"

expected_outcomes:
  - builder_flow_completed: true
  - profile_created: true
  - profile_in_archive: true
  - coc_stats_generated: true
```
  </action>
  <verify>
    <automated>cat tests/scenarios/acceptance/scen_character_builder.yaml | head -30</automated>
  </verify>
  <done>E2E builder scenario</done>
</task>

</tasks>

<verification>
Run verification:
1. `uv run pytest tests/coc/test_builder.py -v`
2. `uv run python -m dm_bot.main smoke-check`
</verification>

<success_criteria>
- Character builder in GameplayOrchestrator
- RuntimeTestDriver builder methods
- Builder produces valid profiles
- Profiles saved to archive
- Unit tests for builder flow
- E2E scenario validates full flow
- All existing tests pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/84-builder-integration/E84-01-SUMMARY.md`
</output>
