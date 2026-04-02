# Renderer Interface Pattern

This document describes the renderer interface pattern used in the Discord AI DM project for Activity-ready boundary separation.

## Pattern Overview

The renderer pattern separates canonical state from renderer-specific output:

```
VisibilitySnapshot (canonical) → Renderer → Renderer-specific output
```

- **Canonical state**: Pure Pydantic data classes with no rendering dependencies
- **Renderer**: Transforms canonical state into platform-specific output
- **Output**: Discord Embeds, strings, Activity UI data, etc.

## Visibility Layer (Canonical)

All visibility types live in `src/dm_bot/orchestrator/visibility.py`:

```python
from dm_bot.orchestrator.visibility import (
    VisibilitySnapshot,
    PlayerVisibility,
    WaitingReasonCode,
    SessionPhase,
)
```

**Requirements:**
- Zero Discord imports
- Zero rendering logic (no colors, embeds, components)
- Pure Pydantic data classes
- Business logic only (state aggregation, formatting into data structures)

## Renderer Layer

Renderers transform VisibilitySnapshot into platform-specific output:

### Player Status Renderer

```python
from dm_bot.orchestrator.visibility import VisibilitySnapshot
from dm_bot.orchestrator.player_status_renderer import PlayerStatusRenderer

renderer = PlayerStatusRenderer(active_characters={})
snapshot: VisibilitySnapshot = build_visibility_snapshot(...)

overview = renderer.render_overview(snapshot)      # str
concise = renderer.render_concise(snapshot)        # str
detail = renderer.render_personal_detail(snapshot, user_id)  # str
```

### KP Ops Renderer

```python
from dm_bot.orchestrator.visibility import VisibilitySnapshot
from dm_bot.orchestrator.kp_ops_renderer import KPOpsRenderer

renderer = KPOpsRenderer(active_characters={})
snapshot: VisibilitySnapshot = build_visibility_snapshot(...)

overview = renderer.render_overview(snapshot)       # str
detailed = renderer.render_detailed(snapshot)      # str
routing = renderer.render_routing_history(snapshot)  # str
```

## Adding a New Renderer

To add a new renderer (e.g., for Discord Activity UI):

1. Create `src/dm_bot/orchestrator/activity_renderer.py`
2. Import only from `visibility.py`
3. Implement renderer class with render methods
4. Do NOT import Discord types in the renderer

Example:

```python
"""Activity UI rendering for visibility surfaces."""

from dm_bot.orchestrator.visibility import (
    VisibilitySnapshot,
    PlayerVisibility,
    WaitingReasonCode,
)


class ActivityRenderer:
    """Renders VisibilitySnapshot for Discord Activity UI."""

    def render_player_panel(self, snapshot: VisibilitySnapshot, user_id: str) -> dict:
        """Render player panel as JSON-serializable dict for Activity UI."""
        # Transform snapshot data into Activity-compatible format
        return {
            "type": "player_panel",
            "data": {...}
        }
```

## Anti-Patterns to Avoid

### ❌ DON'T: Import Discord in visibility layer
```python
# BAD - couples canonical state to Discord
from discord import Embed
from dm_bot.orchestrator.visibility import VisibilitySnapshot
```

### ❌ DON'T: Put business logic in renderers
```python
# BAD - renderers should only transform data
def render_overview(self, snapshot):
    # Don't compute business logic here
    if session.phase == "combat":
        return compute_combat_state()  # This belongs in visibility layer
```

### ❌ DON'T: Return Discord types from orchestrator controllers
```python
# BAD - Discord types should be created in Discord layer
class OnboardingController:
    def create_view(self):
        return OnboardingView(...)  # Discord-specific, belongs in discord_bot/
```

## Testing Without Discord

Because the visibility layer has no Discord dependencies, it can be tested independently:

```python
# This works without discord.py installed
from dm_bot.orchestrator.visibility import VisibilitySnapshot, PlayerSnapshot

snapshot = VisibilitySnapshot(
    campaign=CampaignVisibility(...),
    ...
)
```

This enables:
- Unit testing visibility logic without Discord infrastructure
- Reuse by non-Discord surfaces (Activity UI, web panels)
- Clean dependency graph
