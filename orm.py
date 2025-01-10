# ORM created using sqlmodel, uses pydantic and sqlalchemy in the background, does not depend on model
from datetime import date
from pydantic import BaseModel, ConfigDict, PrivateAttr
from sqlmodel import Field, Relationship, SQLModel, String
from typing import List, Optional


class AllocationsLink(SQLModel, table=True):
    orderline_id: Optional[int] = Field(
        default=None, foreign_key="orderline.orderid", primary_key=True
    )
    batch_id: Optional[int] = Field(
        default=None, foreign_key="batches.reference", primary_key=True
    )


class OrderLineBase(BaseModel):
    # OrderLine is a Value Object, should be immutable type. If they have different values, should be different objects.
    # Postel's Law - "Be liberal in what you accept, and conservative in what you emit".
    model_config = ConfigDict(from_attributes=True, frozen=True, extra="ignore")

    orderid: str
    sku: str
    qty: int


class OrderLine(SQLModel, BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    orderid: str
    sku: str
    qty: int = Field(gt=0)

    batch: list["Batches"] = Relationship(
        back_populates="allocations", link_model=AllocationsLink)


class Batches(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str = Field(String(255), unique=True)
    sku: str
    qty: int = Field(nullable=False)
    eta: Optional[date] = Field(nullable=True)
    _allocations: set[OrderLineBase] =  PrivateAttr(default=set())
    # allocations_id: Optional[int] = Field(default=None, foreign_key="orderline.id") 

    allocations: list[OrderLine] = Relationship(
        back_populates="batch", link_model=AllocationsLink)

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batches):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)
    
    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def can_allocate(self, line: OrderLineBase) -> bool:
            return self.sku == line.sku and self.qty >= line.qty

    def allocate(self, line: OrderLineBase):
        if self.can_allocate(line):
            self._allocations.add(line)
    
    def deallocate(self, line: OrderLineBase):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)
    
    @property
    def available_quantity(self) -> int:
        self.qty = self.qty - self.allocated_quantity
        return self.qty


class OutOfStock(Exception):
    pass


def allocate(line: OrderLineBase, batches: List[Batches]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
