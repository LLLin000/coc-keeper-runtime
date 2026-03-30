import time
from typing import Any, Callable, Coroutine, cast

from dm_bot.characters.importer import CharacterImporter
from dm_bot.characters.sources import DicecloudSnapshotSource
from dm_bot.config import Settings
from dm_bot.diagnostics.service import DiagnosticsService
from dm_bot.models.ollama_client import OllamaClient
from dm_bot.narration.service import NarrationService
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.orchestrator.turn_runner import TurnRunner
from dm_bot.orchestrator.turns import TurnCoordinator
from dm_bot.persistence.store import PersistenceStore
from dm_bot.router.intent_classifier import IntentClassifier
from dm_bot.router.intent_handler import IntentHandlerRegistry
from dm_bot.router.message_buffer import MessageBuffer
from dm_bot.router.service import RouterService
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine
from dm_bot.testing.step_result import OutputRecord, StepResult
from tests.fakes.clock import FakeClock
from tests.fakes.discord import (
    FakeChannel,
    FakeMessage,
    FakeStreamingTransport,
    fake_interaction,
)
from tests.fakes.models import StubModelClient


_GUILD_ID = "guild-test"
_DEFAULT_CHANNEL_ID = "chan-test"


class ModelModeError(Exception):
    pass


class RuntimeTestDriver:
    def __init__(
        self,
        *,
        dice_seed: int | None = None,
        model_client: StubModelClient | None = None,
        model_mode: str = "fake_contract",
        db_path: str | None = None,
        clock: FakeClock | None = None,
    ) -> None:
        self._dice_seed = dice_seed
        self._model_mode = model_mode
        self._db_path = db_path
        self._clock = clock
        self._commands: Any = None
        self._session_store: SessionStore | None = None
        self._gameplay: GameplayOrchestrator | None = None
        self._turn_coordinator: TurnCoordinator | None = None
        self._transport: FakeStreamingTransport | None = None
        self._started = False
        self._output_records: list[OutputRecord] = []
        self._snapshot_state: dict[str, Any] = {}

        self._model_client = self._create_model_client(model_client)

    def _create_model_client(
        self, explicit_client: StubModelClient | None
    ) -> StubModelClient | OllamaClient:
        if explicit_client is not None:
            return explicit_client

        if self._model_mode == "fake_contract":
            return StubModelClient()
        elif self._model_mode == "recorded":
            raise ModelModeError(
                "recorded mode requires VCR cassettes in tests/cassettes/<scenario_id>/"
            )
        elif self._model_mode == "live":
            try:
                settings = Settings()
                return OllamaClient(settings)
            except Exception as e:
                raise ModelModeError(
                    f"live mode requires Ollama to be running. "
                    f"Start Ollama and try again. Error: {e}"
                )
        else:
            raise ModelModeError(f"Unknown model_mode: {self._model_mode}")

    async def start(self) -> None:
        rules_engine = RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        )

        self._gameplay = GameplayOrchestrator(
            importer=CharacterImporter(
                sources={"dicecloud_snapshot": DicecloudSnapshotSource(fixtures={})}
            ),
            registry=CharacterRegistry(),
            rules_engine=rules_engine,
        )

        model_client = self._model_client
        turn_runner = TurnRunner(
            router=RouterService(model_client),
            narrator=NarrationService(model_client),
            gameplay=self._gameplay,
        )

        self._session_store = SessionStore()
        persistence_store = PersistenceStore(self._db_path)
        self._session_store.load_sessions(persistence_store.load_sessions())

        self._turn_coordinator = TurnCoordinator(
            turn_runner=turn_runner,
            persistence_store=persistence_store,
        )

        self._commands = _build_commands(
            session_store=self._session_store,
            turn_coordinator=self._turn_coordinator,
            gameplay=self._gameplay,
            persistence_store=persistence_store,
            model_client=model_client,
        )

        self._transport = FakeStreamingTransport()
        self._started = True

    async def stop(self) -> None:
        self._started = False
        self._commands = None
        self._session_store = None
        self._gameplay = None
        self._turn_coordinator = None

    def _interaction_for(
        self, actor_id: str, channel_id: str = _DEFAULT_CHANNEL_ID
    ) -> Any:
        return fake_interaction(
            user_id=actor_id,
            channel_id=channel_id,
            guild_id=_GUILD_ID,
            display_name=actor_id,
        )

    def _phase_before(self) -> str:
        if self._session_store is None:
            return ""
        for session in self._session_store._sessions.values():
            return session.session_phase.value
        return ""

    async def run_command(
        self,
        actor_id: str,
        command: str,
        args: dict[str, Any],
    ) -> StepResult:
        if not self._started or self._commands is None:
            raise RuntimeError("driver not started")

        phase_before = self._phase_before()
        interaction = self._interaction_for(actor_id)

        _capture_response_messages(interaction, self._output_records, actor_id)

        method = getattr(self._commands, command, None)
        if method is None:
            return StepResult(
                phase_before=phase_before,
                phase_after=phase_before,
                error=f"unknown command: {command}",
            )

        try:
            cmd = cast(Callable[..., Coroutine[Any, Any, Any]], method)
            import inspect

            sig = inspect.signature(cmd)
            if "interaction" in sig.parameters:
                await cmd(interaction, **args)
            else:
                await cmd(**args)
        except Exception as exc:
            return StepResult(
                phase_before=phase_before,
                phase_after=self._phase_before(),
                error=str(exc),
            )

        return StepResult(
            phase_before=phase_before,
            phase_after=self._phase_before(),
            emitted_outputs=list(self._output_records),
        )

    async def send_message(
        self,
        actor_id: str,
        text: str,
        channel: str | None = None,
    ) -> StepResult:
        if not self._started or self._commands is None:
            raise RuntimeError("driver not started")

        channel_id = channel or _DEFAULT_CHANNEL_ID
        phase_before = self._phase_before()

        channel_obj = FakeChannel(channel_id)
        msg = FakeMessage(text)
        output_start = len(self._output_records)

        original_send = channel_obj.send

        async def tracking_send(content: str) -> Any:
            msg.content = content
            self._output_records.append(
                OutputRecord(
                    audience="public",
                    content=content,
                    timestamp=time.time(),
                    message_type="narration",
                )
            )
            return msg

        channel_obj.send = tracking_send  # type: ignore

        class FakeMessageObj:
            content: str = ""
            channel: Any = channel_obj
            guild: Any = type("G", (), {"id": _GUILD_ID})()
            author: Any = type("A", (), {"id": actor_id})()
            mentions: list[Any] = []

        fake_msg = FakeMessageObj()
        fake_msg.content = text

        try:
            await self._commands.handle_channel_message_stream(message=fake_msg)
        except Exception as exc:
            return StepResult(
                phase_before=phase_before,
                phase_after=self._phase_before(),
                error=str(exc),
            )

        channel_obj.send = original_send  # type: ignore[method-assignment]

        return StepResult(
            phase_before=phase_before,
            phase_after=self._phase_before(),
            emitted_outputs=list(self._output_records[output_start:]),
        )

    def snapshot_state(self) -> dict[str, Any]:
        if self._session_store is None:
            return {}
        state: dict[str, Any] = {
            "sessions": self._session_store.dump_sessions(),
        }
        if self._gameplay is not None:
            state["gameplay"] = self._gameplay.export_state()
        return state

    def snapshot_db(self) -> dict[str, Any]:
        if self._session_store is None:
            return {}
        events: list[dict[str, Any]] = []
        store = (
            self._turn_coordinator._persistence_store
            if self._turn_coordinator
            else None
        )
        if store is not None:
            for session in self._session_store._sessions.values():
                session_events = store.list_events(session.campaign_id)
                events.extend(session_events)
        return {"events": events}

    def get_outputs(self, audience: str) -> list[OutputRecord]:
        return [r for r in self._output_records if r.audience == audience]

    def get_phase(self) -> str:
        if self._session_store is None:
            return ""
        for session in self._session_store._sessions.values():
            return session.session_phase.value
        return ""

    def get_phase_history(self) -> list[dict[str, Any]]:
        if self._session_store is None:
            return []
        history: list[dict[str, Any]] = []
        for session in self._session_store._sessions.values():
            for phase_val, dt in session.phase_history:
                history.append({"phase": phase_val, "timestamp": dt.isoformat()})
        return history

    async def restart_runtime(self) -> None:
        if self._session_store is None:
            return
        self._snapshot_state = self.snapshot_state()
        self._output_records.clear()

    async def simulate_crash(self) -> None:
        self._output_records.clear()
        if self._session_store is not None:
            self._session_store._sessions.clear()

    async def simulate_stream_interrupt(self) -> None:
        if self._transport is not None:
            self._transport.sent_messages.clear()


