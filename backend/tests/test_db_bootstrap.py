from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.db.bootstrap import bootstrap_database, database_has_required_tables, ensure_database_ready
from app.models.base import Base


def test_bootstrap_database_creates_tables_when_enabled(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'ares.db'}", future=True)

    bootstrap_database(
        db_engine=engine,
        metadata=Base.metadata,
        bootstrap_mode="create_all",
    )

    assert database_has_required_tables(db_engine=engine, metadata=Base.metadata)


def test_bootstrap_database_raises_when_disabled(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'ares.db'}", future=True)

    with pytest.raises(RuntimeError, match="ARES_DB_BOOTSTRAP=create_all"):
        bootstrap_database(
            db_engine=engine,
            metadata=Base.metadata,
            bootstrap_mode="disabled",
        )


def test_ensure_database_ready_raises_when_tables_are_missing(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'ares.db'}", future=True)

    with pytest.raises(RuntimeError, match="python -m app.db.bootstrap"):
        ensure_database_ready(db_engine=engine, metadata=Base.metadata)
