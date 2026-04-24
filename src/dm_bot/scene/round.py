from dm_bot.scene.action import Action, ActionResult
from dm_bot.scene.state import SceneState


class Round:
    """管理单个回合的收集与结算"""

    def __init__(self) -> None:
        self.actions: list[Action] = []
        self.state = SceneState.WAITING

    def submit_action(self, action: Action) -> None:
        """提交玩家行动"""
        if self.state != SceneState.COLLECTING:
            raise RuntimeError(f"Cannot submit action in state {self.state}")
        self.actions.append(action)

    def start_collection(self) -> None:
        """开始收集行动"""
        self.actions = []
        self.state = SceneState.COLLECTING

    def all_players_acted(self, expected_count: int) -> bool:
        """检查是否所有玩家都已行动"""
        return len(self.actions) >= expected_count

    def resolve(self) -> list[Action]:
        """结算回合：排序并计算结果"""
        if self.state not in (SceneState.COLLECTING, SceneState.RESOLVING):
            raise RuntimeError(f"Cannot resolve in state {self.state}")

        self.state = SceneState.RESOLVING

        # 1. DEX 降序排序，DEX 相同则 user_id 升序
        ordered = sorted(
            self.actions,
            key=lambda a: (-a.dex_value, a.user_id),
        )

        # 2. 逐个处理（占位，实际结算由外部注入 rules/checks）
        for action in ordered:
            if action.result is None:
                action.result = ActionResult(success=True)

        self.state = SceneState.NARRATING
        return ordered

    def get_private_results(self) -> dict[str, str]:
        """获取需要私密发送的结果"""
        results: dict[str, str] = {}
        for action in self.actions:
            if action.visibility == "private" and action.result:
                results[action.user_id] = action.result.extra_info or "行动已执行"
        return results
