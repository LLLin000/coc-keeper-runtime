from pydantic import BaseModel, Field


class CampaignSession(BaseModel):
    campaign_id: str
    channel_id: str
    guild_id: str
    owner_id: str
    member_ids: set[str] = Field(default_factory=set)
    active_characters: dict[str, str] = Field(default_factory=dict)
    active_roles: dict[str, str] = Field(default_factory=dict)
    selected_profiles: dict[str, str] = Field(default_factory=dict)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, CampaignSession] = {}
        self._archive_channels: dict[str, str] = {}
        self._trace_channels: dict[str, str] = {}

    def bind_campaign(self, *, campaign_id: str, channel_id: str, guild_id: str, owner_id: str) -> CampaignSession:
        session = CampaignSession(
            campaign_id=campaign_id,
            channel_id=channel_id,
            guild_id=guild_id,
            owner_id=owner_id,
            member_ids={owner_id},
        )
        self._sessions[channel_id] = session
        return session

    def join_campaign(self, *, channel_id: str, user_id: str) -> CampaignSession:
        session = self._sessions[channel_id]
        session.member_ids.add(user_id)
        return session

    def leave_campaign(self, *, channel_id: str, user_id: str) -> CampaignSession:
        session = self._sessions[channel_id]
        session.member_ids.discard(user_id)
        session.active_characters.pop(user_id, None)
        return session

    def bind_character(self, *, channel_id: str, user_id: str, character_name: str) -> CampaignSession:
        session = self._sessions[channel_id]
        session.active_characters[user_id] = character_name
        return session

    def bind_role(self, *, channel_id: str, user_id: str, role: str) -> CampaignSession:
        session = self._sessions[channel_id]
        session.active_roles[user_id] = role
        return session

    def select_archive_profile(self, *, channel_id: str, user_id: str, profile_id: str) -> CampaignSession:
        session = self._sessions[channel_id]
        session.selected_profiles[user_id] = profile_id
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
            }
            for channel_id, session in self._sessions.items()
        }
        payload["_meta"] = {
            "archive_channels": dict(self._archive_channels),
            "trace_channels": dict(self._trace_channels),
        }
        return payload

    def load_sessions(self, payload: dict[str, dict[str, object]]) -> None:
        self._sessions = {}
        meta = dict(payload.get("_meta", {}))
        self._archive_channels = dict(meta.get("archive_channels", {}))
        self._trace_channels = dict(meta.get("trace_channels", {}))
        for channel_id, raw in payload.items():
            if channel_id == "_meta":
                continue
            session = CampaignSession(
                campaign_id=str(raw["campaign_id"]),
                channel_id=str(raw.get("channel_id", channel_id)),
                guild_id=str(raw["guild_id"]),
                owner_id=str(raw["owner_id"]),
                member_ids=set(raw.get("member_ids", [])),
                active_characters=dict(raw.get("active_characters", {})),
                active_roles=dict(raw.get("active_roles", {})),
                selected_profiles=dict(raw.get("selected_profiles", {})),
            )
            self._sessions[channel_id] = session
