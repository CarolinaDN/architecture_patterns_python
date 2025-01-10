from datetime import date
from sqlalchemy.sql import text
from sqlmodel import select
import pytest
import orm


def test_orderline_mapper_can_load_lines(session):
    data = [
            {"orderid": "order1", "sku": "RED-CHAIR", "qty": 12},
            {"orderid": "order1", "sku": "RED-TABLE", "qty": 13},
            {"orderid": "order2", "sku": "BLUE-LIPSTICK", "qty": 14}
        ]
    session.execute(text("INSERT INTO orderline(orderid, sku, qty) VALUES(:orderid, :sku, :qty)"), data)

    expected = [
        orm.OrderLine(id=1, orderid="order1", sku="RED-CHAIR", qty=12),
        orm.OrderLine(id=2, orderid="order1", sku="RED-TABLE", qty=13),
        orm.OrderLine(id=3, orderid="order2", sku="BLUE-LIPSTICK", qty=14),
    ]

    result = session.exec(select(orm.OrderLine)).all()

    assert result == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = orm.OrderLine(orderid="order1", sku="DECORATIVE-WIDGET", qty=12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT orderid, sku, qty FROM "orderline"')))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


def test_retrieving_batches(session):
    session.execute(text(
        "INSERT INTO batches (reference, sku, qty, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'))
    session.execute(text(
        "INSERT INTO batches (reference, sku, qty, eta)"
        ' VALUES ("batch2", "sku2", 200, "2011-04-11")'
    ))
    expected = [
        orm.Batches(reference="batch1", sku="sku1", qty=100, eta=None),
        orm.Batches(reference="batch2", sku="sku2", qty=200, eta=date(2011, 4, 11)),
    ]

    # Convert each ORM result to a Pydantic model
    query_result = session.exec(select(orm.Batches)).all()
    pydantic_results = [orm.Batches.model_validate(batch) for batch in query_result]

    assert pydantic_results == expected


def test_saving_batches(session):
    batch = orm.Batches(reference="batch1", sku="sku1", qty=100, eta=None)
    session.add(batch)
    session.commit()
    rows = session.execute(text(
        'SELECT reference, sku, qty, eta FROM "batches"'
    ))
    assert list(rows) == [("batch1", "sku1", 100, None)]


def test_saving_allocations(session):
    batch = orm.Batches(reference="batch1", sku="sku1", qty=100, eta=None)
    line = orm.OrderLineBase(orderid="order1", sku="sku1", qty=10)
    batch.allocate(line)
    session.add(batch)
    session.commit()

    order_line = orm.OrderLine(**list(batch._allocations)[0].model_dump())
    session.add(order_line)
    session.exec(select(orm.Batches)).one().allocations.append(order_line)
    rows = list(session.exec(select(orm.AllocationsLink.orderline_id, orm.AllocationsLink.batch_id)).all())
    assert rows == [(line.orderid, batch.reference)]

