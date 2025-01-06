from datetime import date
from typing import List, Optional, Set
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class OrderLine(BaseModel):
    # OrderLine is a Value Object, should be immutable type. If they have different values, should be different objects.
    # Postel's Law - "Be liberal in what you accept, and conservative in what you emit".
    model_config = ConfigDict(frozen=True, extra="ignore")

    orderid: str
    sku: str
    qty: int = Field(gt=0)


class Batch(BaseModel):
    # Batch is an Entity, we can change their values and they are still recognizably the same thing.
    reference: str
    sku: str
    qty: int
    eta: Optional[date]
    _allocations: Set[OrderLine] =  PrivateAttr(default=set())

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
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

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.qty >= line.qty

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)
    
    def deallocate(self, line: OrderLine):
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


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
