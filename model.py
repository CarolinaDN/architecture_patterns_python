from datetime import date
from typing import Optional, Set
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class OrderLine(BaseModel):
    # Postel's Law - "Be liberal in what you accept, and conservative in what you emit"
    model_config = ConfigDict(frozen=True, extra="ignore")

    orderid: str
    sku: str
    qty: int = Field(gt=0)


class Batch(BaseModel):
    reference: str
    sku: str
    qty: int
    eta: Optional[date]
    _allocations: Set[OrderLine] =  PrivateAttr(default=set())

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
        return self.qty - self.allocated_quantity
