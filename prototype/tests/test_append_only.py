from sqlmodel import select

from app.models import Correction, HiringDecision, Void
from tests.conftest import payload


def test_full_sequence_preserves_original_row_values(client, session):
    created = client.post("/records", json=payload(decision="advance")).json()
    rid = created["id"]
    client.patch(f"/records/{rid}", json={"decision": "reject", "reason": "r1", "actor_name": "a"})
    client.patch(f"/records/{rid}", json={"job_role": "SWE III", "reason": "r2", "actor_name": "a"})
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})

    rows = session.exec(select(HiringDecision)).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.id == rid
    assert row.decision.value == "advance"
    assert row.job_role == "SWE II"
    assert row.ai_tool == "ResumeRanker v3"
    assert row.decision_date.isoformat() == "2026-10-20"
    assert row.reviewer_name == "Alex C."

    assert len(session.exec(select(Correction).where(Correction.record_id == rid)).all()) == 2
    assert len(session.exec(select(Void).where(Void.record_id == rid)).all()) == 1
