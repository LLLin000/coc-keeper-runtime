import asyncio
from pathlib import Path

from dm_bot.diagnostics.service import DiagnosticsService
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.coc.archive import InvestigatorArchiveRepository
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.persistence.store import PersistenceStore


class FakeResponse:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bool]] = []

    async def send_message(self, content: str, ephemeral: bool = False) -> None:
        self.messages.append((content, ephemeral))


class FakeInteraction:
    def __init__(self, *, channel_id: str = "chan-1", guild_id: str = "guild-1", user_id: str = "user-1") -> None:
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user = type("User", (), {"id": user_id})()
        self.response = FakeResponse()


class StubTurnRunner:
    async def run_turn(self, envelope):
        return type("TurnResult", (), {"reply": "战斗开始。"})()


def test_diagnostics_service_returns_recent_trace_summary(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "diag.sqlite3")
    store.append_event(campaign_id="camp-1", trace_id="trace-1", event_type="turn.completed", payload={"reply": "ok"})
    service = DiagnosticsService(store)

    summary = service.recent_summary("camp-1")

    assert "trace-1" in summary


def test_diagnostics_service_reports_adventure_state_summary(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "diag.sqlite3")
    store.save_campaign_state(
        "camp-1",
        {
            "adventure_state": {
                "scene_id": "blood_hall",
                "location_id": "blood_hall",
                "story_node_id": "wetland_ambush",
                "clues_found": ["blood_exit_rule", "clock_countdown"],
                "knowledge_log": [{"scope": "player", "recipient_user_id": "user-1", "title": "论坛照片", "content": "你认出了那个少女。"}],
                "objectives": ["找到出口"],
                "module_state": {
                    "time_remaining": 120,
                    "blood_required": 25,
                    "blood_collected": 11,
                    "san_pressure": 2,
                    "danger_level": "high",
                    "pending_push": "life_library_research",
                    "module_rule_mode": "fuzhe",
                },
                "pending_roll": {"id": "life_library_research", "action": "ability_check"},
                "ending_id": None,
            }
        },
    )
    service = DiagnosticsService(store)

    summary = service.recent_summary("camp-1")

    assert "blood_hall" in summary
    assert "story_node=wetland_ambush" in summary
    assert "120" in summary
    assert "blood_exit_rule" in summary
    assert "knowledge_entries=1" in summary
    assert "pending_roll=life_library_research" in summary
    assert "san_pressure=2" in summary
    assert "danger_level=high" in summary
    assert "module_rule_mode=fuzhe" in summary


def test_debug_command_surfaces_recent_events(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "diag.sqlite3")
    store.append_event(campaign_id="camp-1", trace_id="trace-1", event_type="turn.completed", payload={"reply": "ok"})
    commands = BotCommands(
        settings=None,
        session_store=None,
        turn_coordinator=None,
        gameplay=None,
        diagnostics=DiagnosticsService(store),
    )
    interaction = FakeInteraction()

    asyncio.run(commands.debug_status(interaction, campaign_id="camp-1"))

    assert "trace-1" in interaction.response.messages[0][0]


def test_diagnostics_service_surfaces_trigger_events(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "diag.sqlite3")
    store.append_event(
        campaign_id="camp-1",
        trace_id="trigger-clock",
        event_type="trigger.effect_applied",
        payload={"trigger_id": "clock_inspection", "effect": "add_clue", "clue_id": "clock_countdown"},
    )
    service = DiagnosticsService(store)

    summary = service.recent_summary("camp-1")

    assert "trigger.effect_applied" in summary


def test_diagnostics_service_reports_archive_projection_sync(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "diag.sqlite3")
    sessions = SessionStore()
    sessions.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    repo = InvestigatorArchiveRepository()
    profile = repo.create_profile(
        user_id="user-1",
        name="林秋",
        occupation="记者",
        age=26,
        background="夜班记者",
        disposition="冷静",
        favored_skills=["图书馆使用"],
        generation={
            "str": 50, "con": 55, "dex": 60, "app": 65, "pow": 70, "siz": 50, "int": 75, "edu": 80, "luck": 45
        },
    )
    sessions.select_archive_profile(channel_id="chan-1", user_id="user-1", profile_id=profile.profile_id)
    store.save_campaign_state(
        "camp-1",
        {
            "panels": {
                "user-1": {
                    "user_id": "user-1",
                    "name": "林秋",
                    "role": "investigator",
                    "occupation": "记者",
                    "san": profile.coc.san,
                    "hp": profile.coc.hp,
                    "mp": profile.coc.mp,
                    "luck": profile.coc.luck,
                    "skills": dict(profile.coc.skills),
                    "journal": [],
                    "module_flags": {"archive_profile_id": profile.profile_id},
                }
            }
        },
    )
    service = DiagnosticsService(store, session_store=sessions, archive_repository=repo)

    summary = service.recent_summary("camp-1")

    assert "profile_sync:user-1=synced:林秋" in summary
