from app.models import HiringDecision
from tests.conftest import payload


def test_patch_single_field_leaves_original_untouched(client, session):
    rid = client.post("/records", json=payload()).json()["id"]
    r = client.patch(
        f"/records/{rid}",
        json={"decision": "reject", "reason": "manager override", "actor_name": "Alex C."},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["original"]["decision"] == "advance"
    assert body["current"]["decision"] == "reject"
    assert len(body["corrections"]) == 1

    row = session.get(HiringDecision, rid)
    assert row.decision.value == "advance"


def test_patch_missing_reason(client):
    rid = client.post("/records", json=payload()).json()["id"]
    r = client.patch(f"/records/{rid}", json={"decision": "reject", "actor_name": "A"})
    assert r.status_code == 422


def test_patch_missing_actor(client):
    rid = client.post("/records", json=payload()).json()["id"]
    r = client.patch(f"/records/{rid}", json={"decision": "reject", "reason": "r"})
    assert r.status_code == 422


def test_patch_rejects_candidate_id(client):
    rid = client.post("/records", json=payload()).json()["id"]
    r = client.patch(
        f"/records/{rid}",
        json={"candidate_id": "X", "reason": "r", "actor_name": "a"},
    )
    assert r.status_code == 422


def test_patch_rejects_id_and_created_at(client):
    rid = client.post("/records", json=payload()).json()["id"]
    assert client.patch(f"/records/{rid}", json={"id": "x", "reason": "r", "actor_name": "a"}).status_code == 422
    assert client.patch(
        f"/records/{rid}",
        json={"created_at": "1999-01-01T00:00:00", "reason": "r", "actor_name": "a"},
    ).status_code == 422


def test_patch_empty_change(client):
    rid = client.post("/records", json=payload()).json()["id"]
    r = client.patch(f"/records/{rid}", json={"reason": "r", "actor_name": "a"})
    assert r.status_code == 422


def test_patch_sequential_corrections(client):
    rid = client.post("/records", json=payload()).json()["id"]
    client.patch(f"/records/{rid}", json={"decision": "reject", "reason": "r1", "actor_name": "a"})
    client.patch(f"/records/{rid}", json={"job_role": "SWE III", "reason": "r2", "actor_name": "a"})
    body = client.get(f"/records/{rid}").json()
    assert body["current"]["decision"] == "reject"
    assert body["current"]["job_role"] == "SWE III"
    assert len(body["corrections"]) == 2


def test_patch_unknown_record(client):
    r = client.patch("/records/nope", json={"decision": "hold", "reason": "r", "actor_name": "a"})
    assert r.status_code == 404
