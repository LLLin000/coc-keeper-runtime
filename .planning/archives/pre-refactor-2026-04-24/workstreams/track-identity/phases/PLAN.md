# track-identity v1.0 Implementation Plan

> **Non-canonical note:** This file is supplementary planning context only. GSD phase discovery and `/gsd-plan-phase` use numeric `Phase N:` sections in [ROADMAP.md](C:/Users/Lin/Documents/Playground/.planning/workstreams/track-identity/ROADMAP.md) as the source of truth.

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze archive schema, establish two-tier builder, formalize import/delete/COC-validation contracts for track-identity v1.0.

**Architecture:** Six phases executed sequentially. Phase 1 establishes schema truth; phases 2-6 build on it. All new code is behind feature flags / entry point checks until phases are complete.

**Tech Stack:** Python + Pydantic v2 + SQLAlchemy 2.0 + existing `dm_bot.coc.archive`, `dm_bot.coc.builder`, `dm_bot.characters` modules.

---

## Quick Reference: Key Code Issues Found During Survey

| Issue | Location | Fix |
| ----- | -------- | --- |
| `schema_version` default=2 but `create_profile()` passes 3 | `archive.py:22` vs `archive.py:327` | Lock to 3, update default |
| `COCInvestigatorProfile` has no `schema_version` | `characters/models.py:61` | Add `schema_version` field |
| `ModelGuidedInterviewPlanner` exists but is never the primary | `builder.py:232` | Make it primary, heuristic fallback |
| No hard delete command | `archive.py:delete_profile()` | Add `hard_delete_profile()` |
| No paste import | N/A | New `PasteCharacterImporter` class |
| No COC validation at finalize | `builder.py` finalize flow | Add `COCFinalizeValidator` |

---

## Phase Index

| Phase | Name | Status |
| ----- | ---- | ------ |
| 01 | archive-schema-freeze | pending |
| 02 | builder-two-tier | pending |
| 03 | model-guided-interview | pending |
| 04 | import-paste | pending |
| 05 | soft-delete-hard-delete | pending |
| 06 | coc-validation | pending |

---

## Phase 01: archive-schema-freeze

**Goal:** Lock `InvestigatorArchiveProfile.schema_version` to 3, document all fields, add `schema_version` to `COCInvestigatorProfile`, write `v1.0-SPEC.md`.

**Files:**
- Modify: `src/dm_bot/coc/archive.py:22`
- Modify: `src/dm_bot/characters/models.py:61`
- Create: `.planning/workstreams/track-identity/v1.0-SPEC.md`

### Steps

- [ ] **Step 1: Read current archive.py schema_version usage**

Run: `rg "schema_version" src/dm_bot/coc/archive.py src/dm_bot/characters/models.py`
Expected: `archive.py:22` default=2, `archive.py:327` hardcoded 3, `characters/models.py` has none

- [ ] **Step 2: Lock schema_version to 3 in InvestigatorArchiveProfile**

Edit `archive.py:22`: change `schema_version: int = 2` to `schema_version: int = 3`

- [ ] **Step 3: Add schema_version to COCInvestigatorProfile**

Edit `characters/models.py` after line 76: add `schema_version: int = 1 = Field(default=1)`

- [ ] **Step 4: Write v1.0-SPEC.md documenting all archive fields**

Create `.planning/workstreams/track-identity/v1.0-SPEC.md` with full field inventory for `InvestigatorArchiveProfile`, `COCInvestigatorProfile`, `COCAttributes`, and the soft-delete lifecycle.

- [ ] **Step 5: Add test for schema_version consistency**

Create `tests/coc/test_archive_schema.py`:
```python
def test_archive_profile_schema_version_is_3():
    from dm_bot.coc.archive import InvestigatorArchiveProfile
    profile = InvestigatorArchiveProfile.model_fields["schema_version"]
    assert profile.default == 3

def test_coc_investigator_profile_has_schema_version():
    from dm_bot.characters.models import COCInvestigatorProfile
    assert "schema_version" in COCInvestigatorProfile.model_fields
```

- [ ] **Step 6: Run tests**

Run: `uv run pytest tests/coc/test_archive_schema.py -v`
Expected: PASS (2 tests)

- [ ] **Step 7: Commit**

