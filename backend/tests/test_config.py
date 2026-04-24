from pathlib import Path

from app.core.config import discover_env_file_path, discover_env_file_paths


def test_discover_env_file_prefers_repo_root(tmp_path: Path) -> None:
    repo_root = tmp_path / "ares"
    backend_root = repo_root / "backend"
    repo_root.mkdir()
    backend_root.mkdir()

    repo_env = repo_root / ".env"
    repo_env.write_text("ARES_GENERATION_PROVIDER=stub\n", encoding="utf-8")
    (backend_root / ".env").write_text("ARES_GENERATION_PROVIDER=anthropic\n", encoding="utf-8")

    discovered = discover_env_file_path(
        app_root=repo_root,
        backend_root=backend_root,
    )

    assert discovered == repo_env.resolve()


def test_discover_env_file_falls_back_to_repo_root_when_missing(tmp_path: Path) -> None:
    repo_root = tmp_path / "ares"
    backend_root = repo_root / "backend"
    backend_root.mkdir(parents=True)

    discovered = discover_env_file_path(
        app_root=repo_root,
        backend_root=backend_root,
    )

    assert discovered == (repo_root / ".env").resolve()


def test_discover_env_file_candidates_are_explicit_and_stable(tmp_path: Path) -> None:
    repo_root = tmp_path / "ares"
    backend_root = repo_root / "backend"
    backend_root.mkdir(parents=True)

    discovered = discover_env_file_paths(
        app_root=repo_root,
        backend_root=backend_root,
    )

    assert discovered == (
        (repo_root / ".env").resolve(),
        (backend_root / ".env").resolve(),
    )
