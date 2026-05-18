# Store Package Analysis

**Package:** `src/dm_bot/store/`
**File:** `db.py` (71 lines)
**Status:** Minimal persistence layer

---

## 1. Package Purpose and Responsibilities

SQLite persistence layer for the bot. Handles storage and retrieval of:
- Session state (adventure_id, current_scene, scene_state, player locations)
- Character sheets (user_id, session_id, sheet_json)

Does NOT contain business logic.

---

## 2. Key Classes and Signatures

### `Store`

```python
class Store:
    def __init__(self, db_path: str = "dm_bot.db") -> None:
        ...

    def _init_db(self) -> None:
        ...

    def save_session(self, session_id: str, data: dict) -> None:
        ...

    def load_session(self, session_id: str) -> dict | None:
        ...
```

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(db_path: str = "dm_bot.db")` | Initialize DB path and call `_init_db()` |
| `_init_db` | `() -> None` | Private - creates tables if not exist |
| `save_session` | `(session_id: str, data: dict) -> None` | Upsert session row |
| `load_session` | `(session_id: str) -> dict \| None` | Fetch session row or `None` |

---

## 3. Schema (SQLite Tables)

### `sessions`

| Column | Type | Notes |
|--------|------|-------|
| `session_id` | TEXT PRIMARY KEY | Unique session identifier |
| `adventure_id` | TEXT | Active adventure reference |
| `current_scene_id` | TEXT | Current scene in adventure |
| `scene_state` | TEXT | e.g. `waiting`, `collecting`, `resolving`, `narrating` |
| `player_locations` | TEXT | JSON dict: `user_id -> scene_id` |
| `created_at` | TIMESTAMP | Auto-set on creation |

### `characters`

| Column | Type | Notes |
|--------|------|-------|
| `character_id` | TEXT PRIMARY KEY | Unique character identifier |
| `user_id` | TEXT NOT NULL | Discord user ID |
| `session_id` | TEXT | Optional session association |
| `sheet_json` | TEXT | Full character sheet as JSON |

---

## 4. How Store Interacts with Other Packages

Store is the persistence backend consumed by multiple packages:

| Consumer | Access Pattern |
|----------|---------------|
| `scene/` | Calls `store.save_session()` after state transitions; `load_session()` on startup |
| `character/` | Calls `save_session`/`load_session` for sheet persistence |

Data flow:
```
scene.round.resolve() -> store.save_session(session_id, data)
character.builder.complete() -> store.save_session(..., data)
discord_bot.on_ready() -> store.load_session(session_id) -> scene.restore()
```

---

## 5. Design Patterns Used

**Repository Pattern** — `Store` wraps raw SQLite into a domain-friendly interface with `save_session` / `load_session` methods.

**JSON Column Pattern** — `player_locations` and `sheet_json` store structured dicts as JSON text. Caller is responsible for `json.dumps()` / `json.loads()`.

**Upsert Pattern** — `save_session` uses `INSERT ... ON CONFLICT(session_id) DO UPDATE SET` for atomic create-or-update.

---

## 6. Dependencies

Store imports only from stdlib:

| Import | Source | Purpose |
|--------|--------|---------|
| `sqlite3` | stdlib | SQLite database |
| `pathlib.Path` | stdlib | Path handling for `db_path` |
| `json` | stdlib | Serializing/deserializing `player_locations` and `sheet_json` |

**Outgoing dependencies:** None (store does not import other `dm_bot` packages).

**Incoming dependencies:** `scene`, `character` (at runtime, not at import time).

---

## 7. Notes

- No type stubs or Pydantic models — raw dicts passed in/out
- No connection pooling — each operation opens a fresh `sqlite3.connect()`
- No transaction batching — `save_session` is auto-committed per call
- `characters` table defined but no `save_character` / `load_character` methods exist yet — the table was scaffolded in anticipation of `character/` builder use but methods were not implemented