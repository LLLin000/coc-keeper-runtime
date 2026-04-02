# Phase 51 Research: Data Mapping

This document maps the planned `VisibilitySnapshot` data structure to existing Track C and orchestration models to accelerate Phase 51 execution.

## Visibility Block Mapping

### 1. `CampaignVisibility`
*Source:* `src/dm_bot/orchestrator/session_store.py -> CampaignSession`
*   `campaign_id`: `CampaignSession.campaign_id`
*   `channel_id`: `CampaignSession.channel_id`
*   `member_ids`: `CampaignSession.member_ids`
*   `owner_id`: `CampaignSession.owner_id`

### 2. `AdventureVisibility`
*Source:* To be derived from current runtime context (usually held by `AdventureRuntime` or the campaign record itself, representing loaded module flags).
*   `adventure_id` / `module_name`: Needed from orchestrator state.

### 3. `SessionVisibility`
*Source:* `src/dm_bot/orchestrator/session_store.py -> CampaignSession`
*   `phase`: `CampaignSession.session_phase` (Enum mapping)
*   `admin_started`: `CampaignSession.admin_started`
*   `ready_players`: Derived from `CampaignSession.player_ready` dict.
*   `onboarding_complete`: Derived from `CampaignSession.all_onboarding_complete()`

### 4. `WaitingVisibility`
*Source:* Derived logic based on `CampaignSession.session_phase` and `pending_actions`.
*   `reason_code`: e.g., `WAITING_FOR_PLAYERS`, `WAITING_FOR_ADMIN_START`, `WAITING_FOR_ROUND_ACTIONS`.
*   `message`: e.g., "Waiting for player actions."
*   `metadata`: `{"pending_users": session.get_pending_members()}` from `session_store.py`.

### 5. `PlayerVisibility`
*Source:* `src/dm_bot/coc/panels.py -> InvestigatorPanel`
*   `user_id`: `InvestigatorPanel.user_id`
*   `name`: `InvestigatorPanel.name`
*   `hp`: `InvestigatorPanel.hp`
*   `san`: `InvestigatorPanel.san`
*   `mp`: `InvestigatorPanel.mp`
*   `luck`: `InvestigatorPanel.luck`

### 6. `RoutingVisibility`
*Source:* `src/dm_bot/router/intent_handler.py -> IntentHandlingResult`
*   `processed`: `IntentHandlingResult.should_process`
*   `buffered`: `IntentHandlingResult.should_buffer`
*   `feedback`: `IntentHandlingResult.feedback_message`
*   `intent`: Extracted from `MessageIntentMetadata` when a message routes.

## Execution Notes
No new canonical truth sources are required. `VisibilityBuilder` just needs references to `CampaignSession`, a list of `InvestigatorPanel`, and optionally an `IntentHandlingResult` if querying in the context of a message resolution.
