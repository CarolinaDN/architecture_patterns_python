import pytest
from sqlmodel import SQLModel, Session, create_engine
import orm


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    return engine


@pytest.fixture
def session(in_memory_db):
    SQLModel.metadata.create_all(in_memory_db)
    with Session(in_memory_db) as session:
        yield session