```bash
git add src/dm_bot/coc/archive.py src/dm_bot/characters/models.py
git add .planning/workstreams/track-identity/v1.0-SPEC.md
git commit -m "identity(v1.0): lock archive schema_version to 3, add COC schema_version field"
```

---

## Phase 02: builder-two-tier

**Goal:** Add fast-path builder entry point alongside existing full interview path. Fast path: occupation template -> 3 key questions -> auto-generate rest -> skill allocation -> finalize.

**Files:**
- Modify: `src/dm_bot/coc/builder.py` — add `FastCharacterBuilder` class and entry points
- Create: `src/dm_bot/coc/fast_builder.py` — fast path implementation
- Create: `tests/coc/test_fast_builder.py`

### Steps

- [ ] **Step 1: Read existing builder.py start() and answer() flow**

Understand `ConversationalCharacterBuilder.start()` returns `INTRO_QUESTION` and `BuilderSession` tracks `stage`.

- [ ] **Step 2: Add FAST_INTRO_QUESTION and FAST_PATH_SLOTS constants**

In `builder.py` after `REQUIRED_INTERVIEW_SLOTS`:
```python
FAST_PATH_SLOTS = ["core_belief", "weakness", "key_past_event"]
FAST_INTRO_QUESTION = "欢迎使用快速建卡。請選擇或輸入您的職業（如：記者、醫生、私家偵探）："
FAST_QUESTION_MAP = {
    "core_belief": "在故事開始前，告訴我這位調查員的核心信念是什麼？",
    "weakness": "他/她最大的弱點或致命缺陷是什麼？",
    "key_past_event": "過去有什麼關鍵事件塑造了現在的他/她？",
}
```

- [ ] **Step 3: Add `start_fast()` method to ConversationalCharacterBuilder**

```python
def start_fast(self, *, user_id: str, occupation: str, visibility: str = "private") -> str:
    """Start a fast-path builder session.
    
    Args:
        user_id: The user ID
        occupation: Pre-selected occupation template
    
    Returns:
        First question text
    """
    if self._archive_repository.active_profile(user_id) is not None:
        return "你已有激活档案。请先归档或替换当前主角色，再开始新的建卡。"
    session = BuilderSession(user_id=user_id, visibility=visibility, stage="fast")
    session.answers["occupation"] = occupation
    session.current_slot = "core_belief"
    session.asked_slots = ["occupation", "core_belief"]
    self._sessions[user_id] = session
    return FAST_QUESTION_MAP["core_belief"]
```

- [ ] **Step 4: Add `_answer_fast()` handling in ConversationalCharacterBuilder.answer()**

Modify the `answer()` method to detect `session.stage == "fast"` and route to fast path:
```python
async def answer(self, *, user_id: str, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]:
    session = self._sessions[user_id]
    if session.stage == "fast":
        return await self._answer_fast(session=session, answer=answer)
    # ... existing interview flow
```

- [ ] **Step 5: Implement `_answer_fast()`

```python
async def _answer_fast(self, *, session: BuilderSession, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]:
    slot = session.current_slot
    session.raw_answers[slot] = answer
    session.answers.update(self._answer_normalizer.normalize_slot(slot=slot, raw=answer))
    
    if slot == "core_belief":
        session.current_slot = "weakness"
        return FAST_QUESTION_MAP["weakness"], None
    if slot == "weakness":
        session.current_slot = "key_past_event"
        return FAST_QUESTION_MAP["key_past_event"], None
    
    # All 3 answered → generate full profile
    semantic_fields = await self._semantic_extractor.extract(session)
    synthesis = await self._synthesizer.synthesize(session, semantic_fields)
    payload = self._section_normalizer.to_writeback(
        answers=session.answers,
        synthesis=synthesis,
        answer_normalizer=self._answer_normalizer,
    )
    session.pending_writeback = payload
    session.stage = "fast_finalize"
    session.portrait_summary = _build_interview_portrait(payload)
    return _build_fast_finalization_prompt(session), None
```

- [ ] **Step 6: Add `_build_fast_finalization_prompt()` and finalize handler**

```python
def _build_fast_finalization_prompt(session: BuilderSession) -> str:
    return (
        f"{session.portrait_summary}\n\n"
        "快速建卡已完成。如果想调整技能分配，请回复技能列表（2-4项，用逗号分隔）。\n"
        "如果人物画像没问题，回复 `定卡` 或 `确认`。"
    )
```

