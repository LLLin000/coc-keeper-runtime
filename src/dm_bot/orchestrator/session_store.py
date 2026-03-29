from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class CampaignRole(str, Enum):
    """Explicit campaign membership roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


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
    archive_profile_id: str | None = None
    panel_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    source: str = "archive"


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
        ready_players = sum(1 for r in self.player_ready.values() if r)
        return ready_players >= len(self.member_ids) and self.admin_started

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
        if not self.member_ids:
            return True
        return all(self.onboarding_completed.get(uid, False) for uid in self.member_ids)

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
        session = self._sessions[channel_id]
        session.member_ids.add(user_id)
        session._get_or_create_member(user_id)
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
        self, *, channel_id: str, user_id: str, profile_id: str
    ) -> CampaignSession:
        session = self._sessions[channel_id]
        session.selected_profiles[user_id] = profile_id
        if user_id in session.members:
            session.members[user_id].selected_profile_id = profile_id
        return session

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
                "phase_history": session.phase_history,
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
                phase_history=list(raw.get("phase_history", [])),
                onboarding_completed=dict(raw.get("onboarding_completed", {})),
                onboarding_content=dict(raw.get("onboarding_content", {})),
                pending_actions=dict(raw.get("pending_actions", {})),
                action_submitters=set(raw.get("action_submitters", [])),
                round_number=raw.get("round_number"),
            )
            self._sessions[channel_id] = session
