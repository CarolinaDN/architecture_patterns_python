import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import Base


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    return engine


@pytest.fixture
def session(in_memory_db):
    db = sessionmaker(autocommit=False, autoflush=False,bind=in_memory_db)()
    Base.metadata.create_all(in_memory_db)
    try:
        yield db
    finally:
        db.close()
