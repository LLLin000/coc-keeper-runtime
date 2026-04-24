from dm_bot.gameplay.modes import GameModeState
from dm_bot.gameplay.scene_formatter import format_scene_output
from dm_bot.router.contracts import TurnPlan


def test_mode_state_can_switch_between_dm_scene_and_back() -> None:
    state = GameModeState()

    assert state.mode == "dm"
    state.enter_scene(speakers=["守卫", "酒馆老板"])
    assert state.mode == "scene"
    assert state.scene_speakers == ["守卫", "酒馆老板"]
    state.enter_dm()
    assert state.mode == "dm"
    assert state.scene_speakers == []


def test_scene_formatter_adds_explicit_speaker_labels() -> None:
    plan = TurnPlan.model_validate(
        {
            "mode": "scene",
            "tool_calls": [],
            "state_intents": [],
            "narration_brief": "让两个角色分别说话。",
            "speaker_hints": ["守卫", "酒馆老板"],
        }
    )

    rendered = format_scene_output(
        plan=plan,
        raw_output="守卫：站住。酒馆老板：别在我店里打架。",
    )

    assert "[守卫]" in rendered
    assert "[酒馆老板]" in rendered


def test_dm_mode_keeps_plain_narration() -> None:
    plan = TurnPlan.model_validate(
        {
            "mode": "dm",
            "tool_calls": [],
            "state_intents": [],
            "narration_brief": "正常叙述。",
            "speaker_hints": [],
        }
    )

    rendered = format_scene_output(plan=plan, raw_output="你看到门后有微弱的烛光。")

    assert rendered == "你看到门后有微弱的烛光。"
