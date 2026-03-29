"""Onboarding flow controller for managing pre-play onboarding."""

from dm_bot.orchestrator.session_store import SessionPhase, CampaignSession
from dm_bot.orchestrator.onboarding import (
    OnboardingContent,
    get_default_coc7e_onboarding,
    merge_with_adventure_onboarding,
)


class OnboardingController:
    def __init__(self, session: CampaignSession, gameplay=None):
        self.session = session
        self.gameplay = gameplay
        self._load_onboarding_content()

    def _load_onboarding_content(self) -> None:
        adventure_content = None
        if self.gameplay and self.gameplay.adventure:
            if hasattr(self.gameplay.adventure, "onboarding_content"):
                adventure_content = self.gameplay.adventure.onboarding_content

        if self.session.onboarding_content:
            adventure_content = self.session.onboarding_content

        default_content = get_default_coc7e_onboarding()
        merged = merge_with_adventure_onboarding(default_content, adventure_content)
        self.content = merged

    def should_show_onboarding(self) -> bool:
        return self.session.session_phase == SessionPhase.ONBOARDING

    def can_transition_to_scene(self) -> bool:
        return self.session.all_onboarding_complete()

    def mark_player_complete(self, user_id: str) -> None:
        self.session.set_onboarding_complete(user_id, True)

    def is_player_complete(self, user_id: str) -> bool:
        return self.session.is_onboarding_complete(user_id)

    def get_pending_players(self) -> list[str]:
        pending = []
        for member_id in self.session.member_ids:
            if not self.session.is_onboarding_complete(member_id):
                pending.append(member_id)
        return pending

    def get_onboarding_content(self) -> OnboardingContent:
        """Return onboarding content data for use by Discord layer to create views."""
        return self.content

    def transition_to_scene_if_ready(self) -> bool:
        if self.can_transition_to_scene():
            self.session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
            return True
        return False

    def start_onboarding(self) -> None:
        self.session.transition_to(SessionPhase.ONBOARDING)
        for member_id in self.session.member_ids:
            self.session.set_onboarding_complete(member_id, False)

    def get_onboarding_message(self) -> tuple[str, OnboardingContent | None]:
        if self.should_show_onboarding():
            pending = self.get_pending_players()
            if pending:
                return (
                    "📋 **游戏即将开始！**\n\n"
                    "在开始探索之前，请先完成规则概览。\n"
                    f"待确认玩家：{len(pending)} 人",
                    self.content,
                )
        return "", None

    def get_welcome_embed_content(self) -> str:
        return self.content.welcome
