"""Tests for surface board views."""

from dm_bot.surface.board import Board
from dm_bot.surface.session_board import SessionBoard


class TestSessionBoard:
    def test_render_session_identity(self):
        state = {
            "session_id": "ses_abc123",
            "phase": "exploration",
            "participants": ["Alice", "Bob"],
            "module_name": "The Haunting",
        }
        board = SessionBoard()
        output = board.render(state)
        assert "The Haunting" in output
        assert "ses_abc123" in output
        assert "exploration" in output
        assert "Alice" in output
        assert "Bob" in output

    def test_board_abc_cannot_instantiate(self):
        import pytest
        with pytest.raises(TypeError):
            Board()


class TestSceneBoard:
    def test_render_scene_context(self):
        from dm_bot.surface.scene_board import SceneBoard

        state = {
            "scene_id": "s1",
            "scene_name": "Creaky Hallway",
            "scene_desc": "A dark corridor.",
            "round_state": "COLLECTING",
            "action_count": 2,
            "waiting_for": ["KP decision on lockpick"],
        }
        board = SceneBoard()
        output = board.render(state)
        assert "Creaky Hallway" in output
        assert "COLLECTING" in output
        assert "KP decision on lockpick" in output
        assert "2" in output

    def test_render_no_waiting_reason(self):
        from dm_bot.surface.scene_board import SceneBoard

        state = {
            "scene_id": "s2",
            "scene_name": "Empty Room",
            "round_state": "WAITING",
            "action_count": 0,
        }
        board = SceneBoard()
        output = board.render(state)
        assert "Empty Room" in output
        assert "WAITING" in output


class TestBlockerBoard:
    def test_render_blocker_summary(self):
        from dm_bot.surface.blocker_board import BlockerBoard

        state = {
            "blockers": [
                {"blocker_id": "blk_1", "reason": "KP decides lockpick DC", "scene_id": "s1"},
                {"blocker_id": "blk_2", "reason": "Awaiting player response", "scene_id": "s2"},
            ]
        }
        board = BlockerBoard()
        output = board.render(state)
        assert "KP decides lockpick DC" in output
        assert "Awaiting player response" in output
        assert "2" in output

    def test_render_no_blockers(self):
        from dm_bot.surface.blocker_board import BlockerBoard

        board = BlockerBoard()
        output = board.render({"blockers": []})
        assert "No unresolved blockers" in output


class TestConsequenceBoard:
    def test_render_table_visible_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        state = {
            "events": [
                {"event_type": "action.submitted", "visibility": "table_visible", "summary": "Alice searched the room"},
                {"event_type": "action.submitted", "visibility": "kp_only", "summary": "Bob found a hidden key"},
            ]
        }
        board = ConsequenceBoard()
        output = board.render(state, visibility="table_visible")
        assert "Alice searched the room" in output
        assert "Bob found a hidden key" not in output

    def test_render_kp_only_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        state = {
            "events": [
                {"event_type": "clue.revealed", "visibility": "kp_only", "summary": "DC15 Spot Hidden"},
                {"event_type": "clue.revealed", "visibility": "table_visible", "summary": "A clue was found"},
            ]
        }
        board = ConsequenceBoard()
        output = board.render(state, visibility="kp_only")
        assert "DC15 Spot Hidden" in output
        assert "A clue was found" not in output

    def test_render_all_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        board = ConsequenceBoard()
        output = board.render({"events": []})
        assert "No events" in output


