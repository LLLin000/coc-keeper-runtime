from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DM_BOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    discord_token: str = Field(default="")
    discord_application_id: str = Field(default="")
    discord_public_key: str = Field(default="")
    discord_guild_id: str = Field(default="")
    ollama_base_url: str = Field(default="http://localhost:11434/v1")
    router_model: str = Field(default="qwen3:1.7b")
    narrator_model: str = Field(default="qwen3:8b")


def get_settings() -> Settings:
    return Settings()
