import asyncio
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
from tests.fakes.models import ApiModelClient, StubModelClient


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
        self._chase_manager: Any = None
        self._persistence_store: PersistenceStore | None = None

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
        elif self._model_mode == "api":
            return ApiModelClient()
        else:
            raise ModelModeError(f"Unknown model_mode: {self._model_mode}")

    async def start(self) -> None:
        rules_engine = RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        )

        # Import here to avoid circular imports
        from dm_bot.coc.archive import InvestigatorArchiveRepository

        archive_repository = InvestigatorArchiveRepository()

        self._gameplay = GameplayOrchestrator(
            importer=CharacterImporter(
                sources={"dicecloud_snapshot": DicecloudSnapshotSource(fixtures={})}
            ),
            registry=CharacterRegistry(),
            rules_engine=rules_engine,
            archive_repository=archive_repository,
        )

        self._archive_repository = archive_repository

        model_client = self._model_client
        turn_runner = TurnRunner(
            router=RouterService(model_client),
            narrator=NarrationService(model_client),
            gameplay=self._gameplay,
        )

        self._session_store = SessionStore()
        self._persistence_store = PersistenceStore(self._db_path)
        self._session_store.load_sessions(self._persistence_store.load_sessions())

        self._turn_coordinator = TurnCoordinator(
            turn_runner=turn_runner,
            persistence_store=self._persistence_store,
        )

        self._commands = _build_commands(
            session_store=self._session_store,
            turn_coordinator=self._turn_coordinator,
            gameplay=self._gameplay,
            persistence_store=self._persistence_store,
            model_client=model_client,
        )

        self._transport = FakeStreamingTransport()
        self._started = True

    async def stop(self) -> None:
        if self._persistence_store:
            self._persistence_store.close()
            self._persistence_store = None
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
        is_driver_method = False
        if method is None:
            method = getattr(self, command, None)
            if method is not None:
                is_driver_method = True
        if method is None:
            return StepResult(
                phase_before=phase_before,
                phase_after=phase_before,
                error=f"unknown command: {command}",
            )

        try:
            if is_driver_method:
                result = method(**args)
                if asyncio.iscoroutine(result):
                    await result
                return StepResult(
                    phase_before=phase_before,
                    phase_after=self._phase_before(),
                    emitted_outputs=list(self._output_records),
                )
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

    # E79: Skill Usage Tracking methods
    def get_skill_usage(self, player_id: str) -> dict[str, int]:
        """Get skill usage counts for a player (for test assertions).

        Args:
            player_id: The player's user ID

        Returns:
            Dict mapping skill_name -> usage_count
        """
        if self._session_store is None:
            return {}
        for session in self._session_store._sessions.values():
            return session.skill_tracker.usage.get(player_id, {})
        return {}

    def get_skill_successes(self, player_id: str) -> dict[str, int]:
        """Get skill success counts for a player.

        Args:
            player_id: The player's user ID

        Returns:
            Dict mapping skill_name -> success_count
        """
        if self._session_store is None:
            return {}
        for session in self._session_store._sessions.values():
            return session.skill_tracker.successes.get(player_id, {})
        return {}

    def get_eligible_skills(self, player_id: str) -> list[str]:
        """Get list of skills eligible for improvement.

        Args:
            player_id: The player's user ID

        Returns:
            List of skill names that were used during the session
        """
        if self._session_store is None:
            return []
        for session in self._session_store._sessions.values():
            return session.skill_tracker.get_eligible_skills(player_id)
        return []

    def trigger_improvement_phase(
        self, player_id: str | None = None
    ) -> dict[str, dict[str, int]]:
        """Trigger skill improvement phase for all or specific player.

        COC 7e improvement rules: For each eligible skill, roll 1d100.
        If roll < current skill value, add 1d10 improvement.

        Args:
            player_id: Optional specific player ID. If None, all players.

        Returns:
            Dict mapping player_id -> dict of skill -> improvement_amount
        """
        if self._session_store is None:
            return {}

        import random
        from dm_bot.rules.coc.experience import improve_skill

        results: dict[str, dict[str, int]] = {}

        for session in self._session_store._sessions.values():
            tracker = session.skill_tracker

            # Determine which players to process
            players = [player_id] if player_id else list(tracker.usage.keys())

            for pid in players:
                if pid not in tracker.usage:
                    continue

                results[pid] = {}
                eligible_skills = tracker.get_eligible_skills(pid)

                for skill_name in eligible_skills:
                    # Get current skill value (would need character lookup in real impl)
                    # For now, use placeholder - this would integrate with character system
                    current_skill = 50  # Placeholder

                    # Roll for improvement
                    roll = random.randint(1, 100)
                    if roll < current_skill:
                        improvement = random.randint(1, 10)
                        results[pid][skill_name] = improvement

            # Clear tracker after improvement phase
            tracker.clear()

        return results

    def record_skill_usage(
        self, player_id: str, skill_name: str, success: bool = False
    ) -> None:
        """Record skill usage directly (for testing or manual tracking).

        Args:
            player_id: The player's user ID
            skill_name: Name of the skill used
            success: Whether the skill check was successful
        """
        if self._session_store is None:
            return
        for session in self._session_store._sessions.values():
            session.skill_tracker.record_usage(player_id, skill_name, success)
            break  # Only record to first session

    # E82: Chase methods
    def start_chase(
        self,
        fleeer_ids: list[str],
        pursuer_ids: list[str],
        locations: list[dict],
    ) -> dict:
        """Start a chase encounter.

        Args:
            fleeer_ids: IDs of characters fleeing
            pursuer_ids: IDs of characters pursuing
            locations: List of location definitions

        Returns:
            Chase status dict
        """
        from dm_bot.gameplay.chase import GameplayChaseManager

        self._chase_manager = GameplayChaseManager()
        chase = self._chase_manager.start_chase(
            fleeer_ids=fleeer_ids,
            pursuer_ids=pursuer_ids,
            locations=locations,
        )
        return {
            "started": True,
            "fleeers": fleeer_ids,
            "pursuers": pursuer_ids,
            "locations": len(locations),
            "active": chase.active,
            "round": chase.current_round,
        }

    def resolve_chase_round(self) -> dict:
        """Resolve one round of the active chase.

        Returns:
            Round result dict
        """
        if self._chase_manager is None:
            return {"error": "No active chase"}
        return self._chase_manager.resolve_round()

    def get_chase_status(self) -> dict:
        """Get current chase status.

        Returns:
            Status dict
        """
        if self._chase_manager is None:
            return {"active": False}
        return self._chase_manager.get_chase_status()

    def end_chase(self) -> dict:
        """End the active chase.

        Returns:
            Final result
        """
        if self._chase_manager is None:
            return {"ended": False}
        result = self._chase_manager.end_chase()
        self._chase_manager = None
        return result

    # E83: Archive CRUD methods
    def set_archive_repository(self, archive_repository) -> None:
        """Set the archive repository for CRUD operations.

        Args:
            archive_repository: InvestigatorArchiveRepository instance
        """
        self._archive_repository = archive_repository

    def create_test_profile(
        self,
        user_id: str,
        name: str,
        occupation: str,
        age: int,
        **kwargs,
    ) -> dict:
        """Create a test character profile.

        Args:
            user_id: The user ID
            name: Character name
            occupation: Character occupation
            age: Character age
            **kwargs: Additional profile fields

        Returns:
            Created profile as dict
        """
        repo = getattr(self, "_archive_repository", None)
        if repo is None:
            raise RuntimeError(
                "Archive repository not set. Call set_archive_repository first."
            )

        # Generate stats
        generation = kwargs.get("generation", self._generate_test_stats())

        profile = repo.create_profile(
            user_id=user_id,
            name=name,
            occupation=occupation,
            age=age,
            background=kwargs.get("background", "Test background"),
            portrait_summary=kwargs.get(
                "portrait_summary", f"{occupation} test character"
            ),
            concept=kwargs.get("concept", "Test concept"),
            disposition=kwargs.get("disposition", "冷静"),
            favored_skills=kwargs.get("favored_skills", ["侦查", "图书馆使用"]),
            generation=generation,
        )

        return profile.model_dump()

    def get_profile(self, user_id: str, profile_id: str) -> dict | None:
        """Get a profile.

        Args:
            user_id: The user ID
            profile_id: The profile ID

        Returns:
            Profile as dict, or None if not found
        """
        repo = getattr(self, "_archive_repository", None)
        if repo is None:
            return None

        try:
            profile = repo.get_profile(user_id, profile_id)
            return profile.model_dump()
        except KeyError:
            return None

    def update_profile(
        self,
        user_id: str,
        profile_id: str,
        **updates,
    ) -> dict:
        """Update a profile.

        Args:
            user_id: The user ID
            profile_id: The profile ID
            **updates: Fields to update

        Returns:
            Updated profile as dict
        """
        repo = getattr(self, "_archive_repository", None)
        if repo is None:
            raise RuntimeError(
                "Archive repository not set. Call set_archive_repository first."
            )

        profile = repo.update_profile(user_id=user_id, profile_id=profile_id, **updates)
        return profile.model_dump()

    def list_profiles(self, user_id: str) -> list[dict]:
        """List all profiles for a user.

        Args:
            user_id: The user ID

        Returns:
            List of profile dicts
        """
        repo = getattr(self, "_archive_repository", None)
        if repo is None:
            return []

        profiles = repo.list_profiles(user_id)
        return [p.model_dump() for p in profiles]

    def delete_profile(self, user_id: str, profile_id: str) -> bool:
        """Delete a profile.

        Args:
            user_id: The user ID
            profile_id: The profile ID

        Returns:
            True if deleted, False if not found
        """
        repo = getattr(self, "_archive_repository", None)
        if repo is None:
            return False

        try:
            repo.delete_profile(user_id=user_id, profile_id=profile_id)
            return True
        except KeyError:
            return False

    def _generate_test_stats(self) -> dict[str, int]:
        """Generate test character stats."""
        return {
            "str": 50,
            "con": 50,
            "dex": 50,
            "app": 50,
            "pow": 50,
            "siz": 50,
            "int": 50,
            "edu": 50,
            "luck": 50,
        }

    # E84: Character Builder methods
    async def start_character_build(self, user_id: str) -> dict:
        """Start character building interview.

        Args:
            user_id: The user starting the build

        Returns:
            Dict with question and session info
        """
        if not self._gameplay:
            raise RuntimeError("Gameplay not initialized")

        builder = self._gameplay.get_builder()
        if not builder:
            raise RuntimeError("Character builder not available")

        question = builder.start(user_id=user_id)

        return {
            "started": True,
            "question": question,
            "user_id": user_id,
            "has_session": builder.has_session(user_id),
        }

    async def answer_builder_question(
        self,
        user_id: str,
        answer: str,
    ) -> dict:
        """Answer a builder question.

        Args:
            user_id: The user answering
            answer: The answer text

        Returns:
            Dict with next question or completed profile
        """
        if not self._gameplay:
            raise RuntimeError("Gameplay not initialized")

        builder = self._gameplay.get_builder()
        if not builder:
            raise RuntimeError("Character builder not available")

        if not builder.has_session(user_id):
            raise RuntimeError(f"No builder session for user {user_id}")

        next_question, profile = await builder.answer(
            user_id=user_id,
            answer=answer,
        )

        result = {
            "answered": True,
            "question": next_question,
            "has_profile": profile is not None,
        }

        if profile:
            result["profile"] = profile.model_dump()
            result["profile_id"] = profile.profile_id

        return result

    def get_builder_session(self, user_id: str) -> dict:
        """Get current builder session state.

        Args:
            user_id: The user to check

        Returns:
            Session state dict
        """
        if not self._gameplay:
            return {"error": "Gameplay not initialized"}

        builder = self._gameplay.get_builder()
        if not builder:
            return {"error": "Character builder not available"}

        return {
            "has_session": builder.has_session(user_id),
            "user_id": user_id,
        }

    def cancel_builder_session(self, user_id: str) -> dict:
        """Cancel a builder session.

        Args:
            user_id: The user to cancel for

        Returns:
            Result dict
        """
        if not self._gameplay:
            return {"error": "Gameplay not initialized"}

        builder = self._gameplay.get_builder()
        if not builder:
            return {"error": "Character builder not available"}

        # Remove session if exists
        if builder.has_session(user_id):
            del builder._sessions[user_id]
            return {"cancelled": True}

        return {"cancelled": False, "reason": "No active session"}


def _build_commands(
    session_store: SessionStore,
    turn_coordinator: TurnCoordinator,
    gameplay: GameplayOrchestrator,
    persistence_store: PersistenceStore,
    model_client: StubModelClient,
) -> Any:
    coc_assets: Any = None
    archive_repository = getattr(gameplay, "_archive_repository", None)
    character_builder = getattr(gameplay, "character_builder", None)
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
