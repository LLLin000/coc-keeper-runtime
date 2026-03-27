from pydantic import BaseModel, Field


class CampaignSession(BaseModel):
    campaign_id: str
    channel_id: str
    guild_id: str
    owner_id: str
    member_ids: set[str] = Field(default_factory=set)
    active_characters: dict[str, str] = Field(default_factory=dict)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, CampaignSession] = {}

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

    def active_character_for(self, *, channel_id: str, user_id: str) -> str | None:
        session = self._sessions.get(channel_id)
        if session is None:
            return None
        return session.active_characters.get(user_id)

    def get_by_channel(self, channel_id: str) -> CampaignSession | None:
        return self._sessions.get(channel_id)

    def dump_sessions(self) -> dict[str, dict[str, object]]:
        return {
            channel_id: {
                "campaign_id": session.campaign_id,
                "channel_id": session.channel_id,
                "guild_id": session.guild_id,
                "owner_id": session.owner_id,
                "member_ids": sorted(session.member_ids),
                "active_characters": dict(session.active_characters),
            }
            for channel_id, session in self._sessions.items()
        }

    def load_sessions(self, payload: dict[str, dict[str, object]]) -> None:
        self._sessions = {}
        for channel_id, raw in payload.items():
            session = CampaignSession(
                campaign_id=str(raw["campaign_id"]),
                channel_id=str(raw.get("channel_id", channel_id)),
                guild_id=str(raw["guild_id"]),
                owner_id=str(raw["owner_id"]),
                member_ids=set(raw.get("member_ids", [])),
                active_characters=dict(raw.get("active_characters", {})),
            )
            self._sessions[channel_id] = session
