from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_backend_root() -> Path:
    current_file = Path(__file__).resolve()
    for candidate in current_file.parents:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return current_file.parents[2]


def _resolve_project_root(backend_root: Path) -> Path:
    candidate = backend_root.parent
    if (candidate / "docker-compose.yml").exists():
        return candidate
    return backend_root


def _dedupe_paths(*paths: Path) -> tuple[Path, ...]:
    unique_paths: list[Path] = []
    for path in paths:
        if path not in unique_paths:
            unique_paths.append(path)
    return tuple(unique_paths)


_BACKEND_ROOT = _resolve_backend_root()
_PROJECT_ROOT = _resolve_project_root(_BACKEND_ROOT)


def discover_env_file_paths(
    *,
    app_root: Path | None = None,
    backend_root: Path | None = None,
) -> tuple[Path, ...]:
    repo_root = (app_root or _PROJECT_ROOT).resolve()
    backend_dir = (backend_root or _BACKEND_ROOT).resolve()
    return _dedupe_paths(repo_root / ".env", backend_dir / ".env")


def discover_env_file_path(
    *,
    app_root: Path | None = None,
    backend_root: Path | None = None,
) -> Path:
    candidates = discover_env_file_paths(
        app_root=app_root,
        backend_root=backend_root,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


_ENV_FILE_PATHS = discover_env_file_paths()
_ENV_FILE_PATH = discover_env_file_path()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=tuple(str(path) for path in _ENV_FILE_PATHS),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="ARES_APP_ENV")
    database_url: str = Field(
        default="sqlite:///./ares.db",
        alias="DATABASE_URL",
    )
    cors_origins_raw: str = Field(
        default="http://localhost:5180,http://localhost:5173,http://localhost:3000",
        alias="ARES_CORS_ORIGINS",
    )
    generation_provider: str = Field(default="stub", alias="ARES_GENERATION_PROVIDER")
    generation_model: str = Field(default="claude-haiku-4-5", alias="ARES_MODEL")
    embedding_provider: str = Field(default="stub", alias="ARES_EMBEDDING_PROVIDER")
    database_bootstrap: Literal["create_all", "disabled"] = Field(
        default="create_all",
        alias="ARES_DB_BOOTSTRAP",
    )
    world_bible_path_raw: str | None = Field(default=None, alias="ARES_WORLD_BIBLE_PATH")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def env_file_path(self) -> Path:
        return _ENV_FILE_PATH

    @property
    def env_file_candidates(self) -> tuple[Path, ...]:
        return _ENV_FILE_PATHS

    @property
    def world_bible_path(self) -> Path:
        if self.world_bible_path_raw:
            return Path(self.world_bible_path_raw).expanduser().resolve()

        candidates = _dedupe_paths(
            _PROJECT_ROOT / "world_bible.md",
            _BACKEND_ROOT / "world_bible.md",
            Path.cwd() / "world_bible.md",
            Path.cwd().parent / "world_bible.md",
            Path("/app/world_bible.md"),
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return candidates[0]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
