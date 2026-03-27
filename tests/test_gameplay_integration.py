import asyncio

from dm_bot.adventures.loader import load_adventure
from dm_bot.adventures.models import AdventurePackage
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.gameplay.combat import CombatEncounter, Combatant
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.turn_runner import TurnRunner
from dm_bot.router.contracts import TurnPlan
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine


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


class StubRouter:
    def __init__(self, plan: dict[str, object]) -> None:
        self._plan = plan

    async def route(self, envelope):
        return TurnPlan.model_validate(self._plan)


class StubNarrator:
    async def narrate(self, request):
        if request.plan.mode == "scene":
            return "守卫：站住。酒馆老板：别在我店里打架。"
        return "战斗开始。"


def build_gameplay() -> GameplayOrchestrator:
    return GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )


def test_scene_turn_is_formatted_with_speaker_labels() -> None:
    gameplay = build_gameplay()
    runner = TurnRunner(
        router=StubRouter(
            {
                "mode": "scene",
                "tool_calls": [],
                "state_intents": [],
                "narration_brief": "多角色场景。",
                "speaker_hints": ["守卫", "酒馆老板"],
            }
        ),
        narrator=StubNarrator(),
        gameplay=gameplay,
    )
    from dm_bot.models.schemas import TurnEnvelope

    result = asyncio.run(
        runner.run_turn(
            TurnEnvelope(
                campaign_id="camp-1",
                channel_id="chan-1",
                user_id="user-1",
                trace_id="trace-1",
                content="我走进酒馆。",
            )
        )
    )

    assert "[守卫]" in result.reply
    assert "[酒馆老板]" in result.reply


def test_commands_can_switch_scene_mode_and_start_combat() -> None:
    gameplay = build_gameplay()
    commands = BotCommands(settings=None, session_store=None, turn_coordinator=None, gameplay=gameplay)
    interaction = FakeInteraction()

    asyncio.run(commands.enter_scene(interaction, speakers="守卫,酒馆老板"))
    assert gameplay.mode_state.mode == "scene"

    asyncio.run(commands.start_combat(interaction, combatants="Hero:15:20:15,Goblin:12:7:13"))
    assert gameplay.combat is not None
    assert gameplay.combat.active_combatant.name == "Hero"


def test_gameplay_loads_formal_adventure_and_exports_public_and_gm_state() -> None:
    gameplay = build_gameplay()
    adventure = AdventurePackage.model_validate(
        {
            "slug": "mansion_test",
            "title": "疯狂之馆",
            "premise": "测试模组。",
            "start_scene_id": "hall",
            "state_fields": [
                {"key": "time_remaining", "default": 180, "visibility": "public"},
                {"key": "saint_candidate", "default": "", "visibility": "secret"},
                {"key": "administrator_truth", "default": "奈亚化身", "visibility": "gm_only"},
            ],
            "scenes": [
                {
                    "id": "hall",
                    "title": "中央大厅",
                    "summary": "大厅里悬着钟。",
                    "clues": ["四道光幕通往四个分馆"],
                    "reveals": ["钟面上的时间正在流逝"],
                }
            ],
            "endings": [{"id": "death", "title": "死亡", "summary": "团灭。"}],
        }
    )

    gameplay.load_adventure(adventure)

    assert gameplay.adventure_state["scene_id"] == "hall"
    assert gameplay.adventure_state["module_state"]["time_remaining"] == 180

    snapshot = gameplay.adventure_snapshot()
    assert snapshot["public"]["current_scene"]["id"] == "hall"
    assert snapshot["public"]["state"]["time_remaining"] == 180
    assert "administrator_truth" not in snapshot["public"]["state"]
    assert snapshot["gm"]["state"]["administrator_truth"] == "奈亚化身"


def test_gameplay_can_progress_mad_mansion_module_state() -> None:
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("mad_mansion"))

    gameplay.set_adventure_scene("blood_hall")
    gameplay.record_adventure_clue("blood_exit_rule")
    gameplay.update_adventure_state(time_remaining=120, blood_required=25, blood_collected=11)
    gameplay.set_adventure_ending("survive")

    snapshot = gameplay.adventure_snapshot()
    assert snapshot["public"]["current_scene"]["id"] == "blood_hall"
    assert "blood_exit_rule" in gameplay.adventure_state["clues_found"]
    assert snapshot["public"]["state"]["time_remaining"] == 120
    assert snapshot["gm"]["state"]["blood_collected"] == 11
    assert gameplay.adventure_state["ending_id"] == "survive"


