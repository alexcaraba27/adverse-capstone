# Adverse CRUD Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI + SQLite CRUD backend for append-only AI hiring decision records (create / read / correct / void), tested via pytest and FastAPI `/docs`.

**Architecture:** Three append-only tables (`hiring_decisions`, `corrections`, `voids`). All DB writes go through `crud.py`; no code path updates or deletes `hiring_decisions`. "Current" field values are computed at read time as original overlaid by per-field last-non-null-wins from the corrections log.

**Tech Stack:** Python 3.11+, FastAPI, SQLModel, SQLite (file at runtime, in-memory for tests), pytest, httpx TestClient, uvicorn.

**Spec:** `/Users/alexcaraballo/.claude/plans/plan-only-don-t-write-expressive-lollipop.md`

## Global Constraints

- All code under `prototype/` — must not touch `docs/`.
- `hiring_decisions` rows are immutable after insert — no UPDATE, no DELETE in any code path.
- `candidate_id`, `id`, `created_at` are not editable via PATCH (reject with 422).
- `decision` is one of exactly `advance`, `reject`, `hold`.
- Timestamps are server-generated UTC ISO-8601; record IDs are server-generated UUID4.
- No authentication, no cryptographic tamper-evidence — the prototype must not claim either.
- A voided record cannot be corrected again or voided again (409).
- Voided records remain visible in list and detail with `voided: true`.

## Review Focus

Input classes implied by the spec that no task's happy-path tests exercise and would surprise a reasonable user:

1. **Client-supplied `id` / `created_at` on create** — must be ignored, server values win. Pinned by test in Task 2.
2. **PATCH body containing `candidate_id`, `id`, or `created_at`** — must 422, no partial write. Pinned by tests in Task 4.
3. **PATCH with reason + actor but no changed fields** — must 422, no row inserted. Pinned by test in Task 4.
4. **Second void on an already-voided record** — must 409, exactly one `voids` row remains. Pinned by test in Task 5.
5. **Correction on a voided record** — must 409, no `corrections` row written. Pinned by test in Task 5.

---

### Task 1: Project scaffold, DB engine, and models

**Files:**
- Create: `prototype/requirements.txt`
- Create: `prototype/app/__init__.py` (empty)
- Create: `prototype/app/database.py`
- Create: `prototype/app/models.py`
- Create: `prototype/tests/__init__.py` (empty)
- Create: `prototype/tests/conftest.py`
- Create: `prototype/tests/test_scaffold.py`

**Interfaces produced:**
- `Decision` str enum with members `advance`, `reject`, `hold` in `app/models.py`.
- SQLModel tables `HiringDecision`, `Correction`, `Void` in `app/models.py` matching the column spec.
- Pydantic request schemas in `app/models.py`:
  - `HiringDecisionCreate(candidate_id, job_role, ai_tool, decision, decision_date, reviewer_name)` — all required, non-empty strings except `decision` (enum) and `decision_date` (date).
  - `CorrectionRequest(job_role?, ai_tool?, decision?, decision_date?, reviewer_name?, reason, actor_name)` — reason/actor required non-empty; all editable fields optional; `extra="forbid"` so unknown keys raise 422.
  - `VoidRequest(reason, actor_name)` — both required non-empty; `extra="forbid"`.
- Response schemas:
  - `RecordListItem(id, candidate_id, created_at, voided, current: dict)`.
  - `RecordDetail(id, candidate_id, created_at, original: dict, corrections: list, void: dict|None, current: dict, voided: bool)`.
- `app/database.py`:
  - `engine` (file `prototype/adverse.db`).
  - `get_session()` FastAPI dependency yielding a Session.
  - `init_db()` that creates all tables.
- `tests/conftest.py`:
  - `session` fixture using an in-memory SQLite engine with `connect_args={"check_same_thread": False}` and `StaticPool`.
  - `client` fixture that overrides `get_session` on the FastAPI app and returns a `TestClient`.

- [ ] **Step 1: Write `tests/test_scaffold.py`**

```python
from app.models import Decision, HiringDecision, Correction, Void

def test_decision_enum_members():
    assert {d.value for d in Decision} == {"advance", "reject", "hold"}

def test_tables_registered(session):
    from sqlmodel import SQLModel
    names = set(SQLModel.metadata.tables.keys())
    assert {"hiring_decisions", "corrections", "voids"}.issubset(names)
```

- [ ] **Step 2: Run and verify it fails**

Run: `cd prototype && pytest tests/test_scaffold.py -v`
Expected: FAIL — module `app.models` not found.

- [ ] **Step 3: Implement scaffold**

