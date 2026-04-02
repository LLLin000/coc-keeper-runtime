from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from dm_bot.orchestrator.governance_event_log import GovernanceEventLog, GovernanceEvent


class SkillUsageTracker(BaseModel):
    """Tracks skill usage per player per session for COC experience system.

    COC 7e improvement rules: skills used during a session are eligible
    for improvement rolls at session end. This tracker records which skills
    were used (and whether they succeeded) to enable the improvement phase.

    Data Structure:
    - usage: player_id -> skill_name -> count (total uses)
    - successes: player_id -> skill_name -> count (successful uses only)
    """

    # Map: player_id -> skill_name -> usage_count
    usage: dict[str, dict[str, int]] = Field(default_factory=dict)

    # Map: player_id -> skill_name -> success_count
    successes: dict[str, dict[str, int]] = Field(default_factory=dict)

    def record_usage(
        self, player_id: str, skill_name: str, success: bool = False
    ) -> None:
        """Record that a player used a skill.

        Args:
            player_id: The player's user ID
            skill_name: Name of the skill used (e.g., "fighting", "shooting")
            success: Whether the skill check was successful
        """
        if player_id not in self.usage:
            self.usage[player_id] = {}
            self.successes[player_id] = {}

        self.usage[player_id][skill_name] = self.usage[player_id].get(skill_name, 0) + 1
        if success:
            self.successes[player_id][skill_name] = (
                self.successes[player_id].get(skill_name, 0) + 1
            )

    def get_eligible_skills(self, player_id: str) -> list[str]:
        """Get list of skills eligible for improvement (any usage counts).

        Per COC 7e rules, any skill that was used during the session is
        eligible for an improvement roll at session end.
        """
        return list(self.usage.get(player_id, {}).keys())

    def get_usage_count(self, player_id: str, skill_name: str) -> int:
        """Get usage count for a specific skill.

        Args:
            player_id: The player's user ID
            skill_name: Name of the skill

        Returns:
            Total number of times the skill was used
        """
        return self.usage.get(player_id, {}).get(skill_name, 0)

    def get_success_count(self, player_id: str, skill_name: str) -> int:
        """Get success count for a specific skill.

        Args:
            player_id: The player's user ID
            skill_name: Name of the skill

        Returns:
            Number of successful uses of the skill
        """
        return self.successes.get(player_id, {}).get(skill_name, 0)

    def clear(self) -> None:
        """Clear all usage data (call at session end/improvement phase)."""
        self.usage.clear()
        self.successes.clear()


class SelectProfileError(str, Enum):
    NO_SESSION = "no_session"
    NOT_MEMBER = "not_member"
    PROFILE_NOT_FOUND = "profile_not_found"
    PROFILE_INACTIVE = "profile_inactive"
    NOT_PROFILE_OWNER = "not_profile_owner"


class ReadyGateError(str, Enum):
    NO_SESSION = "no_session"
    NOT_MEMBER = "not_member"
    NO_PROFILE_SELECTED = "no_profile_selected"


class ValidationResult(BaseModel):
    success: bool = True
    error: str | None = None
    error_message: str | None = None


