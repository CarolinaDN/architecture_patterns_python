from datetime import date, timedelta
import pytest

from model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


# Could use parametrize to be cleaner

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch(reference="batch-001", sku="SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine(orderid="order1", sku="SMALL-TABLE", qty=2)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch = Batch(reference="batch-001", sku="SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine(orderid="order1", sku="SMALL-TABLE", qty=2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch(reference="batch-001", sku="SMALL-TABLE", qty=2, eta=date.today())
    line = OrderLine(orderid="order1", sku="SMALL-TABLE", qty=20)
    assert not batch.can_allocate(line)


def test_can_allocate_if_available_equal_to_required():
    batch = Batch(reference="batch-001", sku="SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine(orderid="order1", sku="SMALL-TABLE", qty=20)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch(reference="batch-001", sku="SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine(orderid="order1", sku="BIG-TABLE", qty=20)
    assert not batch.can_allocate(line)


def test_can_only_deallocate_allocated_lines():
    """Asserting that deallocating a line from a batch has no effect unless the batch was previously allocated."""
    batch = Batch(reference="batch-001", sku="SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine(orderid="order1", sku="SMALL-TABLE", qty=2)
    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch = Batch(reference="batch-001", sku="SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine(orderid="order1", sku="SMALL-TABLE", qty=2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


# def test_prefers_warehouse_batches_to_shipments():
#     pytest.fail("todo")


# def test_prefers_earlier_batches():
#     pytest.fail("todo")
