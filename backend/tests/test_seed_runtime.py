from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.campaign import Campaign, Objective
from app.models.character import Character
from app.models.memory import Secret
from app.models.world import Area, Faction, LorePage, NPC, POI
from app.services.seed_runtime import seed_world_bible_into_campaign


WORLD_BIBLE_PATH = Path(__file__).resolve().parents[2] / "world_bible.md"


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_seed_runtime_imports_world_bible_into_database() -> None:
    session = _make_session()
    result = seed_world_bible_into_campaign(session, source_path=WORLD_BIBLE_PATH)

    assert result.factions_imported >= 15
    assert result.areas_imported >= 20
    assert result.pois_imported >= 15
    assert result.npcs_imported >= 8
    assert result.lore_pages_imported >= 5
    assert result.characters_imported == 1
    assert result.objectives_imported == 1
    assert result.secrets_imported >= 20

    assert session.scalar(select(Campaign)) is not None
    assert session.scalar(select(Character)) is not None
    assert session.scalar(select(Objective)) is not None
    assert session.scalar(select(Faction)) is not None
    assert session.scalar(select(Area)) is not None
    assert session.scalar(select(POI)) is not None
    assert session.scalar(select(NPC)) is not None
    assert session.scalar(select(LorePage)) is not None
    assert session.scalar(select(Secret)) is not None


def test_seed_runtime_reuses_global_world_entities_on_repeat_import() -> None:
    session = _make_session()
    first = seed_world_bible_into_campaign(session, source_path=WORLD_BIBLE_PATH, campaign_name_override="First")
    second = seed_world_bible_into_campaign(session, source_path=WORLD_BIBLE_PATH, campaign_name_override="Second")

    del first, second

    faction_count = len(session.scalars(select(Faction)).all())
    area_count = len(session.scalars(select(Area)).all())
    poi_count = len(session.scalars(select(POI)).all())
    npc_count = len(session.scalars(select(NPC)).all())
    lore_count = len(session.scalars(select(LorePage)).all())
    campaign_count = len(session.scalars(select(Campaign)).all())

    assert campaign_count == 2
    assert faction_count >= 15
    assert faction_count < 30
    assert area_count >= 20
    assert area_count < 50
    assert poi_count >= 15
    assert poi_count < 50
    assert npc_count >= 8
    assert npc_count < 20
    assert lore_count >= 5
    assert lore_count < 20
