"""Onboarding content system for pre-play briefing.

Provides default COC 7E quick-start content and adventure package override mechanism.
"""

from typing import Any


class OnboardingSection:
    def __init__(
        self,
        section_id: str,
        title: str,
        content: str,
        button_label: str = "继续",
    ):
        self.section_id = section_id
        self.title = title
        self.content = content
        self.button_label = button_label


class OnboardingContent:
    def __init__(
        self,
        welcome: str,
        sections: list[OnboardingSection],
        confirm_text: str = "我已了解规则，可以开始游戏",
        skip_available: bool = False,
    ):
        self.welcome = welcome
        self.sections = sections
        self.confirm_text = confirm_text
        self.skip_available = skip_available

    def to_dict(self) -> dict[str, Any]:
        return {
            "welcome": self.welcome,
            "sections": [
                {
                    "section_id": s.section_id,
                    "title": s.title,
                    "content": s.content,
                    "button_label": s.button_label,
                }
                for s in self.sections
            ],
            "confirm_text": self.confirm_text,
            "skip_available": self.skip_available,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OnboardingContent":
        sections = [
            OnboardingSection(
                section_id=s["section_id"],
                title=s["title"],
                content=s["content"],
                button_label=s.get("button_label", "继续"),
            )
            for s in data.get("sections", [])
        ]
        return cls(
            welcome=data.get("welcome", ""),
            sections=sections,
            confirm_text=data.get("confirm_text", "我已了解规则，可以开始游戏"),
            skip_available=data.get("skip_available", False),
        )


def get_default_coc7e_onboarding() -> OnboardingContent:
    welcome = """**欢迎进入《克苏鲁的呼唤》第七版！**

在你开始探索克苏鲁神话的黑暗角落之前，让我们快速回顾一下这个游戏的核心机制。这些规则将在整个模组中反复出现，提前熟悉会让你的游戏体验更加流畅。

点击下方按钮逐步了解各项规则。"""

    sections = [
        OnboardingSection(
            section_id="d100",
            title="百分骰系统 (D100)",
            content="""**核心机制：百分骰**

游戏使用两颗十面骰（或者一颗百面骰）来判定结果。

🎲 **如何掷骰**：
- 随机生成一个 1-100 的数字
- 与你的技能值进行比较

📊 **成功等级**（目标值 ≤ 技能值时）：
- **大成功 (CRITICAL)**：01-05 （仅限技能值≥50）
- **成功 (SUCCESS)**：≤ 技能值，且不是大成功
- **失败 (FAILURE)**：> 技能值
- **大失败 (FUMBLE)**：96-100 （仅限技能值<50）

💡 **要点**：技能值越高，成功概率越大。""",
            button_label="了解 D100",
        ),
        OnboardingSection(
            section_id="pushing",
            title="强行推动 (Pushing)",
            content="""**关键时刻：强行推动**

当你失败时，有时候可以尝试"强行推动"——再试一次，但承受后果的风险。

🔄 **强行推动规则**：
- 只能在你已经失败的行为上使用
- 强制重新掷骰
- **成功**：行为正常成功
- **失败**：后果比普通失败更严重

⚠️ **风险提示**：
- 战斗中使用可能导致更严重的伤害
- 社交场合可能让情况更糟
- 调查中使用可能触发更多危险

💡 **建议**：不到万不得已，不要轻易推动。""",
            button_label="了解 Pushing",
        ),
        OnboardingSection(
            section_id="san",
            title="理智 (SAN)",
            content="""**调查员的脆弱：理智值**

SAN（Sanity）代表你角色的心理健康程度。

🧠 **SAN 值**：
- 起始值通常为 50（可上下浮动）
- 遭遇克苏鲁神话生物或恐怖事件会减少
- 降至 0 时角色可能永久性崩溃

💀 **失去 SAN 的后果**：
- 每次损失都会带来临时或长期的症状
- 长期症状会累积
- 可能导致恐惧、偏执、幻觉等

🛡️ **恢复 SAN**：
- 通过游戏中的特殊情节恢复
- 电影娱乐、朋友支持等（由 KP 判定）

💡 **提示**：不要让你的 SAN 降到 30 以下！""",
            button_label="了解 SAN",
        ),
        OnboardingSection(
            section_id="luck",
            title="幸运 (Luck)",
            content="""**命运的转折：幸运值**

Luck 是你可以消耗的特殊资源，能在关键时刻改变命运。

⭐ **幸运的使用**：
- 消耗 1 点幸运值，可以将一次掷骰改为恰好成功
- 可以在任何时候使用，包括他人的掷骰
- 起始幸运值通常为 50

🎯 **典型使用场景**：
- 最后一秒躲过致命攻击
- 恰好找到关键线索
- 在最危险的时刻获救

⚡ **注意**：
- 幸运值有限，用完就没了
- 这是你最后的防线，慎重使用！

💡 **策略**：留到最关键的时刻再用。""",
            button_label="了解 Luck",
        ),
    ]

    return OnboardingContent(
        welcome=welcome,
        sections=sections,
        confirm_text="我已了解规则，可以开始游戏",
        skip_available=True,
    )


def merge_with_adventure_onboarding(
    default_content: OnboardingContent,
    adventure_content: dict[str, Any] | None,
) -> OnboardingContent:
    """Merge default COC content with adventure-specific custom onboarding."""
    if not adventure_content:
        return default_content

    override_sections = adventure_content.get("sections", [])
    if not override_sections:
        return default_content

    adventure_sections = [
        OnboardingSection(
            section_id=s.get("section_id", f"custom_{i}"),
            title=s.get("title", "自定义章节"),
            content=s.get("content", ""),
            button_label=s.get("button_label", "继续"),
        )
        for i, s in enumerate(override_sections)
    ]

    return OnboardingContent(
        welcome=adventure_content.get("welcome", default_content.welcome),
        sections=adventure_sections,
        confirm_text=adventure_content.get(
            "confirm_text", default_content.confirm_text
        ),
        skip_available=adventure_content.get(
            "skip_available", default_content.skip_available
        ),
    )
