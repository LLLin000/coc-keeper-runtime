# S14: Startup & Delivery Gate Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Every startup and delivery is reliable and observable.

**Architecture:** Enhance existing preflight/smoke-check. Add CLI status command.

---

### Task 1: Enhanced Preflight — Full System Diagnostics

**Files:**
- Modify: `src/dm_bot/main.py`
- Create: `tests/test_preflight.py`

- [ ] **Step 1: Tests**

```python
"""Tests for preflight/diagnostics."""


class TestPreflight:
    def test_preflight_check_store(self):
        from dm_bot.main import check_store
        import tempfile, os

        result = check_store(":memory:")
        assert result["status"] == "ok"

    def test_preflight_check_modules(self):
        from dm_bot.main import check_modules

        result = check_modules()
        assert result["all_ok"] is True
        assert len(result["modules"]) > 5
```

- [ ] **Step 2: Run -> ImportError**
- [ ] **Step 3: Implement**

Add to `main.py`:

```python
def check_store(db_path: str = ":memory:") -> dict:
    """Verify Store can connect and DB is healthy."""
    try:
        store = Store(db_path)
        integrity = store.check_integrity()
        return integrity
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_modules() -> dict:
    """Verify all runtime modules import correctly."""
    mods = [
        "dm_bot.adventure.models", "dm_bot.trigger.models", "dm_bot.trigger.engine",
        "dm_bot.reveal.models", "dm_bot.reveal.checker",
        "dm_bot.publish.models", "dm_bot.publish.publisher", "dm_bot.publish.contract",
        "dm_bot.store.db", "dm_bot.character.sheet", "dm_bot.character.archive",
        "dm_bot.surface.board", "dm_bot.surface.discord_formatter",
    ]
    results = {}
    all_ok = True
    for mod in mods:
        try:
            __import__(mod)
            results[mod] = "ok"
        except Exception as e:
            results[mod] = str(e)
            all_ok = False
    return {"all_ok": all_ok, "modules": results}


def describe_runtime_full(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    lines = []
    lines.append("=== Discord AI Keeper — Preflight ===")
    lines.append(f"discord_token={'[CONFIGURED]' if settings.discord_token else '[MISSING]'}")
    lines.append(f"narrator_model={settings.narrator_model}")
    lines.append(f"ollama_base_url={settings.ollama_base_url}")

    store_check = check_store()
    lines.append(f"store_integrity={store_check['status']}")

    mods = check_modules()
    lines.append(f"modules={mods['all_ok']}")
    for name, status in mods["modules"].items():
        lines.append(f"  {name}: {status}")

    return "\n".join(lines)
```

Update `preflight` command:
```python
if args.command == "preflight":
    print(describe_runtime_full())
    return 0
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 2: Smoke-Check Distinguishes Failures

**Files:**
- Modify: `src/dm_bot/main.py`
- Modify: `tests/test_preflight.py`

- [ ] **Step 1: Tests**

```python
    def test_smoke_check_ok(self):
        from dm_bot.main import smoke_check

        code = smoke_check()
        assert code == 0
```

- [ ] **Step 2: Implement**

Add to `main.py`:

```python
def smoke_check() -> int:
    """Comprehensive smoke check — separates module vs runtime failure."""
    mods = check_modules()
    if not mods["all_ok"]:
        failed = [n for n, s in mods["modules"].items() if s != "ok"]
        print(f"Smoke check FAILED — module failures: {failed}")
        return 1
    store_check = check_store()
    if store_check.get("status") != "ok":
        print(f"Smoke check FAILED — store: {store_check}")
        return 1
    print("All core modules import successfully. Store: OK.")
    return 0
```

Update smoke-check handler:
```python
if args.command == "smoke-check":
    return smoke_check()
```

- [ ] **Step 3: Tests pass**
- [ ] **Step 4: Commit**

---

### Task 3: Smoke Check and Final Verification

- [ ] **Step 1: `uv run pytest -q` -> ALL PASS**
- [ ] **Step 2: `uv run python -m dm_bot.main smoke-check` -> OK**
- [ ] **Step 3: `uv run python -m dm_bot.main preflight` -> OK**
- [ ] **Step 4: Commit**