Handle `session.stage == "fast_finalize"` in `answer()`: route to existing finalize logic (skill list or `定卡`).

- [ ] **Step 7: Add test for fast builder flow**

Create `tests/coc/test_fast_builder.py`:
```python
@pytest.mark.asyncio
async def test_fast_builder_complete():
    repo = InvestigatorArchiveRepository()
    builder = ConversationalCharacterBuilder(archive_repository=repo)
    
    q1 = builder.start_fast(user_id="user1", occupation="记者")
    assert "職業" in q1
    
    q2, _ = await builder.answer(user_id="user1", answer="真相值得追到底")
    assert "弱點" in q2
    
    q3, _ = await builder.answer(user_id="user1", answer="酗酒")
    assert "關鍵事件" in q3
    
    q4, _ = await builder.answer(user_id="user1", answer="报道失误导致停职")
    assert "定卡" in q4 or "確認" in q4
    
    _, profile = await builder.answer(user_id="user1", answer="定卡")
    assert profile is not None
    assert profile.coc.occupation == "记者"
```

- [ ] **Step 8: Run tests**

Run: `uv run pytest tests/coc/test_fast_builder.py tests/coc/test_builder.py -v`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add src/dm_bot/coc/builder.py tests/coc/test_fast_builder.py
git commit -m "identity(v1.0): add two-tier builder with fast path (occupation + 3 questions)"
```

---

## Phase 03: model-guided-interview

**Goal:** Make `ModelGuidedInterviewPlanner` the primary path with `HeuristicInterviewPlanner` as explicit fallback. Define failure trigger. Expose model-guided entry for all three components (planner, extractor, synthesizer).

**Files:**
- Modify: `src/dm_bot/coc/builder.py` — update `ConversationalCharacterBuilder` to accept model_client and configure model-guided primary
- Modify: `src/dm_bot/models/` — check how model_client is used
- Create: `tests/coc/test_model_guided.py`

### Steps

- [ ] **Step 1: Read how ModelGuidedInterviewPlanner is constructed**

Look at `builder.py:232-272`. The `ModelGuidedInterviewPlanner.__init__` takes `model_client` and optional `fallback`. Currently `ConversationalCharacterBuilder.__init__` sets `_interview_planner = HeuristicInterviewPlanner()` as the default.

- [ ] **Step 2: Update ConversationalCharacterBuilder.__init__ signature**

Change default from `HeuristicInterviewPlanner()` to using model-guided with heuristic fallback:
```python
def __init__(
    self,
    *,
    archive_repository: InvestigatorArchiveRepository,
    roll_provider=None,
    model_client=None,  # NEW
    interview_planner: InterviewPlanner | None = None,
    semantic_extractor: ArchiveSemanticExtractor | None = None,
    answer_normalizer: AnswerNormalizer | None = None,
    synthesizer: CharacterSheetSynthesizer | None = None,
    section_normalizer: SectionNormalizer | None = None,
) -> None:
    # ...
    if interview_planner is not None:
        self._interview_planner = interview_planner
    elif model_client is not None:
        self._interview_planner = ModelGuidedInterviewPlanner(
            model_client=model_client,
            fallback=HeuristicInterviewPlanner(),
        )
    else:
        self._interview_planner = HeuristicInterviewPlanner()
```

- [ ] **Step 3: Apply same pattern to semantic_extractor and synthesizer**

```python
if semantic_extractor is not None:
    self._semantic_extractor = semantic_extractor
elif model_client is not None:
    self._semantic_extractor = ModelGuidedArchiveSemanticExtractor(
        model_client=model_client,
        fallback=HeuristicArchiveSemanticExtractor(),
    )
else:
    self._semantic_extractor = HeuristicArchiveSemanticExtractor()

if synthesizer is not None:
    self._synthesizer = synthesizer
elif model_client is not None:
    self._synthesizer = ModelGuidedCharacterSheetSynthesizer(
        model_client=model_client,
        fallback=HeuristicCharacterSheetSynthesizer(),
    )
else:
    self._synthesizer = HeuristicCharacterSheetSynthesizer()
```

- [ ] **Step 4: Add model failure audit logging**

In `ModelGuidedInterviewPlanner.next_question()`, catch all exceptions and log with `self._log_failure()`:
```python
import logging
logger = logging.getLogger(__name__)

