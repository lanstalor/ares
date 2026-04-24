from __future__ import annotations

from collections.abc import Collection

from sqlalchemy import Engine, inspect
from sqlalchemy.schema import MetaData

from app.core.config import get_settings
from app.db.session import engine
from app.models.base import Base


def _required_table_names(metadata: MetaData) -> Collection[str]:
    return tuple(metadata.tables.keys())


def database_has_required_tables(
    *,
    db_engine: Engine | None = None,
    metadata: MetaData | None = None,
) -> bool:
    target_engine = db_engine or engine
    target_metadata = metadata or Base.metadata
    required = set(_required_table_names(target_metadata))
    existing = set(inspect(target_engine).get_table_names())
    return required.issubset(existing)


def bootstrap_database(
    *,
    db_engine: Engine | None = None,
    metadata: MetaData | None = None,
    bootstrap_mode: str | None = None,
) -> None:
    target_engine = db_engine or engine
    target_metadata = metadata or Base.metadata
    mode = bootstrap_mode or get_settings().database_bootstrap

    if database_has_required_tables(db_engine=target_engine, metadata=target_metadata):
        return

    if mode != "create_all":
        raise RuntimeError(
            "Database schema is missing. Run migrations before startup or set "
            "ARES_DB_BOOTSTRAP=create_all for explicit development bootstrap."
        )

    # Alembic is not wired into this branch yet, so schema creation stays an explicit
    # bootstrap step instead of happening implicitly during API startup.
    target_metadata.create_all(bind=target_engine)


def ensure_database_ready(
    *,
    db_engine: Engine | None = None,
    metadata: MetaData | None = None,
) -> None:
    if database_has_required_tables(db_engine=db_engine, metadata=metadata):
        return

    raise RuntimeError(
        "Database schema is missing. Run `python -m app.db.bootstrap` before starting the API."
    )


def main() -> None:
    bootstrap_database()
    print(f"Database bootstrap complete using mode={get_settings().database_bootstrap}.")


if __name__ == "__main__":
    main()
