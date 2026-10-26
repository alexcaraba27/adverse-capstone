from sqlmodel import select

from app.models import Correction, HiringDecision, Void
from tests.conftest import payload


def test_void_appends_row(client, session):
    rid = client.post("/records", json=payload()).json()["id"]
    r = client.post(f"/records/{rid}/void", json={"reason": "duplicate", "actor_name": "Alex"})
    assert r.status_code == 200
    body = r.json()
    assert body["voided"] is True
    assert body["void"]["reason"] == "duplicate"

    assert session.get(HiringDecision, rid) is not None
    assert len(session.exec(select(Void).where(Void.record_id == rid)).all()) == 1


def test_double_void_409(client, session):
    rid = client.post("/records", json=payload()).json()["id"]
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})
    r = client.post(f"/records/{rid}/void", json={"reason": "r2", "actor_name": "a"})
    assert r.status_code == 409
    assert len(session.exec(select(Void).where(Void.record_id == rid)).all()) == 1


def test_correction_after_void_409(client, session):
    rid = client.post("/records", json=payload()).json()["id"]
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})
    r = client.patch(f"/records/{rid}", json={"decision": "hold", "reason": "r", "actor_name": "a"})
    assert r.status_code == 409
    assert len(session.exec(select(Correction).where(Correction.record_id == rid)).all()) == 0


def test_void_missing_fields(client):
    rid = client.post("/records", json=payload()).json()["id"]
    assert client.post(f"/records/{rid}/void", json={"reason": "r"}).status_code == 422


def test_voided_record_still_in_list_and_detail(client):
    rid = client.post("/records", json=payload()).json()["id"]
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})
    assert any(item["id"] == rid and item["voided"] for item in client.get("/records").json())
    assert client.get(f"/records/{rid}").json()["voided"] is True


def test_void_unknown_record(client):
    assert client.post("/records/nope/void", json={"reason": "r", "actor_name": "a"}).status_code == 404