async def next_question(self, session: BuilderSession) -> BuilderQuestionChoice:
    try:
        # ... existing model call
    except Exception as e:
        logger.warning(
            "ModelGuidedInterviewPlanner failed, falling back to heuristic",
            extra={"user_id": session.user_id, "error": str(e)},
        )
    return await self._fallback.next_question(session)
```

Apply same pattern to `ModelGuidedArchiveSemanticExtractor.extract()` and `ModelGuidedCharacterSheetSynthesizer.synthesize()`.

- [ ] **Step 5: Add model-guided failure trigger config**

```python
MODEL_GUIDED_FAILURE_THRESHOLD = 3  # consecutive failures before switching to heuristic-only

class ModelGuidedInterviewPlanner:
    def __init__(self, *, model_client, fallback: InterviewPlanner | None = None, max_retries: int = 2):
        self._model_client = model_client
        self._fallback = fallback or HeuristicInterviewPlanner()
        self._max_retries = max_retries
        self._consecutive_failures = 0
```

After 3 consecutive model failures, mark as degraded and skip model calls.

- [ ] **Step 6: Add tests for model-guided fallback**

Create `tests/coc/test_model_guided.py`:
```python
class TestModelGuidedFallback:
    """Test model-guided with heuristic fallback."""

    @pytest.mark.asyncio
    async def test_model_guided_falls_back_on_error(self):
        """When model client raises, heuristic fallback is used."""
        repo = InvestigatorArchiveRepository()
        failing_client = MockModelClient(raises=True)
        builder = ConversationalCharacterBuilder(
            archive_repository=repo,
            model_client=failing_client,
        )
        
        builder.start(user_id="user1")
        q, _ = await builder.answer(user_id="user1", answer="张三")
        # Should not raise — heuristic fallback used
        assert q is not None
```

- [ ] **Step 7: Run tests**

Run: `uv run pytest tests/coc/test_model_guided.py tests/coc/test_builder.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add src/dm_bot/coc/builder.py tests/coc/test_model_guided.py
git commit -m "identity(v1.0): make model-guided primary with heuristic fallback and audit logging"
```

---

## Phase 04: import-paste

**Goal:** Implement manual paste import with AI-assisted parsing. User pastes character sheet text; AI parses into `CharacterRecord` / `COCInvestigatorProfile`; user reviews and confirms.

**Files:**
- Create: `src/dm_bot/characters/paste_importer.py` — `PasteCharacterImporter` class
- Modify: `src/dm_bot/characters/importer.py` — add paste route
- Create: `tests/test_character_import.py` (update)

### Steps

- [ ] **Step 1: Read existing importer.py and sources.py**

`importer.py` routes `provider` string to source class. `sources.py` has `DicecloudSnapshotSource` and `COCInvestigatorSource`.

- [ ] **Step 2: Define paste import format spec in v1.0-SPEC.md**

Add section to `v1.0-SPEC.md`:
```markdown
### Paste Import Format

User pastes raw character sheet text. Parser expects sections:
- Name / Occupation / Age
- Characteristics (STR, CON, DEX, APP, POW, SIZ, INT, EDU)
- Derived stats (SAN, HP, MP, Luck)
- Skills list

Parser extracts using regex patterns. User reviews extracted `CharacterRecord` before saving.
```

- [ ] **Step 3: Implement PasteCharacterImporter**

```python
class PasteCharacterImporter:
    """Import character from pasted text using AI-assisted parsing."""
    
    def __init__(self, *, model_client) -> None:
        self._model_client = model_client
    
    async def parse(self, raw_text: str) -> CharacterRecord:
        """Parse pasted text into CharacterRecord.
        
        Args:
            raw_text: Raw character sheet text pasted by user
            
        Returns:
            CharacterRecord with COC data populated
            
        Raises:
            ParseError: If text cannot be parsed
        """
        request = ModelRequest(
            system_prompt=(
                "你是克苏鲁呼唤7版的Keeper，正在从玩家粘贴的角色卡文本中提取结构化数据。"
                "从文本中提取：姓名、职业、年龄、三维（STR/CON/DEX/APP/POW/SIZ/INT/EDU）、SAN、HP、MP、Luck、技能列表。"
                "只返回JSON，对应CharacterRecord和COCInvestigatorProfile的结构。"
                "如果某字段无法从文本确定，使用合理的默认值（SAN=POW值，HP=(CON+SIZ)//10，MP=POW//5）。"
            ),
            user_prompt=f"角色卡文本:\n{raw_text}",
            response_format={"type": "json_object"},
        )
        try:
            response = await self._model_client.call_router(request)
            payload = json.loads(response.content)
            return self._build_record(payload)
        except Exception as e:
            raise ParseError(f"无法解析角色卡文本: {e}") from e
    
    def _build_record(self, payload: dict) -> CharacterRecord:
        # Build COCInvestigatorProfile from parsed payload
        # Build CharacterRecord with source=PasteImport
        ...
