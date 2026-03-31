"""Consequence aggregator for group action resolution.

Three-pass aggregation:
1. Collect all consequences from action results
2. Group by visibility level
3. Sort by priority
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AggregatedConsequence:
    """A single aggregated consequence."""

    character_id: str
    visibility: str  # public, private, group, keeper
    content: str
    priority: int = 0
    source_action: str = ""


@dataclass
class VisibilityGroup:
    """Consequences grouped by visibility."""

    visibility: str
    consequences: list[AggregatedConsequence] = field(default_factory=list)


@dataclass
class AggregatedConsequences:
    """Result of consequence aggregation."""

    groups: dict[str, VisibilityGroup] = field(default_factory=dict)


class ConsequenceAggregator:
    """Aggregates consequences from batch resolution into visibility-grouped output.

    Three-pass aggregation:
    1. Collect: Gather all consequences from action results
    2. Group: Organize by visibility (public/private/group/keeper)
    3. Sort: Order by priority within each group
    """

    def aggregate(
        self,
        batch_result,
        llm_summary_enabled: bool = False,
    ) -> AggregatedConsequences:
        """Aggregate consequences from batch resolution result.

        Args:
            batch_result: BatchResolutionResult from RulesEngine.execute_batch()
            llm_summary_enabled: Whether to use LLM for summarizing groups

        Returns:
            AggregatedConsequences with visibility-grouped consequences
        """
        # Pass 1: Collect all consequences
        all_consequences = self._collect_all(batch_result.action_results)

        # Pass 2: Group by visibility
        by_visibility = self._group_by_visibility(all_consequences)

        # Pass 3: Sort by priority within each group
        sorted_groups = self._sort_by_priority(by_visibility)

        # Optional LLM summarization
        if llm_summary_enabled:
            sorted_groups = self._llm_summarize_groups(sorted_groups)

        return AggregatedConsequences(groups=sorted_groups)

    def _collect_all(self, action_results: list) -> list[AggregatedConsequence]:
        """Collect all consequences from action results."""
        consequences = []
        for result in action_results:
            # Extract consequences from rule outcomes
            for outcome in getattr(result, "rule_outcomes", []):
                consequence = AggregatedConsequence(
                    character_id=result.character_id,
                    visibility=getattr(result, "visibility", "public"),
                    content=self._format_outcome(outcome),
                    priority=self._determine_priority(outcome),
                    source_action=result.action_text,
                )
                consequences.append(consequence)

            # Extract from trigger effects if present
            for effect in getattr(result, "trigger_effects", []):
                consequence = AggregatedConsequence(
                    character_id=result.character_id,
                    visibility=getattr(result, "visibility", "public"),
                    content=self._format_trigger_effect(effect),
                    priority=10,  # Triggers are high priority
                    source_action=result.action_text,
                )
                consequences.append(consequence)

            # Also add the action text itself as a consequence
            if hasattr(result, "action_text") and result.action_text:
                consequence = AggregatedConsequence(
                    character_id=result.character_id,
                    visibility=getattr(result, "visibility", "public"),
                    content=f"{result.character_id}: {result.action_text}",
                    priority=5,
                    source_action=result.action_text,
                )
                consequences.append(consequence)

        return consequences

    def _group_by_visibility(
        self, consequences: list[AggregatedConsequence]
    ) -> dict[str, VisibilityGroup]:
        """Group consequences by visibility level."""
        groups: dict[str, VisibilityGroup] = {}
        for consequence in consequences:
            vis = consequence.visibility
            if vis not in groups:
                groups[vis] = VisibilityGroup(visibility=vis)
            groups[vis].consequences.append(consequence)
        return groups

    def _sort_by_priority(
        self, groups: dict[str, VisibilityGroup]
    ) -> dict[str, VisibilityGroup]:
        """Sort consequences within each group by priority descending."""
        for vis, group in groups.items():
            group.consequences = sorted(
                group.consequences,
                key=lambda c: c.priority,
                reverse=True,
            )
        return groups

    def _llm_summarize_groups(
        self, groups: dict[str, VisibilityGroup]
    ) -> dict[str, VisibilityGroup]:
        """Summarize groups using LLM (placeholder for future implementation)."""
        # TODO: Integrate with Ollama for LLM summarization
        # For now, just return unsummarized
        return groups

    def _format_outcome(self, outcome: dict[str, Any]) -> str:
        """Format a rule outcome into Keeper-style narrative text."""
        action = outcome.get("action", "unknown")
        if action == "coc_skill_check":
            label = outcome.get("label", "技能检定")
            success = outcome.get("success", False)
            roll = outcome.get("roll", "")
            grade = outcome.get("grade", "")
            if success:
                if grade == "extreme":
                    return f"{label}：大成功——你做到了远超预期的事情（{roll}）"
                elif grade == "hard":
                    return f"{label}：困难成功——你完成得相当漂亮（{roll}）"
                else:
                    return f"{label}：检定通过——你勉强做到了（{roll}）"
            else:
                return f"{label}：检定失败——事情没有按你的预期发展（{roll}）"
        elif action == "coc_sanity_check":
            san_loss = outcome.get("san_loss", "0")
            success = outcome.get("success", False)
            if success:
                return f"SAN检定：你稳住了心神，但那一幕已刻入记忆（损失 {san_loss}）"
            else:
                return f"SAN检定：理智的防线出现裂痕（损失 {san_loss}）"
        elif action == "attack_roll":
            hit = outcome.get("hit", False)
            weapon = outcome.get("weapon", "武器")
            if hit:
                return f"{weapon}攻击命中"
            else:
                return f"{weapon}攻击落空"
        elif action == "damage_roll":
            total = outcome.get("total", 0)
            if total > 0:
                return f"造成 {total} 点伤害"
            return "未造成伤害"
        else:
            return str(outcome)

    def _format_trigger_effect(self, effect: Any) -> str:
        """Format a trigger effect into human-readable text."""
        if hasattr(effect, "event_type"):
            return f"【事件触发】{effect.event_type}"
        return "【事件触发】"

    def _determine_priority(self, outcome: dict[str, Any]) -> int:
        """Determine priority of an outcome for sorting."""
        action = outcome.get("action", "")
        if action in ("coc_sanity_check", "attack_roll"):
            return 20
        elif action == "coc_skill_check":
            return 15
        elif action == "damage_roll":
            return 10
        return 5
