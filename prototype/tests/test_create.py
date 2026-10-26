import uuid

from tests.conftest import payload


def test_create_returns_201_with_server_fields(client):
    r = client.post("/records", json=payload())
    assert r.status_code == 201
    body = r.json()
    uuid.UUID(body["id"])
    assert body["created_at"]
    assert body["decision_date"] == "2026-10-20"
    assert body["created_at"] != "2026-10-20"


def test_create_rejects_missing_field(client):
    bad = payload()
    bad.pop("reviewer_name")
    assert client.post("/records", json=bad).status_code == 422


def test_create_rejects_bad_decision(client):
    assert client.post("/records", json=payload(decision="maybe")).status_code == 422


def test_create_rejects_client_supplied_id(client):
    bad = payload() | {"id": "attacker"}
    assert client.post("/records", json=bad).status_code == 422


def test_create_rejects_client_supplied_created_at(client):
    bad = payload() | {"created_at": "1999-01-01T00:00:00"}
    assert client.post("/records", json=bad).status_code == 422


def test_create_two_same_candidate_get_distinct_ids(client):
    a = client.post("/records", json=payload()).json()["id"]
    b = client.post("/records", json=payload()).json()["id"]
    assert a != b