class TestSessionContext:
    def test_session_context_holds_state(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        assert ctx.session_id == "ses_1"
        assert ctx.phase == "idle"

    def test_session_context_participants(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        ctx.add_participant("Alice")
        ctx.add_participant("Bob")
        assert "Alice" in ctx.participants
        assert len(ctx.participants) == 2

    def test_session_board_from_context(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.session_board import SessionBoard

        ctx = SessionContext(session_id="ses_abc", module_name="Haunting")
        ctx.add_participant("Alice")
        ctx.phase = "exploration"

        board = SessionBoard()
        output = board.render(ctx.to_dict())
        assert "ses_abc" in output
        assert "Haunting" in output
        assert "Alice" in output
        assert "exploration" in output


class TestBoardIntegration:
    def test_all_boards_render_session_state(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.session_board import SessionBoard
        from dm_bot.surface.consequence_board import ConsequenceBoard
        from dm_bot.publish.models import ActionSubmittedEvent

        ctx = SessionContext(session_id="ses_test", module_name="TestModule")
        ctx.add_participant("Alice")
        ctx.phase = "active"

        pub = ctx.publisher
        pub.publish(ActionSubmittedEvent(
            session_id="ses_test", scene_id="s1",
            user_id="Alice", action_text="Alice searched the room"
        ))

        session_out = SessionBoard().render(ctx.to_dict())
        assert "TestModule" in session_out
        assert "Alice" in session_out

        events = [
            {"event_type": e.event_type, "visibility": e.visibility.value, "summary": getattr(e, 'action_text', '')}
            for e in pub.get_events()
        ]
        conseq_out = ConsequenceBoard().render({"events": events})
        assert "Alice searched the room" in conseq_out


class TestViewPayload:
    def test_create_payload(self):
        from dm_bot.surface.view_payload import ViewPayload, ViewSection

        section = ViewSection(heading="Findings", body="The team discovered...")
        payload = ViewPayload(title="Clue Report", sections=[section])
        assert payload.title == "Clue Report"
        assert payload.sections[0].heading == "Findings"

    def test_payload_with_fields(self):
        from dm_bot.surface.view_payload import ViewPayload, FieldEntry

        payload = ViewPayload(
            title="Scene Status",
            fields=[FieldEntry(name="Round", value="3"), FieldEntry(name="Actions", value="2", inline=True)],
        )
        assert len(payload.fields) == 2
        assert payload.fields[1].inline is True


class TestDiscordFormatter:
    def test_format_title_and_fields(self):
        from dm_bot.surface.discord_formatter import DiscordFormatter
        from dm_bot.surface.view_payload import ViewPayload, FieldEntry

        payload = ViewPayload(
            title="Session: The Haunting",
            fields=[FieldEntry(name="Phase", value="exploration"), FieldEntry(name="Players", value="Alice, Bob")],
        )
        result = DiscordFormatter.format(payload)
        assert "Session: The Haunting" in result
        assert "Phase" in result
        assert "exploration" in result
        assert "Alice, Bob" in result

    def test_format_sections(self):
        from dm_bot.surface.discord_formatter import DiscordFormatter
        from dm_bot.surface.view_payload import ViewPayload, ViewSection

        payload = ViewPayload(
            title="Clue Report",
            sections=[ViewSection(heading="Bloody Footprint", body="A trail leads east.")],
        )
        result = DiscordFormatter.format(payload)
        assert "Bloody Footprint" in result
        assert "A trail leads east." in result

    def test_format_empty_payload(self):
        from dm_bot.surface.discord_formatter import DiscordFormatter
        from dm_bot.surface.view_payload import ViewPayload

        result = DiscordFormatter.format(ViewPayload(title="Empty"))
        assert "Empty" in result


class TestClueBoard:
    def test_render_visible_clues(self):
        from dm_bot.surface.clue_board import ClueBoard

        state = {
            "clues": [
                {"clue_id": "c1", "title": "Bloody Knife", "description": "Found under the bed."},
                {"clue_id": "c2", "title": "Strange Symbol", "description": "Carved into the wall."},
            ],
            "visible_clue_ids": ["c1"],
            "player_id": "Alice",
        }
        board = ClueBoard()
        output = board.render(state)
        assert "Bloody Knife" in output
        assert "Strange Symbol" not in output

    def test_render_no_clues(self):
        from dm_bot.surface.clue_board import ClueBoard

        board = ClueBoard()
        output = board.render({"clues": [], "visible_clue_ids": [], "player_id": "Alice"})
        assert "No visible clues" in output

    def test_render_known_clues(self):
        from dm_bot.surface.clue_board import ClueBoard

        state = {
            "clues": [
                {"clue_id": "c1", "title": "Letter", "description": "A torn letter."},
                {"clue_id": "c2", "title": "Key", "description": "An iron key."},
            ],
            "visible_clue_ids": ["c1", "c2"],
            "known_clue_ids": ["c1"],
            "player_id": "Alice",
        }
        board = ClueBoard()
        output = board.render(state)
        assert "[Known]" in output or "Known" in output


class TestClueBoardIntegration:
    def test_clue_board_from_reveal_checker(self):
        from dm_bot.surface.clue_board import ClueBoard
        from dm_bot.reveal.models import RevealGate, KnowledgeState
        from dm_bot.reveal.checker import RevealChecker

        checker = RevealChecker()
        gate_open = RevealGate(clue_id="c1", gate_type="manual")
        gate_open.open(opened_by="KP")
        gate_closed = RevealGate(clue_id="c2", gate_type="manual")
        alice_knowledge = KnowledgeState(player_id="Alice")

        clues_data = [
            {"clue_id": "c1", "title": "Open Clue", "description": "Visible to all."},
            {"clue_id": "c2", "title": "Hidden Clue", "description": "Not visible."},
        ]
        gates = [gate_open, gate_closed]

        visible_ids = [
            c["clue_id"] for c in clues_data
            if checker.is_clue_visible(c["clue_id"], "Alice", gates, alice_knowledge)
        ]

        state = {
            "clues": clues_data,
            "visible_clue_ids": visible_ids,
            "known_clue_ids": alice_knowledge.known_clue_ids,
            "player_id": "Alice",
        }
        board = ClueBoard()
        output = board.render(state)
        assert "Open Clue" in output
        assert "Hidden Clue" not in output

    def test_clue_board_in_session_context(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.clue_board import ClueBoard
        from dm_bot.reveal.models import RevealGate, KnowledgeState
        from dm_bot.reveal.checker import RevealChecker

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        checker = RevealChecker()
        gate_open = RevealGate(clue_id="c1", gate_type="manual")
        gate_open.open(opened_by="KP")
        gate_closed = RevealGate(clue_id="c2", gate_type="manual")

        clues_data = [
            {"clue_id": "c1", "title": "Open Clue", "description": "Visible."},
            {"clue_id": "c2", "title": "Hidden Clue", "description": "Hidden."},
        ]
        gates_list = [gate_open, gate_closed]
        player_knowledge = KnowledgeState(player_id="Alice")

        visible_ids = [
            c["clue_id"] for c in clues_data
            if checker.is_clue_visible(c["clue_id"], "Alice", gates_list, player_knowledge)
        ]

        state = ctx.to_dict()
        state.update({
            "clues": clues_data,
            "visible_clue_ids": visible_ids,
            "known_clue_ids": player_knowledge.known_clue_ids,
            "player_id": "Alice",
        })
        board = ClueBoard()
        output = board.render(state)
        assert "Open Clue" in output
        assert "Hidden Clue" not in output

class TestCharacterBoard:
    def test_render_sheet(self):
        from dm_bot.surface.character_board import CharacterCardBoard

        state = {
            "name": "Alice",
            "age": 30,
            "occupation": "Detective",
            "strength": 60, "constitution": 50, "size": 50,
            "dexterity": 50, "appearance": 50, "intelligence": 70,
            "power": 60, "education": 65, "luck": 40,
            "hit_points": 10, "magic_points": 12, "sanity": 60, "sanity_max": 99,
            "skills": {"Spot Hidden": 60, "Library Use": 50},
        }
        board = CharacterCardBoard()
        output = board.render(state)
        assert "Alice" in output
        assert "Detective" in output
        assert "60" in output  # strength value
        assert "Spot Hidden" in output

    def test_render_minimal_sheet(self):
        from dm_bot.surface.character_board import CharacterCardBoard

        board = CharacterCardBoard()
        output = board.render({"name": "Bob", "occupation": "Writer"})
        assert "Bob" in output