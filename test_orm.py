import model
from datetime import date
from sqlalchemy.sql import text
import pytest
import orm


def test_orderline_mapper_can_load_lines(session):
    data = [
            {"orderid": "order1", "sku": "RED-CHAIR", "qty": 12},
            {"orderid": "order1", "sku": "RED-TABLE", "qty": 13},
            {"orderid": "order2", "sku": "BLUE-LIPSTICK", "qty": 14}
        ]
    session.execute(text("INSERT INTO order_lines(orderid, sku, qty) VALUES(:orderid, :sku, :qty)"), data)

    expected = [
        model.OrderLine(orderid="order1", sku="RED-CHAIR", qty=12),
        model.OrderLine(orderid="order1", sku="RED-TABLE", qty=13),
        model.OrderLine(orderid="order2", sku="BLUE-LIPSTICK", qty=14),
    ]

    # Convert each ORM result to a Pydantic model
    query_result = session.query(orm.OrderLines).all()
    pydantic_results = [model.OrderLine.model_validate(batch) for batch in query_result]

    assert pydantic_results == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine(orderid="order1", sku="DECORATIVE-WIDGET", qty=12)
    session.add(orm.OrderLines(**new_line.model_dump()))
    session.commit()

    rows = list(session.execute(text('SELECT orderid, sku, qty FROM "order_lines"')))
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
        model.Batch(reference="batch1", sku="sku1", qty=100, eta=None),
        model.Batch(reference="batch2", sku="sku2", qty=200, eta=date(2011, 4, 11)),
    ]

    # Convert each ORM result to a Pydantic model
    query_result = session.query(orm.Batches).all()
    pydantic_results = [model.Batch.model_validate(batch) for batch in query_result]

    assert pydantic_results == expected


def test_saving_batches(session):
    batch = model.Batch(reference="batch1", sku="sku1", qty=100, eta=None)
    session.add(orm.Batches(**batch.model_dump()))
    session.commit()
    rows = session.execute(text(
        'SELECT reference, sku, qty, eta FROM "batches"'
    ))
    assert list(rows) == [("batch1", "sku1", 100, None)]


@pytest.mark.skip("Issue with relationships, to modify to sql model")
def test_saving_allocations(session):
    batch = model.Batch(reference="batch1", sku="sku1", qty=100, eta=None)
    line = model.OrderLine(orderid="order1", sku="sku1", qty=10)
    batch.allocate(line)
    session.add(orm.Batches(**batch.model_dump()))
    session.commit()
    rows = list(session.execute(text('SELECT orderline_id, batch_id FROM "allocations"')))
    print(rows)
    assert rows == [(line.orderid, batch.reference)]


@pytest.mark.skip("Issue with relationships, to modify to sql model")
def test_retrieving_allocations(session):
    session.execute(text(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES ("order1", "sku1", 12)'
    ))
    [[olid]] = session.execute(text(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="sku1"),
    )
    session.execute(text(
        "INSERT INTO batches (reference, sku, qty, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'
    ))
    [[bid]] = session.execute(text(
        "SELECT id FROM batches WHERE reference=:ref AND sku=:sku"),
        dict(ref="batch1", sku="sku1"),
    )
    session.execute(text(
        "INSERT INTO allocations (orderline_id, batch_id) VALUES (:olid, :bid)"),
        dict(olid=olid, bid=bid),
    )

    batch = session.query(orm.Batches).one()
    # Print the results 

    print("hereee", model.Batch.model_validate(batch).model_dump(include={"_allocations",}))

    assert batch._allocations == {model.OrderLine(orderid="order1", sku="sku1", qty=12)}
