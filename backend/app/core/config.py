from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="ARES_APP_ENV")
    database_url: str = Field(
        default="sqlite:///./ares.db",
        alias="DATABASE_URL",
    )
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="ARES_CORS_ORIGINS",
    )
    generation_provider: str = Field(default="stub", alias="ARES_GENERATION_PROVIDER")
    embedding_provider: str = Field(default="stub", alias="ARES_EMBEDDING_PROVIDER")
    world_bible_path_raw: str | None = Field(default=None, alias="ARES_WORLD_BIBLE_PATH")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def world_bible_path(self) -> Path:
        if self.world_bible_path_raw:
            return Path(self.world_bible_path_raw).expanduser().resolve()

        candidates = [
            Path.cwd() / "world_bible.md",
            Path.cwd().parent / "world_bible.md",
            Path("/app/world_bible.md"),
            Path(__file__).resolve().parents[3] / "world_bible.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return candidates[0]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
