import abc
import model
import orm
from sqlmodel import col, select


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(orm.Batches(**batch.model_dump()))

    def get(self, reference):
        batch = self.session.exec(select(orm.Batches).where(orm.Batches.reference==reference)).one()
        return model.Batch.model_validate(batch)

    def list(self):
        return self.session.exec(select(orm.Batches)).all()
