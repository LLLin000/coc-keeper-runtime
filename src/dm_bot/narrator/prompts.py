"""AI 叙事提示词模板"""


def scene_opening(scene_name: str, scene_desc: str, characters: list[str]) -> str:
    return (
        f"你是一个 horror investigation TRPG 的守秘人（Keeper）。\n"
        f"当前场景：{scene_name}\n"
        f"场景描述：{scene_desc}\n"
        f"在场调查员：{', '.join(characters)}\n"
        f"请用中文描述这个场景的开场，营造氛围，并引导调查员们开始行动。"
    )


def action_ack(action_text: str, character_name: str) -> str:
    return (
        f"你是守秘人。调查员 {character_name} 正在执行行动：{action_text}\n"
        f"请用中文给出简短的即时反馈（1-2句话），确认行动并开始描述，但不要透露结果。"
    )


def scene_resolution(scene_name: str, actions_summary: str) -> str:
    return (
        f"你是守秘人。当前场景：{scene_name}\n"
        f"本轮所有调查员的行动及结果如下：\n{actions_summary}\n"
        f"请用中文写一个统一的场景叙事，描述所有行动的结果和场景的变化。"
    )
