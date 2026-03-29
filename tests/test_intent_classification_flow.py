"""ROUTER-03: Intent classification and buffering flow tests."""

import pytest
from dm_bot.router.intent import (
    MessageIntent,
    should_buffer_intent,
    get_intent_priority,
    get_handling_decision,
    MessageIntentMetadata,
)


def test_should_buffer_intent_scene_round_resolving_player_action():
    """PLAYER_ACTION is buffered during scene_round_resolving phase."""
    assert (
        should_buffer_intent(MessageIntent.PLAYER_ACTION, "scene_round_resolving")
        is True
    )


def test_should_buffer_intent_scene_round_resolving_admin_action():
    """ADMIN_ACTION is NOT buffered during scene_round_resolving phase."""
    assert (
        should_buffer_intent(MessageIntent.ADMIN_ACTION, "scene_round_resolving")
        is False
    )


def test_should_buffer_intent_scene_round_resolving_ooc():
    """OOC is buffered during scene_round_resolving phase."""
    assert should_buffer_intent(MessageIntent.OOC, "scene_round_resolving") is True


def test_should_buffer_intent_combat_player_action():
    """PLAYER_ACTION is NOT buffered during combat (each action resolved immediately)."""
    assert should_buffer_intent(MessageIntent.PLAYER_ACTION, "combat") is False


def test_should_buffer_intent_combat_admin_action():
    """ADMIN_ACTION is NOT buffered during combat."""
    assert should_buffer_intent(MessageIntent.ADMIN_ACTION, "combat") is False


def test_should_buffer_intent_combat_ooc():
    """OOC is buffered during combat."""
    assert should_buffer_intent(MessageIntent.OOC, "combat") is True


def test_should_buffer_intent_other_phases_not_buffered():
    """Messages are not buffered during other phases (e.g., scene_round_open)."""
    assert (
        should_buffer_intent(MessageIntent.PLAYER_ACTION, "scene_round_open") is False
    )
    assert should_buffer_intent(MessageIntent.OOC, "lobby") is False


def test_get_intent_priority_scene_round_open_player_action():
    """PLAYER_ACTION has highest priority (10) during scene_round_open."""
    priority = get_intent_priority(MessageIntent.PLAYER_ACTION, "scene_round_open")
    assert priority == 10


def test_get_intent_priority_lobby_admin_action():
    """ADMIN_ACTION has highest priority (10) during lobby."""
    priority = get_intent_priority(MessageIntent.ADMIN_ACTION, "lobby")
    assert priority == 10


def test_get_intent_priority_scene_round_resolving_admin_action():
    """ADMIN_ACTION has highest priority (10) during scene_round_resolving."""
    priority = get_intent_priority(MessageIntent.ADMIN_ACTION, "scene_round_resolving")
    assert priority == 10


def test_get_intent_priority_combat_player_action():
    """PLAYER_ACTION has highest priority (10) during combat."""
    priority = get_intent_priority(MessageIntent.PLAYER_ACTION, "combat")
    assert priority == 10


def test_get_handling_decision_buffers_player_action():
    """get_handling_decision() returns 'buffered' for bufferable intents."""
    decision = get_handling_decision(
        MessageIntent.PLAYER_ACTION, "scene_round_resolving"
    )
    assert "buffered" in decision.lower()


def test_get_handling_decision_admin_not_buffered():
    """get_handling_decision() returns 'immediately' for admin actions."""
    decision = get_handling_decision(
        MessageIntent.ADMIN_ACTION, "scene_round_resolving"
    )
    assert "immediately" in decision.lower() or "processed" in decision.lower()


def test_get_handling_decision_unknown_phase_defaults():
    """get_handling_decision() handles unknown phases gracefully."""
    decision = get_handling_decision(MessageIntent.PLAYER_ACTION, "unknown_phase")
    assert decision is not None
    assert len(decision) > 0


def test_message_intent_metadata_fields():
    """MessageIntentMetadata contains all required fields."""
    metadata = MessageIntentMetadata(
        intent=MessageIntent.PLAYER_ACTION,
        classification_reasoning="player is taking an action",
        handling_decision="buffered",
        was_buffered=True,
        phase_at_classification="scene_round_resolving",
    )
    assert metadata.intent == MessageIntent.PLAYER_ACTION
    assert metadata.classification_reasoning == "player is taking an action"
    assert metadata.handling_decision == "buffered"
    assert metadata.was_buffered is True
    assert metadata.phase_at_classification == "scene_round_resolving"


def test_message_intent_values():
    """All MessageIntent enum values are defined."""
    assert MessageIntent.OOC.value == "ooc"
    assert MessageIntent.SOCIAL_IC.value == "social_ic"
    assert MessageIntent.PLAYER_ACTION.value == "player_action"
    assert MessageIntent.RULES_QUERY.value == "rules_query"
    assert MessageIntent.ADMIN_ACTION.value == "admin_action"
    assert MessageIntent.UNKNOWN.value == "unknown"
