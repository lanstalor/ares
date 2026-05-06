import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.campaign import Campaign
from app.models.character import Character, Item
from app.services.consequence_applier import Consequences, InventoryUpdate, apply_consequences

def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()

@pytest.fixture
def session():
    db = _make_session()
    try:
        yield db
    finally:
        db.close()

def test_inventory_update_add_new_item(session):
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    char = Character(campaign_id=campaign.id, name="Davan")
    session.add(char)
    session.commit()

    consequences = Consequences(
        inventory_updates=[
            InventoryUpdate(name="Stun Baton", action="add", quantity=1, tags="weapon, shock")
        ]
    )

    apply_consequences(session, campaign, consequences)
    session.commit()

    item = session.query(Item).filter_by(name="Stun Baton").first()
    assert item is not None
    assert item.quantity == 1
    assert item.tags == "weapon, shock"


def test_inventory_update_add_existing_item(session):
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    char = Character(campaign_id=campaign.id, name="Davan")
    session.add(char)
    session.flush()

    item = Item(campaign_id=campaign.id, character_id=char.id, name="Credit Chit", quantity=100)
    session.add(item)
    session.commit()

    consequences = Consequences(
        inventory_updates=[
            InventoryUpdate(name="Credit Chit", action="add", quantity=50)
        ]
    )

    apply_consequences(session, campaign, consequences)
    session.commit()

    updated_item = session.query(Item).filter_by(name="Credit Chit").first()
    assert updated_item.quantity == 150


def test_inventory_update_remove_item(session):
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    char = Character(campaign_id=campaign.id, name="Davan")
    session.add(char)
    session.flush()

    item = Item(campaign_id=campaign.id, character_id=char.id, name="Medkit", quantity=2)
    session.add(item)
    session.commit()

    consequences = Consequences(
        inventory_updates=[
            InventoryUpdate(name="Medkit", action="remove", quantity=1)
        ]
    )

    apply_consequences(session, campaign, consequences)
    session.commit()

    updated_item = session.query(Item).filter_by(name="Medkit").first()
    assert updated_item is not None
    assert updated_item.quantity == 1

    # Remove the last one
    consequences = Consequences(
        inventory_updates=[
            InventoryUpdate(name="Medkit", action="remove")
        ]
    )
    apply_consequences(session, campaign, consequences)
    session.commit()

    deleted_item = session.query(Item).filter_by(name="Medkit").first()
    assert deleted_item is None
