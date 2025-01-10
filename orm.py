# ORM depends on model
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()

class OrderLines(Base):
    __tablename__ = 'order_lines'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    orderid: Mapped[str] = mapped_column(String(255))
    sku: Mapped[str]
    qty: Mapped[int] = mapped_column(nullable=False)


class Batches(Base):
    __tablename__ = 'batches'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(255))
    sku: Mapped[str]
    qty: Mapped[int] = mapped_column(nullable=False)
    eta = mapped_column(Date, nullable=True)


class Allocations(Base):
    __tablename__ = 'allocations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    orderline_id: Mapped[int] = mapped_column(ForeignKey("order_lines.id"))
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