class CampaignRole(str, Enum):
    """Explicit campaign membership roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class DuplicateMemberError(Exception):
    """Raised when a user attempts to join a campaign they are already a member of."""

    pass


class UnboundChannelError(Exception):
    """Raised when attempting to join a channel that has no bound campaign."""

    pass


class CampaignMember(BaseModel):
    """Structured campaign membership replacing primitive set-of-strings."""

    user_id: str
    campaign_id: str
    joined_at: datetime = Field(default_factory=datetime.now)
    role: CampaignRole = CampaignRole.MEMBER
    ready: bool = False
    selected_profile_id: str | None = None
    active_character_name: str | None = None


class CampaignCharacterInstance(BaseModel):
    """Active investigator projection for a player in a campaign."""

    campaign_id: str
    user_id: str
    character_name: str
    status: str = "active"
    archive_profile_id: str | None = None
    panel_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    source: str = "archive"


class Visibility(str, Enum):
    """Visibility levels for batch action results."""

    PUBLIC = "public"
    PRIVATE = "private"
    GROUP = "group"
    KEEPER = "keeper"


@dataclass
class ActionBatchEntry:
    """A single action entry in a scene round batch."""

    user_id: str
    character_id: str
    action_text: str
    submitted_at: datetime = field(default_factory=datetime.now)
    dex_value: int | None = None
    visibility: Visibility = Visibility.PUBLIC


class SessionPhase(str, Enum):
    """Explicit session phases for multiplayer campaigns."""

    ONBOARDING = "onboarding"
    LOBBY = "lobby"
    AWAITING_READY = "awaiting_ready"
    AWAITING_ADMIN_START = "awaiting_admin_start"
    SCENE_ROUND_OPEN = "scene_round_open"
    SCENE_ROUND_RESOLVING = "scene_round_resolving"
    COMBAT = "combat"
    PAUSED = "paused"


class CampaignSession(BaseModel):
    campaign_id: str
    channel_id: str
    guild_id: str
    owner_id: str
    member_ids: set[str] = Field(default_factory=set)
    active_characters: dict[str, str] = Field(default_factory=dict)
    active_roles: dict[str, str] = Field(default_factory=dict)
    selected_profiles: dict[str, str] = Field(default_factory=dict)
    # Structured identity models (Phase 52)
    members: dict[str, CampaignMember] = Field(default_factory=dict)
    character_instances: dict[str, CampaignCharacterInstance] = Field(
        default_factory=dict
    )
    # Session phase tracking (vC.1.2)
    session_phase: SessionPhase = SessionPhase.LOBBY
    player_ready: dict[str, bool] = Field(default_factory=dict)
    admin_started: bool = False
    phase_history: list[tuple[str, datetime]] = Field(default_factory=list)
    # Onboarding tracking (vC.1.2 - Phase 48)
    onboarding_completed: dict[str, bool] = Field(default_factory=dict)
    onboarding_content: dict[str, object] = Field(default_factory=dict)
    # Round collection tracking (vC.1.2 - Phase 49)
    pending_actions: dict[str, str] = Field(default_factory=dict)
    action_submitters: set[str] = Field(default_factory=set)
    # Round tracking (Phase 54 - KP Ops Surfaces)
    round_number: int | None = None

    # Skill usage tracking (E79 - Skill Usage Tracking & Combat Integration)
    skill_tracker: SkillUsageTracker = Field(default_factory=SkillUsageTracker)

    def _get_or_create_member(self, user_id: str) -> CampaignMember:
        if user_id not in self.members:
            self.members[user_id] = CampaignMember(
                user_id=user_id,
                campaign_id=self.campaign_id,
            )
        return self.members[user_id]

    def transition_to(self, new_phase: SessionPhase) -> None:
        self.session_phase = new_phase
        self.phase_history.append((new_phase.value, datetime.now()))

    def set_player_ready(self, user_id: str, ready: bool) -> None:
        self.player_ready[user_id] = ready
        if user_id in self.members:
            self.members[user_id].ready = ready

    def can_start_session(self) -> bool:
        if not self.member_ids:
            return False
        player_ids = [
            uid
            for uid in self.member_ids
            if self.members.get(uid, None)
            and self.members[uid].role == CampaignRole.MEMBER
        ]
        if not player_ids:
            return True
        ready_players = sum(
            1 for uid in player_ids if self.player_ready.get(uid, False)
        )
        return ready_players >= len(player_ids) and self.admin_started

    def all_ready(self) -> bool:
        """Check if all PLAYER campaign members have marked themselves ready.

        Excludes owner/admin - only regular MEMBER role players need to ready up.
        """
        if not self.member_ids:
            return True
        player_ids = [
            uid
            for uid in self.member_ids
            if self.members.get(uid, None)
            and self.members[uid].role == CampaignRole.MEMBER
        ]
        if not player_ids:
            return True
        return all(self.player_ready.get(uid, False) for uid in player_ids)

    def transition_on_all_ready(self) -> bool:
        """If all players are ready and phase is AWAITING_READY, advance to AWAITING_ADMIN_START.
        Returns True if transition occurred, False otherwise."""
        if self.session_phase == SessionPhase.AWAITING_READY and self.all_ready():
            self.transition_to(SessionPhase.AWAITING_ADMIN_START)
            return True
        return False

    def get_phase_context(self) -> dict[str, object]:
        return {
            "phase": self.session_phase.value,
            "player_ready_count": sum(1 for r in self.player_ready.values() if r),
            "total_members": len(self.member_ids),
            "admin_started": self.admin_started,
            "onboarding_completed_count": sum(
                1 for c in self.onboarding_completed.values() if c
            ),
            "onboarding_content": bool(self.onboarding_content),
        }

    def set_onboarding_complete(self, user_id: str, complete: bool = True) -> None:
        self.onboarding_completed[user_id] = complete

    def is_onboarding_complete(self, user_id: str) -> bool:
        return self.onboarding_completed.get(user_id, False)

    def all_onboarding_complete(self) -> bool:
        """Check if all PLAYER campaign members have completed onboarding.

        Excludes owner/admin - only regular MEMBER role players need to complete onboarding.
        """
        if not self.member_ids:
            return True
        player_ids = [
            uid
            for uid in self.member_ids
            if self.members.get(uid, None)
            and self.members[uid].role == CampaignRole.MEMBER
        ]
        if not player_ids:
            return True
        return all(self.onboarding_completed.get(uid, False) for uid in player_ids)

    def set_onboarding_content(self, content: dict[str, object]) -> None:
        self.onboarding_content = content

    def get_onboarding_content(self) -> dict[str, object]:
        return self.onboarding_content

    def set_player_action(self, user_id: str, action: str) -> None:
        if action and action.strip():
            self.pending_actions[user_id] = action.strip()
            self.action_submitters.add(user_id)

    def clear_player_action(self, user_id: str) -> None:
        self.pending_actions.pop(user_id, None)
        self.action_submitters.discard(user_id)

    def clear_all_actions(self) -> None:
        self.pending_actions.clear()
        self.action_submitters.clear()

    def has_submitted(self, user_id: str) -> bool:
        return user_id in self.action_submitters

    def get_pending_members(self) -> list[str]:
        return [mid for mid in self.member_ids if mid not in self.action_submitters]

    def all_submitted(self) -> bool:
        if not self.member_ids:
            return True
        return all(uid in self.action_submitters for uid in self.member_ids)

    def get_submitter_names(self) -> list[str]:
        names = []
        for uid in self.action_submitters:
            char_name = self.active_characters.get(uid)
            if char_name:
                names.append(char_name)
        return names

    def get_pending_member_names(self) -> list[str]:
        names = []
        for uid in self.get_pending_members():
            char_name = self.active_characters.get(uid)
            if char_name:
                names.append(char_name)
        return names


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, CampaignSession] = {}
        self._archive_channels: dict[str, str] = {}
        self._trace_channels: dict[str, str] = {}
        self._admin_channels: dict[str, str] = {}
        self._game_channels: dict[str, str] = {}
        self._player_status_channels: dict[str, str] = {}
        self._ops_channels: dict[str, str] = {}
        self.event_log = GovernanceEventLog()

    def bind_campaign(
        self, *, campaign_id: str, channel_id: str, guild_id: str, owner_id: str
    ) -> CampaignSession:
        session = CampaignSession(
            campaign_id=campaign_id,
            channel_id=channel_id,
            guild_id=guild_id,
            owner_id=owner_id,
            member_ids={owner_id},
        )
        session.members[owner_id] = CampaignMember(
            user_id=owner_id,
            campaign_id=campaign_id,
            role=CampaignRole.OWNER,
        )
        self._sessions[channel_id] = session
        return session

    def join_campaign(self, *, channel_id: str, user_id: str) -> CampaignSession:
        if channel_id not in self._sessions:
            raise UnboundChannelError(
                f"No campaign is bound to channel {channel_id}. "
                "Use /bind_campaign first."
            )
        session = self._sessions[channel_id]

        if user_id in session.members:
            raise DuplicateMemberError(
                f"User {user_id} is already a member of campaign {session.campaign_id}."
            )

        session.member_ids.add(user_id)
        member = session._get_or_create_member(user_id)

        session.character_instances[user_id] = CampaignCharacterInstance(
            campaign_id=session.campaign_id,
            user_id=user_id,
            character_name="",
        )

        # Auto-transition lobby → awaiting_ready when first non-owner joins
        if session.session_phase == SessionPhase.LOBBY and user_id != session.owner_id:
            session.transition_to(SessionPhase.AWAITING_READY)

        return session

    def leave_campaign(self, *, channel_id: str, user_id: str) -> CampaignSession:
        session = self._sessions[channel_id]
        session.member_ids.discard(user_id)
        session.active_characters.pop(user_id, None)
        session.members.pop(user_id, None)
        session.character_instances.pop(user_id, None)
        session.clear_player_action(user_id)
        return session

    def bind_character(
        self, *, channel_id: str, user_id: str, character_name: str
    ) -> CampaignSession:
        session = self._sessions[channel_id]
        session.active_characters[user_id] = character_name
        if user_id in session.members:
            session.members[user_id].active_character_name = character_name
        if user_id in session.character_instances:
            session.character_instances[user_id].character_name = character_name
            session.character_instances[user_id].status = "active"
        return session

    def bind_role(self, *, channel_id: str, user_id: str, role: str) -> CampaignSession:
        session = self._sessions[channel_id]
        session.active_roles[user_id] = role
        if user_id in session.members:
            try:
                session.members[user_id].role = CampaignRole(role)
            except ValueError:
                pass
        return session

    def select_archive_profile(
        self,
        *,
        channel_id: str,
        user_id: str,
        profile_id: str,
        profiles: dict[str, object] | None = None,
    ) -> ValidationResult:
        session = self._sessions.get(channel_id)
        if session is None:
            return ValidationResult(
                success=False,
                error=SelectProfileError.NO_SESSION.value,
                error_message="当前频道没有绑定战役。",
            )
        if user_id not in session.members:
            return ValidationResult(
                success=False,
                error=SelectProfileError.NOT_MEMBER.value,
                error_message="你还不是这个战役的成员。请先使用 /join_campaign 加入。",
            )
        if profiles is not None:
            profile = profiles.get(profile_id)
            if profile is None:
                return ValidationResult(
                    success=False,
                    error=SelectProfileError.PROFILE_NOT_FOUND.value,
                    error_message=f"档案 `{profile_id}` 不存在。",
                )
            if isinstance(profile, dict):
                profile_status = profile.get("status", "active")
                profile_user_id = profile.get("user_id", "")
            else:
                profile_status = getattr(profile, "status", "active")
                profile_user_id = getattr(profile, "user_id", "")
            if profile_status != "active":
                return ValidationResult(
                    success=False,
                    error=SelectProfileError.PROFILE_INACTIVE.value,
                    error_message=f"档案 `{profile_id}` 已归档，无法选用。",
                )
            if str(profile_user_id) != user_id:
                return ValidationResult(
                    success=False,
                    error=SelectProfileError.NOT_PROFILE_OWNER.value,
                    error_message="你只能选用自己的档案。",
                )
        session.selected_profiles[user_id] = profile_id
        if user_id in session.members:
            session.members[user_id].selected_profile_id = profile_id
        if user_id in session.character_instances:
            profile_name = profile_id
            if profiles is not None:
                p = profiles.get(profile_id)
                if p is not None:
                    if isinstance(p, dict):
                        profile_name = p.get("name", profile_id)
                    else:
                        profile_name = getattr(p, "name", profile_id)
            session.character_instances[user_id].archive_profile_id = profile_id
            session.character_instances[user_id].character_name = profile_name
            session.character_instances[user_id].status = "active"
        return ValidationResult(success=True)

    def validate_ready(self, *, channel_id: str, user_id: str) -> ValidationResult:
        session = self._sessions.get(channel_id)
        if session is None:
            return ValidationResult(
                success=False,
                error=ReadyGateError.NO_SESSION.value,
                error_message="当前频道没有绑定战役。",
            )
        member = session.members.get(user_id)
        if member is None:
            return ValidationResult(
                success=False,
                error=ReadyGateError.NOT_MEMBER.value,
                error_message="你还不是这个战役的成员。请先使用 /join_campaign 加入。",
            )
        instance = session.character_instances.get(user_id)
        if not instance or instance.status != "active" or not instance.character_name:
            return ValidationResult(
                success=False,
                error=ReadyGateError.NO_PROFILE_SELECTED.value,
                error_message="请先使用 /select_profile 选择一个调查员档案，或提供角色名称。",
            )
        return ValidationResult(success=True)

    def selected_profile_for(self, *, channel_id: str, user_id: str) -> str | None:
        session = self._sessions.get(channel_id)
        if session is None:
            return None
        return session.selected_profiles.get(user_id)

    def bind_archive_channel(self, *, guild_id: str, channel_id: str) -> None:
        self._archive_channels[guild_id] = channel_id

    def archive_channel_for(self, guild_id: str) -> str | None:
        return self._archive_channels.get(guild_id)

    def bind_trace_channel(self, *, guild_id: str, channel_id: str) -> None:
        self._trace_channels[guild_id] = channel_id

    def trace_channel_for(self, guild_id: str) -> str | None:
        return self._trace_channels.get(guild_id)

    def bind_admin_channel(self, *, guild_id: str, channel_id: str) -> None:
        self._admin_channels[guild_id] = channel_id

    def admin_channel_for(self, guild_id: str) -> str | None:
        return self._admin_channels.get(guild_id)

    def bind_game_channel(self, *, guild_id: str, channel_id: str) -> None:
        self._game_channels[guild_id] = channel_id

    def game_channel_for(self, guild_id: str) -> str | None:
        return self._game_channels.get(guild_id)

    def bind_player_status_channel(self, *, guild_id: str, channel_id: str) -> None:
        self._player_status_channels[guild_id] = channel_id

    def player_status_channel_for(self, guild_id: str) -> str | None:
        return self._player_status_channels.get(guild_id)

    def bind_ops_channel(self, *, guild_id: str, channel_id: str) -> None:
        self._ops_channels[guild_id] = channel_id

    def ops_channel_for(self, guild_id: str) -> str | None:
        return self._ops_channels.get(guild_id)

    def active_character_for(self, *, channel_id: str, user_id: str) -> str | None:
        session = self._sessions.get(channel_id)
        if session is None:
            return None
        return session.active_characters.get(user_id)

    def active_role_for(self, *, channel_id: str, user_id: str) -> str | None:
        session = self._sessions.get(channel_id)
        if session is None:
            return None
        return session.active_roles.get(user_id)

    def get_by_channel(self, channel_id: str) -> CampaignSession | None:
        return self._sessions.get(channel_id)

    def get_by_campaign(self, campaign_id: str) -> CampaignSession | None:
        for session in self._sessions.values():
            if session.campaign_id == campaign_id:
                return session
        return None

    def get_member(self, channel_id: str, user_id: str) -> CampaignMember | None:
        session = self._sessions.get(channel_id)
        if session is None:
            return None
        return session.members.get(user_id)

    def get_character_instance(
        self, channel_id: str, user_id: str
    ) -> CampaignCharacterInstance | None:
        session = self._sessions.get(channel_id)
        if session is None:
            return None
        return session.character_instances.get(user_id)

    def get_active_instances_for_user(
        self, user_id: str
    ) -> list[tuple[str, CampaignCharacterInstance]]:
        results = []
        for session in self._sessions.values():
            instance = session.character_instances.get(user_id)
            if instance and instance.status == "active" and instance.character_name:
                results.append((session.channel_id, instance))
        return results

    def retire_instance(
        self, *, channel_id: str, user_id: str
    ) -> CampaignCharacterInstance:
        session = self._sessions.get(channel_id)
        if session is None:
            raise ValueError("No campaign bound")
        instance = session.character_instances.get(user_id)
        if instance is None:
            raise ValueError("User has no campaign character instance")
        if instance.status == "retired":
            return instance
        instance.status = "retired"
        instance.character_name = ""
        instance.archive_profile_id = None
        self.event_log.append_event(
            GovernanceEvent(
                operation="instance_retire",
                user_id=user_id,
                campaign_id=session.campaign_id,
                operator_id=user_id,
                before_state={"status": "active"},
                after_state={"status": "retired"},
            )
        )
        return instance

    def select_instance_profile(
        self,
        *,
        channel_id: str,
        user_id: str,
        profile_id: str,
        archive_repo=None,
    ) -> CampaignCharacterInstance:
        session = self._sessions.get(channel_id)
        if session is None:
            raise ValueError("No campaign bound")
        instance = session.character_instances.get(user_id)
        if instance is None:
            raise ValueError("User has no campaign character instance")
        profile_name = profile_id
        if archive_repo is not None:
            profile = archive_repo.get_profile(user_id, profile_id)
            if profile is None:
                raise ValueError(f"Profile {profile_id} does not exist")
            if profile.status != "active":
                raise ValueError(f"Profile {profile_id} is 已归档")
            profile_name = profile.name
        instance.archive_profile_id = profile_id
        instance.character_name = profile_name
        instance.status = "active"
        self.event_log.append_event(
            GovernanceEvent(
                operation="instance_select",
                user_id=user_id,
                profile_id=profile_id,
                campaign_id=session.campaign_id,
                operator_id=user_id,
            )
        )
        return instance

    def force_archive_instance(
        self,
        *,
        channel_id: str,
        admin_id: str,
        target_user_id: str,
        reason: str,
    ) -> CampaignCharacterInstance:
        session = self._sessions.get(channel_id)
        if session is None:
            raise ValueError("No campaign bound")
        member = session.members.get(target_user_id)
        if member is None:
            raise ValueError(f"User {target_user_id} is not a member")
        if session.owner_id != admin_id:
            raise PermissionError("Only campaign owner can force archive")
        instance = session.character_instances.get(target_user_id)
        if instance is None:
            raise ValueError("Target user has no campaign character instance")
        before_state = instance.model_dump()
        instance.status = "retired"
        instance.character_name = ""
        instance.archive_profile_id = None
        self.event_log.append_event(
            GovernanceEvent(
                operation="instance_force_archive",
                user_id=target_user_id,
                campaign_id=session.campaign_id,
                operator_id=admin_id,
                before_state=before_state,
                after_state=instance.model_dump(),
                reason=reason,
            )
        )
        return instance

    def reassign_ownership(
        self,
        *,
        channel_id: str,
        current_owner_id: str,
        new_owner_id: str,
        reason: str,
    ) -> tuple[CampaignMember, CampaignMember]:
        session = self._sessions.get(channel_id)
        if session is None:
            raise ValueError("No campaign bound")
        if current_owner_id != session.owner_id:
            raise PermissionError("Only the current owner can reassign ownership")
        if current_owner_id == new_owner_id:
            raise ValueError("Cannot reassign ownership to yourself")
        old_owner = session.members.get(current_owner_id)
        new_owner = session.members.get(new_owner_id)
        if old_owner is None or new_owner is None:
            raise ValueError(f"User {new_owner_id} is not a member")
        old_owner.role = CampaignRole.ADMIN
        new_owner.role = CampaignRole.OWNER
        session.owner_id = new_owner_id
        self.event_log.append_event(
            GovernanceEvent(
                operation="ownership_reassign",
                user_id=new_owner_id,
                campaign_id=session.campaign_id,
                operator_id=current_owner_id,
                before_state={
                    "role": CampaignRole.OWNER.value,
                    "owner_id": current_owner_id,
                },
                after_state={
                    "role": CampaignRole.ADMIN.value,
                    "owner_id": new_owner_id,
                },
                reason=reason,
            )
        )
        return new_owner, old_owner

    def list_members(self, channel_id: str) -> list[CampaignMember]:
        session = self._sessions.get(channel_id)
        if session is None:
            return []
        return list(session.members.values())

    def channels_selecting_profile(self, *, user_id: str, profile_id: str) -> list[str]:
        return [
            session.channel_id
            for session in self._sessions.values()
            if session.selected_profiles.get(user_id) == profile_id
        ]

    def dump_sessions(self) -> dict[str, dict[str, object]]:
        payload = {
            channel_id: {
                "campaign_id": session.campaign_id,
                "channel_id": session.channel_id,
                "guild_id": session.guild_id,
                "owner_id": session.owner_id,
                "member_ids": sorted(session.member_ids),
                "active_characters": dict(session.active_characters),
                "active_roles": dict(session.active_roles),
                "selected_profiles": dict(session.selected_profiles),
                "members": {
                    uid: m.model_dump(mode="json") for uid, m in session.members.items()
                },
                "character_instances": {
                    uid: ci.model_dump(mode="json")
                    for uid, ci in session.character_instances.items()
                },
                "session_phase": session.session_phase.value,
                "player_ready": dict(session.player_ready),
                "admin_started": session.admin_started,
                "phase_history": [
                    (phase, ts.isoformat()) for phase, ts in session.phase_history
                ],
                "onboarding_completed": dict(session.onboarding_completed),
                "onboarding_content": dict(session.onboarding_content),
                "pending_actions": dict(session.pending_actions),
                "action_submitters": sorted(session.action_submitters),
                "round_number": session.round_number,
            }
            for channel_id, session in self._sessions.items()
        }
        payload["_meta"] = {
            "archive_channels": dict(self._archive_channels),
            "trace_channels": dict(self._trace_channels),
            "admin_channels": dict(self._admin_channels),
            "game_channels": dict(self._game_channels),
            "player_status_channels": dict(self._player_status_channels),
            "ops_channels": dict(self._ops_channels),
        }
        return payload

    def load_sessions(self, payload: dict[str, dict[str, object]]) -> None:
        self._sessions = {}
        meta = dict(payload.get("_meta", {}))
        self._archive_channels = dict(meta.get("archive_channels", {}))
        self._trace_channels = dict(meta.get("trace_channels", {}))
        self._admin_channels = dict(meta.get("admin_channels", {}))
        self._game_channels = dict(meta.get("game_channels", {}))
        self._player_status_channels = dict(meta.get("player_status_channels", {}))
        self._ops_channels = dict(meta.get("ops_channels", {}))
        for channel_id, raw in payload.items():
            if channel_id == "_meta":
                continue

            raw_members = raw.get("members", {})
            raw_instances = raw.get("character_instances", {})

            members: dict[str, CampaignMember] = {
                uid: CampaignMember.model_validate(m) for uid, m in raw_members.items()
            }
            character_instances: dict[str, CampaignCharacterInstance] = {
                uid: CampaignCharacterInstance.model_validate(ci)
                for uid, ci in raw_instances.items()
            }

            # Backward-compat: reconstruct members from legacy fields if missing
            if not members and raw.get("member_ids"):
                owner_id = str(raw.get("owner_id", ""))
                for uid in raw["member_ids"]:
                    uid_str = str(uid)
                    role = (
                        CampaignRole.OWNER
                        if uid_str == owner_id
                        else CampaignRole.MEMBER
                    )
                    members[uid_str] = CampaignMember(
                        user_id=uid_str,
                        campaign_id=str(raw["campaign_id"]),
                        role=role,
                        ready=bool(raw.get("player_ready", {}).get(uid_str, False)),
                        selected_profile_id=raw.get("selected_profiles", {}).get(
                            uid_str
                        ),
                        active_character_name=raw.get("active_characters", {}).get(
                            uid_str
                        ),
                    )

            session = CampaignSession(
                campaign_id=str(raw["campaign_id"]),
                channel_id=str(raw.get("channel_id", channel_id)),
                guild_id=str(raw["guild_id"]),
                owner_id=str(raw["owner_id"]),
                member_ids=set(raw.get("member_ids", [])),
                active_characters=dict(raw.get("active_characters", {})),
                active_roles=dict(raw.get("active_roles", {})),
                selected_profiles=dict(raw.get("selected_profiles", {})),
                members=members,
                character_instances=character_instances,
                session_phase=SessionPhase(raw.get("session_phase", "lobby")),
                player_ready=dict(raw.get("player_ready", {})),
                admin_started=raw.get("admin_started", False),
                phase_history=[
                    (phase, datetime.fromisoformat(ts))
                    for phase, ts in raw.get("phase_history", [])
                ],
                onboarding_completed=dict(raw.get("onboarding_completed", {})),
                onboarding_content=dict(raw.get("onboarding_content", {})),
                pending_actions=dict(raw.get("pending_actions", {})),
                action_submitters=set(raw.get("action_submitters", [])),
                round_number=raw.get("round_number"),
            )
            self._sessions[channel_id] = session
