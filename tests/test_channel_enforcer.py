import pytest
from dm_bot.discord_bot.channel_enforcer import (
    ChannelEnforcer,
    ChannelPolicy,
    ChannelType,
)
from dm_bot.orchestrator.session_store import SessionStore


class TestChannelTypeDetection:
    def test_archive_channel_detected(self) -> None:
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="a1")
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "a1")

        assert result == ChannelType.ARCHIVE

    def test_admin_channel_detected(self) -> None:
        store = SessionStore()
        store.bind_admin_channel(guild_id="g1", channel_id="admin1")
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "admin1")

        assert result == ChannelType.ADMIN

    def test_trace_channel_detected(self) -> None:
        store = SessionStore()
        store.bind_trace_channel(guild_id="g1", channel_id="trace1")
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "trace1")

        assert result == ChannelType.TRACE

    def test_game_channel_detected(self) -> None:
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "game1")

        assert result == ChannelType.GAME

    def test_unbound_channel_returns_general(self) -> None:
        store = SessionStore()
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "random_channel")

        assert result == ChannelType.GENERAL


class TestCommandPolicyEnforcement:
    def test_archive_command_allowed_in_archive_channel(self) -> None:
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="a1")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("sheet", "g1", "a1")

        assert allowed is True
        assert message is None

    def test_archive_command_blocked_in_game_channel(self) -> None:
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="a1")
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("sheet", "g1", "game1")

        assert allowed is False
        assert message is not None
        assert "角色档案" in message

    def test_admin_command_allowed_in_admin_channel(self) -> None:
        store = SessionStore()
        store.bind_admin_channel(guild_id="g1", channel_id="admin1")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("admin_profiles", "g1", "admin1")

        assert allowed is True
        assert message is None

    def test_admin_command_blocked_in_game_channel(self) -> None:
        store = SessionStore()
        store.bind_admin_channel(guild_id="g1", channel_id="admin1")
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("admin_profiles", "g1", "game1")

        assert allowed is False
        assert message is not None

    def test_game_command_allowed_in_game_channel(self) -> None:
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("take_turn", "g1", "game1")

        assert allowed is True
        assert message is None

    def test_game_command_blocked_in_archive_channel(self) -> None:
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="a1")
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("take_turn", "g1", "a1")

        assert allowed is False
        assert message is not None


class TestRedirectMessage:
    def test_redirect_message_includes_correct_channel(self) -> None:
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="a1")
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("sheet", "g1", "game1")

        assert allowed is False
        assert message is not None
        assert "角色档案" in message


class TestCustomPolicyRegistration:
    def test_register_custom_policy(self) -> None:
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game1")
        enforcer = ChannelEnforcer(session_store=store)

        custom_policy = ChannelPolicy(
            command_names=["custom_cmd"],
            allowed_types={ChannelType.GAME},
            redirect_message="Use in game channel",
        )
        enforcer.register_policy(custom_policy)

        allowed, _ = enforcer.check_command("custom_cmd", "g1", "game1")
        assert allowed is True

        allowed, _ = enforcer.check_command("custom_cmd", "g1", "a1")
        assert allowed is False
