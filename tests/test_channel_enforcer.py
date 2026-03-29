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


class TestDISC02GameCommands:
    """DISC-02: Channel enforcement gates for specific game commands.

    Tests join_campaign, ready, load_adventure, and profiles commands
    which are covered by the game_policy.
    """

    def test_join_campaign_allowed_in_game_channel(self) -> None:
        """join_campaign allowed when game channel is bound."""
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("join_campaign", "g1", "game-chan")

        assert allowed is True
        assert message is None

    def test_join_campaign_rejected_in_archive_channel(self) -> None:
        """join_campaign rejected in archive channel when game channel is bound."""
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="archive-chan")
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("join_campaign", "g1", "archive-chan")

        assert allowed is False
        assert "游戏大厅" in message

    def test_join_campaign_allowed_in_general_channel_when_no_game_bound(self) -> None:
        store = SessionStore()
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("join_campaign", "g1", "any-chan")

        assert allowed is True
        assert message is None

    def test_ready_allowed_in_game_channel(self) -> None:
        """ready command allowed in game channel."""
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("ready", "g1", "game-chan")

        assert allowed is True
        assert message is None

    def test_ready_rejected_in_archive_channel(self) -> None:
        """ready command rejected in archive channel."""
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="archive-chan")
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("ready", "g1", "archive-chan")

        assert allowed is False
        assert "游戏大厅" in message

    def test_ready_allowed_in_general_channel_when_only_archive_bound(self) -> None:
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="archive-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("ready", "g1", "general-chan")

        assert allowed is True
        assert message is None

    def test_load_adventure_allowed_in_game_channel(self) -> None:
        """load_adventure allowed in game channel."""
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("load_adventure", "g1", "game-chan")

        assert allowed is True
        assert message is None

    def test_load_adventure_rejected_in_archive_channel(self) -> None:
        """load_adventure rejected in archive channel."""
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="archive-chan")
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command(
            "load_adventure", "g1", "archive-chan"
        )

        assert allowed is False
        assert "游戏大厅" in message

    def test_profiles_command_allowed_in_archive_channel(self) -> None:
        """profiles command allowed in archive channel."""
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="archive-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("profiles", "g1", "archive-chan")

        assert allowed is True
        assert message is None

    def test_profiles_command_allowed_in_general_when_archive_not_bound(self) -> None:
        """profiles allowed in general channel when no archive channel is bound."""
        store = SessionStore()
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("profiles", "g1", "any-chan")

        assert allowed is True
        assert message is None

    def test_profiles_command_rejected_in_game_channel_without_archive_binding(
        self,
    ) -> None:
        """profiles rejected in game channel only if archive channel is also bound."""
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        store.bind_archive_channel(guild_id="g1", channel_id="archive-chan")
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("profiles", "g1", "game-chan")

        assert allowed is False
        assert "角色档案" in message

    def test_unpolicied_command_allowed(self) -> None:
        """Commands without policy are always allowed."""
        store = SessionStore()
        enforcer = ChannelEnforcer(session_store=store)

        allowed, message = enforcer.check_command("unknown_command", "g1", "any-chan")

        assert allowed is True
        assert message is None

    def test_channel_type_detection_game(self) -> None:
        """channel_type_for returns GAME for bound game channel."""
        store = SessionStore()
        store.bind_game_channel(guild_id="g1", channel_id="game-chan")
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "game-chan")

        assert result == ChannelType.GAME

    def test_channel_type_detection_archive(self) -> None:
        """channel_type_for returns ARCHIVE for bound archive channel."""
        store = SessionStore()
        store.bind_archive_channel(guild_id="g1", channel_id="archive-chan")
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "archive-chan")

        assert result == ChannelType.ARCHIVE

    def test_channel_type_detection_general(self) -> None:
        """channel_type_for returns GENERAL for unbound channel."""
        store = SessionStore()
        enforcer = ChannelEnforcer(session_store=store)

        result = enforcer.channel_type_for("g1", "any-chan")

        assert result == ChannelType.GENERAL
