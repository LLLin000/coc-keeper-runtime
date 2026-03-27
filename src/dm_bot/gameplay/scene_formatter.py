from dm_bot.router.contracts import TurnPlan


def format_scene_output(*, plan: TurnPlan, raw_output: str) -> str:
    if plan.mode != "scene":
        return raw_output.strip()

    rendered = raw_output
    for speaker in plan.speaker_hints:
        rendered = rendered.replace(f"{speaker}：", f"[{speaker}] ")
        rendered = rendered.replace(f"{speaker}:", f"[{speaker}] ")
    return rendered.strip()