```

- [ ] **Step 4: Add paste route to CharacterImporter**

Modify `importer.py`:
```python
class CharacterImporter:
    _SOURCE_REGISTRY = {
        "dicecloud": DicecloudSnapshotSource,
        "coc_pregen": COCInvestigatorSource,
        "paste": PasteCharacterImporter,  # NEW
    }
```

- [ ] **Step 5: Write tests for paste importer**

```python
class TestPasteImporter:
    @pytest.mark.asyncio
    async def test_parses_valid_coc_text(self):
        importer = PasteCharacterImporter(model_client=MockModelClient())
        text = """
        姓名：张三
        职业：记者
        年龄：34
        STR: 55 CON: 60 DEX: 70 APP: 65
        POW: 75 SIZ: 50 INT: 80 EDU: 85
        SAN: 75 HP: 11 MP: 15 Luck: 45
        技能：图书馆使用60、心理学55、说服50
        """
        record = await importer.parse(text)
        assert record.name == "张三"
        assert record.coc.occupation == "记者"
```

- [ ] **Step 6: Run tests**

Run: `uv run pytest tests/test_character_import.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/dm_bot/characters/paste_importer.py src/dm_bot/characters/importer.py
git add tests/test_character_import.py
git commit -m "identity(v1.0): add paste import with AI-assisted character sheet parsing"
```

---

## Phase 05: soft-delete-hard-delete

**Goal:** Implement permanent delete command. Archive now supports: soft-delete (7-day grace), expired-but-recoverable status, and hard delete.

**Files:**
- Modify: `src/dm_bot/coc/archive.py` — add `hard_delete_profile()`, update `purge_expired_deleted()` and `recover_profile()` for expired state
- Modify: `src/dm_bot/orchestrator/gameplay.py` — add `/delete-character --permanent` command handler
- Create: `tests/test_character_archive_flow.py` (update with hard delete tests)

### Steps

- [ ] **Step 1: Add `hard_delete_profile()` to InvestigatorArchiveRepository**

```python
def hard_delete_profile(
    self, *, user_id: str, profile_id: str, append_event=None
) -> None:
    """Permanently delete a profile. Irreversible.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        append_event: Optional callback to log the deletion event
    
    Raises:
        ValueError: If profile not found
    """
    if user_id not in self._profiles or profile_id not in self._profiles[user_id]:
        raise ValueError(f"Profile {profile_id} not found")
    profile = self._profiles[user_id][profile_id]
    
    # Log the deletion before removing
    if append_event:
        append_event(
            operation="profile_hard_delete",
            user_id=user_id,
            profile_id=profile_id,
            profile_name=profile.name,
        )
    
    del self._profiles[user_id][profile_id]
    
    # Also remove from persistence
    if self._persistence:
        self._persistence.delete_profile(user_id, profile_id)
```

- [ ] **Step 2: Update `recover_profile()` to handle expired status**

Current code: `recover_profile()` only recovers if status == "deleted". Update to also recover if status == "expired":
```python
def recover_profile(self, *, user_id: str, profile_id: str) -> InvestigatorArchiveProfile:
    profile = self.get_profile(user_id, profile_id)
    if profile.status not in ("deleted", "expired"):
        raise ValueError("Can only recover a deleted or expired profile")
    # After grace period, still allow recovery but require explicit action
    profile.status = "active"
    profile.deleted_at = None
    self._profiles[user_id][profile_id] = profile
    return profile
