"""Character archive — versioned wrapper around CharacterSheet.

Canonical fields:
- schema_version: int — archive schema version (currently 1)
- character_id: str — unique identifier (matches player user_id for fast path)
- player_id: str — Discord user ID who owns this character
- sheet: CharacterSheet — the COC investigator stats, skills, metadata
- created_at: datetime — archive creation timestamp
- updated_at: datetime — last modification timestamp
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from dm_bot.character.sheet import CharacterSheet


class CharacterArchive(BaseModel):
    """Versioned character archive with player binding."""

    schema_version: int = Field(default=1, description="Archive schema version")
    character_id: str = Field(min_length=1, description="Unique character identifier")
    player_id: str = Field(min_length=1, description="Discord user ID of owner")
    sheet: CharacterSheet = Field(description="COC investigator sheet data")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Archive creation time")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modification time")
