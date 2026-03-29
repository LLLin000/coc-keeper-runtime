"""KP Ops rendering for Discord surfaces.

This module provides renderers that transform VisibilitySnapshot data
into high-density KP/operator-facing Discord messages for the ops channel.
"""

from datetime import datetime

from dm_bot.orchestrator.visibility import (
    VisibilitySnapshot,
    WaitingReasonCode,
    PlayerSnapshot,
    SessionPhase,
    RoutingOutcome,
)


class KPOpsRenderer:
    """Renders VisibilitySnapshot for KP/operator surfaces."""

    def __init__(self, active_characters: dict[str, str] | None = None) -> None:
        self._active_characters = active_characters or {}

    def render_overview(self, snapshot: VisibilitySnapshot | None) -> str:
        """High-density overview for ops channel - shows phase, round, blockers, runtime."""
        if snapshot is None:
            return self._render_inactive()

        if not snapshot.campaign.campaign_id:
            return self._render_inactive()

        return self._render_ops_overview(snapshot)

    def render_detailed(self, snapshot: VisibilitySnapshot | None) -> str:
        """Detailed per-player view showing ready/submitted/onboarding status."""
        if snapshot is None:
            return self._render_inactive()

        if not snapshot.campaign.campaign_id:
            return self._render_inactive()

        return self._render_player_details(snapshot)

    def render_routing_history(self, snapshot: VisibilitySnapshot | None) -> str:
        """Routing history view showing last 10 decisions."""
        if snapshot is None:
            return self._render_inactive()

        if not snapshot.campaign.campaign_id:
            return self._render_inactive()

        return self._render_routing(snapshot)

    def _render_inactive(self) -> str:
        return "🔕 **当前没有活跃战役**"

    def _render_ops_overview(self, snapshot: VisibilitySnapshot) -> str:
        lines = []

        phase_emoji = self._phase_emoji(snapshot.session.phase)
        round_info = ""
        if snapshot.session.round_number:
            round_info = f" (Round {snapshot.session.round_number})"

        lines.append(f"🎭 Session: **{snapshot.session.phase.value}**{round_info}")

        waiting_line = self._build_waiting_line(snapshot)
        if waiting_line:
            lines.append(waiting_line)

        pending_ids = snapshot.waiting.metadata.get("pending_user_ids", [])
        if pending_ids:
            pending_names = [
                self._active_characters.get(uid, uid[:8]) for uid in pending_ids
            ]
            lines.append(f"📋 Pending: {', '.join(pending_names)}")

        if snapshot.adventure.adventure_id:
            lines.append(f"📦 Adventure: {snapshot.adventure.adventure_id}")
            if snapshot.adventure.scene_id:
                lines.append(f"   Scene: {snapshot.adventure.scene_id}")

        ready = snapshot.session.ready_count
        total = snapshot.session.total_members
        admin = "Yes" if snapshot.session.admin_started else "No"
        lines.append(f"👤 Ready: {ready}/{total} | Admin Started: {admin}")

        if snapshot.routing and snapshot.routing.outcome:
            outcome_emoji = self._outcome_emoji(snapshot.routing.outcome)
            lines.append(
                f"{outcome_emoji} Last Routing: {snapshot.routing.outcome.value}"
            )

        return "\n".join(lines)

    def _build_waiting_line(self, snapshot: VisibilitySnapshot) -> str:
        reason = snapshot.waiting.reason_code
        if reason == WaitingReasonCode.NONE:
            return ""

        if reason == WaitingReasonCode.WAITING_FOR_PLAYER_ACTIONS:
            submitted = snapshot.session.total_members - len(
                snapshot.waiting.metadata.get("pending_user_ids", [])
            )
            waiting = len(snapshot.waiting.metadata.get("pending_user_ids", []))
            return f"⏳ Waiting: {waiting} players to submit actions ({submitted}/{snapshot.session.total_members} submitted)"

        if reason == WaitingReasonCode.WAITING_FOR_READY:
            pending = len(snapshot.waiting.metadata.get("pending_user_ids", []))
            return f"⏳ Waiting: {pending} players to ready up"

        if reason == WaitingReasonCode.RESOLVING_SCENE:
            submitters = snapshot.waiting.metadata.get("submitted_user_ids", [])
            names = [self._active_characters.get(uid, uid[:8]) for uid in submitters]
            return f"⚙️ Resolving: {', '.join(names)} submitted"

        return f"⏳ {snapshot.waiting.message}"

    def _render_player_details(self, snapshot: VisibilitySnapshot) -> str:
        lines = []
        lines.append("**Player Details:**")

        players = snapshot.players.players
        if not players:
            lines.append("No players in session")
            return "\n".join(lines)

        for player in players:
            name = self._active_characters.get(player.user_id, player.name)
            detail = self._render_single_player(player, name)
            lines.append(detail)
            lines.append("")

        return "\n".join(lines).strip()

    def _render_single_player(self, player: PlayerSnapshot, name: str) -> str:
        char_info = f"{name}"
        if player.role:
            char_info += f" ({player.role})"

        lines = [f"👤 {char_info}"]

        ready_status = "✓ Ready" if player.is_ready else "✗ Not Ready"
        action_status = (
            "✓ Action Submitted" if player.has_submitted_action else "⏳ Pending Action"
        )
        onboard_status = (
            "✓ Onboarded" if player.onboarding_complete else "✗ Not Onboarded"
        )

        lines.append(f"  {ready_status} | {action_status} | {onboard_status}")

        return "\n".join(lines)

    def _render_routing(self, snapshot: VisibilitySnapshot) -> str:
        lines = []
        lines.append("**Routing History (Last 10):**")

        history = snapshot.routing_history
        if not history:
            lines.append("No routing history yet")
            return "\n".join(lines)

        for entry in reversed(history[-10:]):
            time_str = entry.timestamp.strftime("%H:%M")
            user = self._active_characters.get(entry.user_id, entry.user_id[:8])
            outcome_emoji = self._outcome_emoji(entry.outcome)

            entry_line = f"🕐 {time_str} | {user} | {entry.intent} | {outcome_emoji} {entry.outcome.value}"
            lines.append(entry_line)

            if entry.explanation:
                lines.append(f'    "{entry.explanation}"')

        return "\n".join(lines)

    def _phase_emoji(self, phase: SessionPhase) -> str:
        phase_emojis = {
            SessionPhase.LOBBY: "🏠",
            SessionPhase.ONBOARDING: "📋",
            SessionPhase.AWAITING_READY: "✋",
            SessionPhase.AWAITING_ADMIN_START: "👑",
            SessionPhase.SCENE_ROUND_OPEN: "🎭",
            SessionPhase.SCENE_ROUND_RESOLVING: "⚙️",
            SessionPhase.COMBAT: "⚔️",
            SessionPhase.PAUSED: "⏸️",
        }
        return phase_emojis.get(phase, "❓")

    def _outcome_emoji(self, outcome: RoutingOutcome) -> str:
        outcome_emojis = {
            RoutingOutcome.PROCESSED: "✅",
            RoutingOutcome.BUFFERED: "📦",
            RoutingOutcome.IGNORED: "🚫",
            RoutingOutcome.DEFERRED: "⏳",
            RoutingOutcome.UNKNOWN: "❓",
        }
        return outcome_emojis.get(outcome, "❓")