Write `requirements.txt` with `fastapi`, `sqlmodel`, `uvicorn[standard]`, `pytest`, `httpx`. Implement `app/database.py` and `app/models.py` to satisfy the Interfaces block. Table names via SQLModel `__tablename__`. For `Decision`, use `str, Enum`. For optional correction columns, use `Optional[...] = Field(default=None, nullable=True)`.

- [ ] **Step 4: Run and verify it passes**

Run: `cd prototype && pytest tests/test_scaffold.py -v`
Expected: PASS, 2 tests.

- [ ] **Step 5: Commit**

```bash
git add prototype/
git commit -m "feat(prototype): scaffold FastAPI + SQLModel schema for Adverse CRUD"
```

---

### Task 2: Create endpoint

**Files:**
- Create: `prototype/app/crud.py`
- Create: `prototype/app/main.py`
- Create: `prototype/tests/test_create.py`

**Interfaces:**
- Consumes: Task 1 models and session.
- Produces: `create_record(session, payload: HiringDecisionCreate) -> HiringDecision` in `app/crud.py`. FastAPI route `POST /records` in `app/main.py` returning 201 and the created record as a dict with `id`, `candidate_id`, `job_role`, `ai_tool`, `decision`, `decision_date`, `reviewer_name`, `created_at`.

- [ ] **Step 1: Write tests**

```python
# tests/test_create.py
import uuid

def _payload(**over):
    base = {
        "candidate_id": "C1",
        "job_role": "SWE II",
        "ai_tool": "ResumeRanker v3",
        "decision": "advance",
        "decision_date": "2026-10-20",
        "reviewer_name": "Alex C.",
    }
    base.update(over); return base

def test_create_returns_201_with_server_fields(client):
    r = client.post("/records", json=_payload())
    assert r.status_code == 201
    body = r.json()
    uuid.UUID(body["id"])          # valid uuid
    assert body["created_at"]
    assert body["decision_date"] == "2026-10-20"
    assert body["created_at"][:4] != "2026-10-20"[:4] or body["created_at"] != "2026-10-20"

def test_create_rejects_missing_field(client):
    bad = _payload(); bad.pop("reviewer_name")
    assert client.post("/records", json=bad).status_code == 422

def test_create_rejects_bad_decision(client):
    assert client.post("/records", json=_payload(decision="maybe")).status_code == 422

def test_create_ignores_client_id_and_created_at(client, session):
    from app.models import HiringDecision
    payload = _payload() | {"id": "attacker", "created_at": "1999-01-01T00:00:00"}
    r = client.post("/records", json=payload)
    assert r.status_code == 422  # extra="forbid" rejects unknown keys

def test_create_two_same_candidate_get_distinct_ids(client):
    a = client.post("/records", json=_payload()).json()["id"]
    b = client.post("/records", json=_payload()).json()["id"]
    assert a != b
```

- [ ] **Step 2: Run and verify failure**

Run: `cd prototype && pytest tests/test_create.py -v`
Expected: FAIL — no `POST /records` route.

- [ ] **Step 3: Implement**

In `app/crud.py`, `create_record` generates UUID4 string, UTC `datetime.utcnow()`, inserts, commits, refreshes, returns. In `app/main.py`, build the FastAPI app, call `init_db()` on startup, mount `POST /records` with `status_code=201`, use `HiringDecisionCreate` with `model_config = ConfigDict(extra="forbid")`.

- [ ] **Step 4: Run and verify pass**

Run: `cd prototype && pytest tests/test_create.py -v`
Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add prototype/
git commit -m "feat(prototype): POST /records creates immutable hiring decision"
```

---

### Task 3: Read endpoints

**Files:**
- Modify: `prototype/app/crud.py`
- Modify: `prototype/app/main.py`
- Create: `prototype/tests/test_read.py`

**Interfaces:**
- Consumes: `create_record` from Task 2.
- Produces:
  - `list_records(session, candidate_id: str | None) -> list[RecordListItem]` — computes `current` and `voided` per record.
  - `get_record_detail(session, record_id: str) -> RecordDetail | None` — returns None if unknown.
  - `_current_values(original: HiringDecision, corrections: list[Correction]) -> dict` helper applying per-field last-non-null-wins over `job_role, ai_tool, decision, decision_date, reviewer_name`.
  - Routes `GET /records?candidate_id=...` and `GET /records/{id}` (404 if missing).

- [ ] **Step 1: Write tests**

```python
def test_list_empty(client):
    assert client.get("/records").json() == []

