import json

from pydantic import ValidationError

from dm_bot.models.schemas import ModelRequest
from dm_bot.router.intent import (
    IntentClassificationRequest,
    IntentClassificationResult,
    MessageIntent,
    DEFAULT_INTENT,
    get_handling_decision,
    MessageIntentMetadata,
)


class IntentClassifierError(RuntimeError):
    pass


class IntentClassifier:
    def __init__(self, client) -> None:
        self._client = client

    async def classify(
        self, request: IntentClassificationRequest
    ) -> IntentClassificationResult:
        system_prompt = (
            "You are an intent classifier for a Discord Call of Cthulhu Keeper. "
            "Classify the message into one of: ooc, social_ic, player_action, rules_query, admin_action, unknown. "
            "Return ONLY valid JSON with keys: intent, confidence (0.0-1.0), reasoning. "
            "Be conservative with confidence - only use 0.9+ when very certain."
        )

        user_prompt = (
            f"Session phase: {request.session_phase}\n"
            f"User is admin: {request.is_admin}\n"
            f"Message: {request.content}\n\n"
            "Classify this message. Consider:\n"
            "- ooc: Player discussing something out of game, meta-commentary\n"
            "- social_ic: In-character but not an action requiring resolution (greetings, small talk)\n"
            "- player_action: Player attempting something in-game that needs resolution\n"
            "- rules_query: Player asking about game rules or mechanics\n"
            "- admin_action: Command affecting session/adventure (admin only)\n"
            "- unknown: Cannot determine intent"
        )

        model_request = ModelRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
        )

        try:
            response = await self._client.call_router(model_request)
            payload = json.loads(response.content)

            intent_str = payload.get("intent", "unknown")
            confidence = float(payload.get("confidence", 0.5))
            reasoning = payload.get("reasoning", "")

            try:
                intent = MessageIntent(intent_str)
            except ValueError:
                intent = DEFAULT_INTENT
                reasoning = f"Invalid intent '{intent_str}', defaulted to unknown"

            confidence = max(0.0, min(1.0, confidence))

            return IntentClassificationResult(
                intent=intent,
                confidence=confidence,
                reasoning=reasoning,
            )
        except (json.JSONDecodeError, ValidationError, Exception) as exc:
            raise IntentClassifierError(f"Intent classification failed: {exc}") from exc

    def create_metadata(
        self,
        result: IntentClassificationResult,
        session_phase: str,
        handling_decision: str,
        was_buffered: bool = False,
    ) -> MessageIntentMetadata:
        return MessageIntentMetadata(
            intent=result.intent,
            classification_reasoning=result.reasoning,
            handling_decision=handling_decision,
            was_buffered=was_buffered,
            phase_at_classification=session_phase,
        )

    def get_feedback_message(
        self, intent: MessageIntent, session_phase: str
    ) -> str | None:
        decision = get_handling_decision(intent, session_phase)

        feedback_map = {
            MessageIntent.OOC: {
                "scene_round_open": "OOC messages are being deferred during action collection.",
                "scene_round_resolving": "OOC messages are buffered until scene resolves.",
                "combat": "OOC messages are not appropriate during combat.",
            },
            MessageIntent.SOCIAL_IC: {
                "scene_round_resolving": "Social IC messages are buffered during resolution.",
                "combat": "Social IC is limited during combat - actions only.",
            },
            MessageIntent.PLAYER_ACTION: {
                "scene_round_resolving": "Your action has been recorded and will be resolved shortly.",
                "combat": "Your action is being processed.",
            },
            MessageIntent.RULES_QUERY: {
                "scene_round_resolving": "Rules questions are deferred until scene resolves.",
                "combat": "Rules questions cannot be answered during combat.",
            },
        }

        specific_feedback = feedback_map.get(intent, {}).get(session_phase)
        if specific_feedback:
            return f"_{specific_feedback}_"
        return None

    async def classify_message(
        self,
        *,
        trace_id: str,
        campaign_id: str,
        channel_id: str,
        user_id: str,
        content: str,
        session_phase: str,
        is_admin: bool = False,
    ) -> IntentClassificationResult:
        request = IntentClassificationRequest(
            trace_id=trace_id,
            campaign_id=campaign_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            session_phase=session_phase,
            is_admin=is_admin,
        )
        return await self.classify(request)
