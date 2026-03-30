import json

from pydantic import ValidationError

from dm_bot.models.schemas import ModelRequest, TurnEnvelope
from dm_bot.router.contracts import TurnPlan
from dm_bot.router.intent import MessageIntent


class RouterError(RuntimeError):
    pass


class RouterService:
    def __init__(self, client) -> None:
        self._client = client

    async def route(
        self,
        envelope: TurnEnvelope,
        session_phase: str = "lobby",
        intent: MessageIntent = MessageIntent.UNKNOWN,
        intent_reasoning: str = "",
    ) -> TurnPlan:
        request = ModelRequest(
            system_prompt=(
                "You are the routing model for a Discord Call of Cthulhu Keeper runtime. "
                "Return only valid JSON with keys: mode, tool_calls, state_intents, narration_brief, speaker_hints. "
                "mode must be one of dm, scene, combat. tool_calls and state_intents must be arrays. "
                "narration_brief must be a short string. speaker_hints must be an array of speaker names."
            ),
            user_prompt=(
                f"trace_id={envelope.trace_id}\n"
                f"campaign_id={envelope.campaign_id}\n"
                f"channel_id={envelope.channel_id}\n"
                f"user_id={envelope.user_id}\n"
                f"session_phase={session_phase}\n"
                f"classified_intent={intent.value}\n"
                f"intent_reasoning={intent_reasoning}\n"
                f"player_input={envelope.content}"
            ),
            response_format={"type": "json_object"},
        )
        response = await self._client.call_router(request)
        try:
            payload = self._normalize_payload(json.loads(response.content))
            payload["intent"] = intent.value
            payload["intent_reasoning"] = intent_reasoning
            return TurnPlan.model_validate(payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise RouterError("router returned invalid structured output") from exc

    def _normalize_payload(self, payload: dict[str, object]) -> dict[str, object]:
        tool_calls = []
        for item in list(payload.get("tool_calls", [])):
            if isinstance(item, str):
                tool_calls.append({"name": item, "arguments": {}})
            elif isinstance(item, dict):
                tool_calls.append(
                    {
                        "name": item.get("name") or item.get("tool"),
                        "arguments": item.get("arguments") or item.get("params") or {},
                    }
                )
            else:
                tool_calls.append(item)

        state_intents = []
        for item in list(payload.get("state_intents", [])):
            if isinstance(item, str):
                state_intents.append({"kind": item, "payload": {}})
            else:
                state_intents.append(item)

        payload["tool_calls"] = tool_calls
        payload["state_intents"] = state_intents
        payload.setdefault("speaker_hints", [])
        return payload