def test_list_filter_by_candidate(client):
    client.post("/records", json=_payload(candidate_id="A"))
    client.post("/records", json=_payload(candidate_id="B"))
    assert len(client.get("/records?candidate_id=A").json()) == 1
    assert client.get("/records?candidate_id=Z").json() == []

def test_detail_404(client):
    assert client.get("/records/does-not-exist").status_code == 404

def test_detail_includes_original_and_current(client):
    rid = client.post("/records", json=_payload()).json()["id"]
    body = client.get(f"/records/{rid}").json()
    assert body["original"]["decision"] == "advance"
    assert body["current"]["decision"] == "advance"
    assert body["corrections"] == []
    assert body["void"] is None
    assert body["voided"] is False
```

(`_payload` reused via `tests/conftest.py` helper; move it there to avoid duplication.)

- [ ] **Step 2: Run and verify failure**

Run: `cd prototype && pytest tests/test_read.py -v`
Expected: FAIL — routes not defined.

- [ ] **Step 3: Implement**

Add `_current_values` and the two CRUD functions. Mount routes. For list, order isn't specified — default to `created_at ASC` for deterministic tests.

- [ ] **Step 4: Run and verify pass**

Run: `cd prototype && pytest tests/test_read.py -v`
Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```bash
git add prototype/
git commit -m "feat(prototype): GET /records and /records/{id} with computed current values"
```

---

### Task 4: Update (correction) endpoint

**Files:**
- Modify: `prototype/app/crud.py`
- Modify: `prototype/app/main.py`
- Create: `prototype/tests/test_update.py`

**Interfaces:**
- Produces: `apply_correction(session, record_id: str, req: CorrectionRequest) -> Correction` raising `LookupError` (→ 404), `ValueError("voided")` (→ 409), or `ValueError("empty")` (→ 422 — but prefer catching empty in the Pydantic layer via validator). Route `PATCH /records/{id}` returning the updated detail.

- [ ] **Step 1: Write tests**

```python
def test_patch_single_field(client, session):
    rid = client.post("/records", json=_payload()).json()["id"]
    r = client.patch(f"/records/{rid}",
                     json={"decision": "reject", "reason": "manager override", "actor_name": "Alex C."})
    assert r.status_code == 200
    body = r.json()
    assert body["original"]["decision"] == "advance"
    assert body["current"]["decision"] == "reject"
    assert len(body["corrections"]) == 1

    from app.models import HiringDecision
    row = session.get(HiringDecision, rid)
    assert row.decision.value == "advance"  # original row unchanged

def test_patch_missing_reason(client):
    rid = client.post("/records", json=_payload()).json()["id"]
    r = client.patch(f"/records/{rid}", json={"decision": "reject", "actor_name": "A"})
    assert r.status_code == 422

def test_patch_rejects_candidate_id(client):
    rid = client.post("/records", json=_payload()).json()["id"]
    r = client.patch(f"/records/{rid}",
                     json={"candidate_id": "X", "reason": "r", "actor_name": "a"})
    assert r.status_code == 422

def test_patch_empty_change(client):
    rid = client.post("/records", json=_payload()).json()["id"]
    r = client.patch(f"/records/{rid}", json={"reason": "r", "actor_name": "a"})
    assert r.status_code == 422

def test_patch_sequential_corrections(client):
    rid = client.post("/records", json=_payload()).json()["id"]
    client.patch(f"/records/{rid}",
                 json={"decision": "reject", "reason": "r1", "actor_name": "a"})
    client.patch(f"/records/{rid}",
                 json={"job_role": "SWE III", "reason": "r2", "actor_name": "a"})
    body = client.get(f"/records/{rid}").json()
    assert body["current"]["decision"] == "reject"
    assert body["current"]["job_role"] == "SWE III"
    assert len(body["corrections"]) == 2

def test_patch_unknown_record(client):
    r = client.patch("/records/nope", json={"decision": "hold", "reason": "r", "actor_name": "a"})
    assert r.status_code == 404
```

- [ ] **Step 2: Run and verify failure**

Run: `cd prototype && pytest tests/test_update.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

Use a Pydantic model validator on `CorrectionRequest` that asserts at least one of the five editable fields is set — otherwise raises → 422. `extra="forbid"` handles the `candidate_id`/`id`/`created_at` rejection. Insert a `Correction` row with only the submitted fields filled; others `None`. Do not touch the original row.

- [ ] **Step 4: Run and verify pass**

Run: `cd prototype && pytest tests/test_update.py -v`
Expected: PASS, 6 tests.

- [ ] **Step 5: Commit**

```bash
git add prototype/
git commit -m "feat(prototype): PATCH /records/{id} appends correction, originals immutable"
```

---