def test_gameplay_evaluates_scene_actions_with_guidance_and_roll_prompts() -> None:
    gameplay = build_gameplay()
    gameplay.load_adventure(
        AdventurePackage.model_validate(
            {
                "slug": "guided_module",
                "title": "Guided Module",
                "premise": "测试模组。",
                "start_scene_id": "hall",
                "scenes": [
                    {
                        "id": "hall",
                        "title": "中央大厅",
                        "summary": "白色大厅中央有一座石钟和四道门。",
                        "guidance": {
                            "ambient_focus": ["石钟", "四道门"],
                            "light_hint": "你们可以先观察石钟或靠近任一道门。",
                            "rescue_hint": "最稳妥的推进方向是先调查石钟，再决定进哪道门。"
                        },
                        "interactables": [
                            {
                                "id": "clock",
                                "title": "石钟",
                                "keywords": ["钟", "clock"],
                                "judgement": "auto",
                                "result_text": "钟针在倒退。",
                                "discover_clue": "clock_countdown"
                            },
                            {
                                "id": "bookshelf",
                                "title": "书架",
                                "keywords": ["书架", "翻书"],
                                "judgement": "roll",
                                "roll_type": "ability_check",
                                "roll_label": "LibraryUse",
                                "prompt_text": "这里需要一次图书馆检定，看看你能不能从散乱的手记里拼出有用信息。"
                            }
                        ]
                    }
                ]
            }
        )
    )

    auto = gameplay.evaluate_scene_action("我先检查一下大厅里的钟。")
    roll = gameplay.evaluate_scene_action("我去翻书架。")
    miss1 = gameplay.evaluate_scene_action("我站着发呆。")
    miss2 = gameplay.evaluate_scene_action("我继续发呆。")

    assert auto["kind"] == "auto"
    assert "倒退" in str(auto["message"])
    assert "clock_countdown" in gameplay.adventure_state["clues_found"]
    assert roll["kind"] == "roll_needed"
    assert roll["roll"]["action"] == "ability_check"
    assert "图书馆检定" in str(roll["message"])
    assert miss1["kind"] == "hint"
    assert "观察石钟" in str(miss1["message"])
    assert miss2["kind"] == "hint"
    assert "最稳妥的推进方向" in str(miss2["message"])


def test_gameplay_tracks_locations_and_distinguishes_observe_vs_enter() -> None:
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("mad_mansion"))

    snapshot = gameplay.adventure_snapshot()
    assert snapshot["public"]["current_location"]["id"] == "central_hall"
    assert "greed_hall" in {item["to_location_id"] for item in snapshot["public"]["reachable_locations"]}

    observe = gameplay.evaluate_scene_action("我打量一下贪欲之馆的光幕，不进去。")
    assert gameplay.adventure_state["location_id"] == "central_hall"
    enter = gameplay.evaluate_scene_action("我走进贪欲之馆。")

    assert observe["kind"] == "auto"
    assert "没有立刻踏进去" in str(observe["message"])
    assert gameplay.adventure_state["location_id"] == "greed_hall"
    assert enter["kind"] == "auto"
    assert "贪欲之馆" in str(enter["message"])


def test_manual_roll_applies_trigger_consequences() -> None:
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("mad_mansion"))
    gameplay.set_adventure_location("life_hall")

    prompt = gameplay.evaluate_scene_action("我去翻书架和旧笔记。")
    assert prompt["kind"] == "roll_needed"
    assert gameplay.adventure_state["pending_roll"]["id"] == "life_library_research"

    result = gameplay.resolve_manual_roll(
        actor_name="调查员A",
        action="ability_check",
        label="LibraryUse",
        modifier=20,
        advantage="none",
    )

    assert "consequence_summary" in result
    assert "管理员并非不可触及" in str(result["consequence_summary"])
    assert "life_library_notes" in gameplay.adventure_state["clues_found"]
    assert "pending_roll" not in gameplay.adventure_state