def _build_commands(
    session_store: SessionStore,
    turn_coordinator: TurnCoordinator,
    gameplay: GameplayOrchestrator,
    persistence_store: PersistenceStore,
    model_client: StubModelClient,
) -> Any:
    coc_assets: Any = None
    archive_repository: Any = None
    character_builder: Any = None
    intent_classifier = IntentClassifier(model_client)
    message_buffer = MessageBuffer()
    intent_handler_registry = IntentHandlerRegistry(message_buffer=message_buffer)
    diagnostics = DiagnosticsService(
        persistence_store,
        session_store=session_store,
        archive_repository=archive_repository,
    )

    from dm_bot.config import Settings
    from dm_bot.discord_bot.commands import BotCommands

    return BotCommands(
        settings=Settings(),
        session_store=session_store,
        turn_coordinator=turn_coordinator,
        gameplay=gameplay,
        diagnostics=diagnostics,
        persistence_store=persistence_store,
        coc_assets=coc_assets,
        archive_repository=archive_repository,
        character_builder=character_builder,
        intent_classifier=intent_classifier,
        message_buffer=message_buffer,
        intent_handler_registry=intent_handler_registry,
    )


def _capture_response_messages(
    interaction: Any, output_records: list[OutputRecord], actor_id: str
) -> None:
    original_send = interaction.response.send_message
    original_followup_send = interaction.followup.send

    async def tracking_send(content: str, **kwargs: Any) -> None:
        ephemeral = kwargs.get("ephemeral", False)
        audience = "kp" if ephemeral else "public"
        output_records.append(
            OutputRecord(
                audience=audience,
                content=content,
                timestamp=time.time(),
                message_type="system",
            )
        )
        await original_send(content, **kwargs)

    async def tracking_followup(content: str, **kwargs: Any) -> None:
        output_records.append(
            OutputRecord(
                audience="kp",
                content=content,
                timestamp=time.time(),
                message_type="system",
            )
        )
        await original_followup_send(content, **kwargs)

    interaction.response.send_message = tracking_send
    interaction.followup.send = tracking_followup