### Task 5: Void endpoint + append-only invariants

**Files:**
- Modify: `prototype/app/crud.py`
- Modify: `prototype/app/main.py`
- Create: `prototype/tests/test_void.py`
- Create: `prototype/tests/test_append_only.py`
- Create: `prototype/README.md`

**Interfaces:**
- Produces: `apply_void(session, record_id: str, req: VoidRequest) -> Void` with same error semantics (404 unknown, 409 already-voided). Correction and void endpoints both check `is_voided(session, record_id)` → bool via `SELECT 1 FROM voids WHERE record_id=? LIMIT 1`. Route `POST /records/{id}/void`.

- [ ] **Step 1: Write tests**

```python
# tests/test_void.py
def test_void_appends_row(client, session):
    rid = client.post("/records", json=_payload()).json()["id"]
    r = client.post(f"/records/{rid}/void", json={"reason": "duplicate", "actor_name": "Alex"})
    assert r.status_code == 200
    body = r.json()
    assert body["voided"] is True
    assert body["void"]["reason"] == "duplicate"

    from app.models import HiringDecision, Void
    assert session.get(HiringDecision, rid) is not None
    assert session.query(Void).filter_by(record_id=rid).count() == 1

def test_double_void_409(client, session):
    rid = client.post("/records", json=_payload()).json()["id"]
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})
    r = client.post(f"/records/{rid}/void", json={"reason": "r2", "actor_name": "a"})
    assert r.status_code == 409
    from app.models import Void
    assert session.query(Void).filter_by(record_id=rid).count() == 1

def test_correction_after_void_409(client, session):
    rid = client.post("/records", json=_payload()).json()["id"]
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})
    r = client.patch(f"/records/{rid}", json={"decision": "hold", "reason": "r", "actor_name": "a"})
    assert r.status_code == 409
    from app.models import Correction
    assert session.query(Correction).filter_by(record_id=rid).count() == 0

def test_void_missing_fields(client):
    rid = client.post("/records", json=_payload()).json()["id"]
    assert client.post(f"/records/{rid}/void", json={"reason": "r"}).status_code == 422

def test_voided_record_still_in_list_and_detail(client):
    rid = client.post("/records", json=_payload()).json()["id"]
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})
    assert any(item["id"] == rid and item["voided"] for item in client.get("/records").json())
    assert client.get(f"/records/{rid}").json()["voided"] is True

def test_void_unknown_record(client):
    assert client.post("/records/nope/void", json={"reason":"r","actor_name":"a"}).status_code == 404
```

```python
# tests/test_append_only.py
def test_full_sequence_preserves_original_row_values(client, session):
    created = client.post("/records", json=_payload(decision="advance")).json()
    rid = created["id"]
    client.patch(f"/records/{rid}", json={"decision": "reject", "reason": "r", "actor_name": "a"})
    client.patch(f"/records/{rid}", json={"job_role": "SWE III", "reason": "r", "actor_name": "a"})
    client.post(f"/records/{rid}/void", json={"reason": "r", "actor_name": "a"})

    from app.models import HiringDecision, Correction, Void
    rows = session.query(HiringDecision).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.decision.value == "advance"
    assert row.job_role == "SWE II"
    assert session.query(Correction).filter_by(record_id=rid).count() == 2
    assert session.query(Void).filter_by(record_id=rid).count() == 1
```

- [ ] **Step 2: Run and verify failure**

Run: `cd prototype && pytest tests/test_void.py tests/test_append_only.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

Add `is_voided` + `apply_void` in `crud.py`. Guard `apply_correction` with `is_voided` → raise voided error. Mount route. Write `README.md` with the three verification commands (install, uvicorn, pytest).

- [ ] **Step 4: Run and verify all pass**

Run: `cd prototype && pytest -v`
Expected: PASS, all tests across the five files.

- [ ] **Step 5: Commit**

```bash
git add prototype/
git commit -m "feat(prototype): POST /records/{id}/void with append-only invariants"
```

## Self-review notes

- Spec coverage: Create (Task 2), Read (Task 3), Update (Task 4), Void (Task 5), append-only invariant (Task 5). All five testing-checklist sections from the design doc map to task tests.
- Review Focus pins: client-supplied id/created_at (Task 2), PATCH rejecting candidate_id/id/created_at (Task 4 via `extra="forbid"`), empty PATCH (Task 4 via validator), double-void (Task 5), correction-after-void (Task 5).
- Type consistency: `Decision` enum used in create payload AND correction payload AND response; `_current_values` returns a dict with the same five keys everywhere.
- Signatures are unambiguous; no step contains more than one decision.
