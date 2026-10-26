from tests.conftest import payload


def test_list_empty(client):
    assert client.get("/records").json() == []


def test_list_filter_by_candidate(client):
    client.post("/records", json=payload(candidate_id="A"))
    client.post("/records", json=payload(candidate_id="B"))
    assert len(client.get("/records?candidate_id=A").json()) == 1
    assert client.get("/records?candidate_id=Z").json() == []


def test_detail_404(client):
    assert client.get("/records/does-not-exist").status_code == 404


def test_detail_includes_original_and_current(client):
    rid = client.post("/records", json=payload()).json()["id"]
    body = client.get(f"/records/{rid}").json()
    assert body["original"]["decision"] == "advance"
    assert body["current"]["decision"] == "advance"
    assert body["corrections"] == []
    assert body["void"] is None
    assert body["voided"] is False
