"""ROUTER-02: MessageBuffer flow tests."""

import pytest
from datetime import datetime
from dm_bot.router.message_buffer import MessageBuffer, BufferedMessage
from dm_bot.router.intent import MessageIntent, MessageIntentMetadata


@pytest.fixture
def buffer():
    return MessageBuffer()


@pytest.fixture
def metadata():
    return MessageIntentMetadata(
        intent=MessageIntent.PLAYER_ACTION,
        classification_reasoning="looks like a game action",
        handling_decision="buffered",
        was_buffered=True,
        phase_at_classification="scene_round_resolving",
    )


def test_buffer_message_returns_true(buffer, metadata):
    """buffer_message() returns True when message is buffered."""
    result = buffer.buffer_message(
        "ch1", "u1", "我检查书架", MessageIntent.PLAYER_ACTION, metadata
    )
    assert result is True


def test_get_buffered_messages_all_for_channel(buffer, metadata):
    """get_buffered_messages() returns all buffered messages for a channel."""
    buffer.buffer_message(
        "ch1", "u1", "message 1", MessageIntent.PLAYER_ACTION, metadata
    )
    buffer.buffer_message(
        "ch1", "u2", "message 2", MessageIntent.PLAYER_ACTION, metadata
    )
    msgs = buffer.get_buffered_messages("ch1")
    assert len(msgs) == 2


def test_release_buffered_messages_clears_buffer(buffer, metadata):
    """release_buffered_messages() clears buffer and returns messages."""
    buffer.buffer_message("ch1", "u1", "message", MessageIntent.PLAYER_ACTION, metadata)
    msgs = buffer.release_buffered_messages("ch1")
    assert len(msgs) == 1
    assert buffer.has_buffered_messages("ch1") is False


def test_clear_buffer_without_return(buffer, metadata):
    """clear_buffer() removes buffer without returning messages."""
    buffer.buffer_message("ch1", "u1", "message", MessageIntent.PLAYER_ACTION, metadata)
    buffer.clear_buffer("ch1")
    assert buffer.has_buffered_messages("ch1") is False


def test_has_buffered_messages_true_when_present(buffer, metadata):
    """has_buffered_messages() returns True when messages exist."""
    buffer.buffer_message("ch1", "u1", "message", MessageIntent.PLAYER_ACTION, metadata)
    assert buffer.has_buffered_messages("ch1") is True


def test_has_buffered_messages_false_when_empty(buffer):
    """has_buffered_messages() returns False when no messages buffered."""
    assert buffer.has_buffered_messages("ch1") is False


def test_buffer_multiple_users(buffer, metadata):
    """Messages from multiple users are buffered separately by channel."""
    buffer.buffer_message(
        "ch1", "u1", "Alice message", MessageIntent.PLAYER_ACTION, metadata
    )
    buffer.buffer_message(
        "ch1", "u2", "Bob message", MessageIntent.PLAYER_ACTION, metadata
    )
    buffer.buffer_message(
        "ch2", "u3", "Other channel", MessageIntent.PLAYER_ACTION, metadata
    )
    assert len(buffer.get_buffered_messages("ch1")) == 2
    assert len(buffer.get_buffered_messages("ch2")) == 1


def test_format_buffered_message_summary(buffer, metadata):
    """format_buffered_message_summary() returns formatted user-facing summary."""
    buffer.buffer_message(
        "ch1", "u1", "检查书架", MessageIntent.PLAYER_ACTION, metadata
    )
    buffer.buffer_message(
        "ch1", "u1", "翻阅文件", MessageIntent.PLAYER_ACTION, metadata
    )
    summary = buffer.format_buffered_message_summary("ch1")
    assert summary is not None
    assert "Buffered Messages" in summary


def test_format_buffered_message_summary_empty_channel(buffer):
    """format_buffered_message_summary() returns None for empty channel."""
    summary = buffer.format_buffered_message_summary("ch_empty")
    assert summary is None


def test_get_buffer_summary(buffer, metadata):
    """get_buffer_summary() returns dict with message counts and timestamps."""
    buffer.buffer_message(
        "ch1", "u1", "message 1", MessageIntent.PLAYER_ACTION, metadata
    )
    buffer.buffer_message(
        "ch1", "u2", "message 2", MessageIntent.PLAYER_ACTION, metadata
    )
    summary = buffer.get_buffer_summary("ch1")
    assert summary["total"] == 2
    assert "by_intent" in summary
    assert summary["oldest"] is not None
    assert summary["newest"] is not None


def test_buffer_respects_channel_isolation(buffer, metadata):
    """Messages are isolated by channel - different channels don't share buffers."""
    buffer.buffer_message(
        "ch1", "u1", "ch1 message", MessageIntent.PLAYER_ACTION, metadata
    )
    buffer.buffer_message("ch2", "u2", "ch2 message", MessageIntent.OOC, metadata)
    assert len(buffer.get_buffered_messages("ch1")) == 1
    assert len(buffer.get_buffered_messages("ch2")) == 1
    buffer.release_buffered_messages("ch1")
    assert buffer.has_buffered_messages("ch1") is False
    assert buffer.has_buffered_messages("ch2") is True