```

- [ ] **Step 3: Update `purge_expired_deleted()` to mark expired instead of purging**

```python
def purge_expired_deleted(self, *, user_id: str, append_event=None) -> int:
    """Mark deleted profiles past grace period as 'expired'.
    
    Does NOT hard-delete — just transitions to 'expired' status.
    Hard delete requires explicit /delete-character --permanent command.
    """
    marked = 0
    profiles = self._profiles.get(user_id, {})
    for pid, profile in list(profiles.items()):
        if profile.status == "deleted" and profile.deleted_at is not None:
            elapsed = datetime.now(timezone.utc) - profile.deleted_at
            if elapsed.days > GRACE_PERIOD_DAYS:
                profile.status = "expired"
                profiles[pid] = profile
                marked += 1
                if append_event:
                    append_event(
                        operation="profile_expired",
                        user_id=user_id,
                        profile_id=pid,
                    )
    return marked
```

- [ ] **Step 4: Update `list_profiles()` to show expired profiles**

```python
def list_profiles(self, user_id: str) -> list[InvestigatorArchiveProfile]:
    profiles = list(self._profiles.get(user_id, {}).values())
    return sorted(
        profiles,
        key=lambda item: (item.status == "archived", item.status == "expired", item.name)
    )
```

- [ ] **Step 5: Add tests for hard delete and expired state**

In `test_character_archive_flow.py`:
```python
def test_hard_delete_removes_profile():
    repo = InvestigatorArchiveRepository()
    # ... create profile ...
    repo.hard_delete_profile(user_id="user1", profile_id=profile.profile_id)
    assert "user1" not in repo._profiles or profile.profile_id not in repo._profiles["user1"]

def test_expired_profile_can_be_recovered():
    # Set up expired profile
    repo._profiles["user1"]["p1"].status = "expired"
    profile = repo.recover_profile(user_id="user1", profile_id="p1")
    assert profile.status == "active"
```

- [ ] **Step 6: Run tests**

Run: `uv run pytest tests/test_character_archive_flow.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/dm_bot/coc/archive.py tests/test_character_archive_flow.py
git commit -m "identity(v1.0): add hard delete command and expired status with recovery"
```

---

## Phase 06: coc-validation

**Goal:** Add COC rule validation at finalize. Hard enforcement on characteristics/derived stats (must be generated, not user-set). Soft warnings on skill allocation and SAN range. Allow override with confirmation.

**Files:**
- Create: `src/dm_bot/coc/coc_validator.py` — `COCFinalizeValidator` class
- Modify: `src/dm_bot/coc/builder.py` — integrate validator into `_finalize_from_portrait()`
- Create: `tests/coc/test_coc_validation.py`

### Steps

- [ ] **Step 1: Read existing finalize flow in builder.py**

`_finalize_from_portrait()` at line 589. It currently accepts any finalize reply or skill list without validation.

- [ ] **Step 2: Define COCFinalizeValidator class**

```python
from dataclasses import dataclass

@dataclass
class ValidationResult:
    hard_violations: list[str]  # Cannot proceed — must regenerate
    soft_warnings: list[str]    # Can override with confirmation
    
    @property
    def is_clean(self) -> bool:
        return len(self.hard_violations) == 0 and len(self.soft_warnings) == 0

