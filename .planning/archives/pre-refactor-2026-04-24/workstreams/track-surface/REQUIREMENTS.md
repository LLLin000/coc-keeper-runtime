# Requirements — `track-surface`

## `v1.0` — Session Boards And Runtime-Aware Presentation

### `SUR-01` Session Board Contract

Players and operators must be able to inspect current session state from runtime-owned truth without browsing raw diagnostics.

### `SUR-02` Scene Framing

Scene focus, cross-cut context, and waiting state must be rendered in a way that is readable in Discord and consistent with runtime semantics.

### `SUR-03` Consequence Publication

Consequences must be rendered according to runtime-owned ownership scopes rather than ad hoc string formatting.

### `SUR-04` Clue And History Boards

Shared clue and history surfaces must present canonical shared knowledge without leaking private/KP-only information.

### `SUR-05` Activity-Ready View Contract

Surface payloads must be separable from Discord-specific formatting so richer UI can reuse them later.

## `v1.1` — Identity And Onboarding Surface Integration

### `SUR-06` Archive Card Contract

Archive and identity cards must render long-lived profile truth without mixing in campaign-local state incorrectly.

### `SUR-07` Builder Flow Polish

Builder surfaces must feel DM-first and Keeper-guided without re-owning builder logic.

### `SUR-08` Campaign And Roster Surfaces

Players need clear shared views of campaign identity, roster, and currently bound roles.

### `SUR-09` New-Player Start Pack

Surface-level onboarding must explain the minimum rules and flow needed to start playing quickly.

### `SUR-10` Command Information Architecture

Commands, help copy, and channel guidance must be coherent enough that users know where actions belong.

## `v1.2` — Interactive Discord Surface And Activity Bridge

### `SUR-11` Stateful Views

Longer cards and boards need stateful/paginated presentation within Discord constraints.

### `SUR-12` Component-Driven Actions

Buttons, selects, and follow-up interactions must map cleanly onto runtime- and identity-owned contracts.

### `SUR-13` Delivery Reliability

DM, ephemeral, and public delivery choices must be explicit and dependable across common Discord flows.

### `SUR-14` Activity Bridge Schema

Future Activity UI work must be able to consume the same presentation contracts without re-deriving meaning.

### `SUR-15` Surface QA And Localization

Chinese-first copy, readability, and consistency checks must be part of the surface completion criteria.