class COCFinalizeValidator:
    """Validates character sheet against COC 7e rules at finalize.
    
    Hard violations (characteristics/derived stats): cannot be overridden
    Soft violations (skill points, SAN range, skill values): warned but allowed
    """
    
    def validate(self, profile: InvestigatorArchiveProfile) -> ValidationResult:
        hard = []
        soft = []
        
        # Hard: characteristics must be generated by formula, not user-set
        attrs = profile.coc.attributes
        for attr_name, attr_val in {
            "STR": attrs.str, "CON": attrs.con, "DEX": attrs.dex,
            "APP": attrs.app, "POW": attrs.pow, "SIZ": attrs.siz,
            "INT": attrs.int, "EDU": attrs.edu
        }.items():
            if not (15 <= attr_val <= 90):
                hard.append(f"{attr_name}={attr_val} outside COC range [15-90]")
        
        # Hard: derived stats must match formula
        expected_hp = (attrs.con + attrs.siz) // 10
        if profile.coc.hp != expected_hp:
            hard.append(f"HP={profile.coc.hp} does not match formula (CON+SIZ)//10={expected_hp}")
        
        expected_mp = max(0, attrs.pow // 5)
        if profile.coc.mp != expected_mp:
            hard.append(f"MP={profile.coc.mp} does not match formula POW//5={expected_mp}")
        
        expected_san = attrs.pow
        if profile.coc.san != expected_san:
            hard.append(f"SAN={profile.coc.san} does not match starting formula POW={expected_san}")
        
        # Soft: SAN range
        if not (0 <= profile.coc.san <= 99):
            soft.append(f"SAN={profile.coc.san} outside normal range 0-99")
        
        # Soft: skill values
        for skill, value in profile.coc.skills.items():
            if value > 100:
                soft.append(f"技能 {skill}={value} 超过100")
        
        # Soft: skill point pools (approximate)
        # COC 7e: occupation points = EDU*2, interest points = EDU*2
        total_occ = sum(profile.coc.skills.get(s, 0) for s in profile.finishing.recommended_occupation_skills)
        if total_occ > attrs.edu * 2 * 2:  # rough upper bound
            soft.append(f"职业技能总点={total_occ} 超出常规上限（{attrs.edu*2*2}）")
        
        return ValidationResult(hard_violations=hard, soft_warnings=soft)
```

- [ ] **Step 3: Integrate validator into builder finalize flow**

Modify `_finalize_from_portrait()` to call validator before creating profile:
```python
async def _finalize_from_portrait(self, *, session: BuilderSession, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]:
    # ... existing skill list / finalize handling ...
    
    # After skill list update, validate before creating
    validator = COCFinalizeValidator()
    validation = validator.validate(profile)
    
    if validation.hard_violations:
        return (
            f"[硬性规则冲突] 以下数值不符合COC规则，必须重新生成属性：\n"
            + "\n".join(f"  - {v}" for v in validation.hard_violations)
            + "\n\n请回复「重新生成」以重新roll属性，或联系KP。",
            None,
        )
    
    if validation.soft_warnings:
        session.pending_warnings = validation.soft_warnings
        # Store updated profile and proceed with warning
        ...
    
    return final_message, profile
```

- [ ] **Step 4: Add warning display in finalization prompt**

```python
def _build_finalization_prompt(session: BuilderSession) -> str:
    base = f"{session.portrait_summary}\n\n访谈到此告一段落..."
    if getattr(session, "pending_warnings", None):
        base += "\n\n[规则警告]：\n" + "\n".join(f"  ! {w}" for w in session.pending_warnings)
        base += "\n如确认，回复 `定卡` 或 `确认override`。"
    return base
```

- [ ] **Step 5: Write tests**

```python
def test_validator_catches_bad_hp():
    from dm_bot.coc.coc_validator import COCFinalizeValidator
    validator = COCFinalizeValidator()
    
    profile = make_profile(hp=999)  # Invalid HP
    result = validator.validate(profile)
    
    assert any("HP" in v for v in result.hard_violations)

def test_validator_warns_high_skill():
    profile = make_profile(skills={"图书馆使用": 150})
    result = validator.validate(profile)
    
    assert any("超过100" in w for w in result.soft_warnings)
```

- [ ] **Step 6: Run tests**

Run: `uv run pytest tests/coc/test_coc_validation.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/dm_bot/coc/coc_validator.py src/dm_bot/coc/builder.py
git add tests/coc/test_coc_validation.py
git commit -m "identity(v1.0): add COC finalize validator with hard/soft violation handling"
```

---

## End-to-End Verification

After all 6 phases:

- [ ] Run full test suite: `uv run pytest -q`
- [ ] Run smoke check: `uv run python -m dm_bot.main smoke-check`
- [ ] Verify v1.0-SPEC.md is complete with all field documentation

---

## Files Summary

| File | Action |
| ---- | ------ |
| `src/dm_bot/coc/archive.py` | Modify — schema_version lock, hard_delete, expired state |
| `src/dm_bot/characters/models.py` | Modify — add COCInvestigatorProfile.schema_version |
| `src/dm_bot/coc/builder.py` | Modify — model-guided primary, fast builder, validator integration |
| `src/dm_bot/characters/paste_importer.py` | Create — paste import |
| `src/dm_bot/characters/importer.py` | Modify — add paste route |
| `src/dm_bot/coc/coc_validator.py` | Create — COC validation at finalize |
| `tests/coc/test_archive_schema.py` | Create |
| `tests/coc/test_fast_builder.py` | Create |
| `tests/coc/test_model_guided.py` | Create |
| `tests/coc/test_coc_validation.py` | Create |
| `tests/test_character_import.py` | Modify |
| `tests/test_character_archive_flow.py` | Modify |
| `.planning/workstreams/track-identity/v1.0-SPEC.md` | Create |
