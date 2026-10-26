# Adverse CRUD Prototype

Minimal FastAPI + SQLite backend for AI hiring decision records.
Append-only data model: originals and correction history survive every edit.

**Not production:** no authentication, no cryptographic tamper-evidence,
no retention policy. Reviewer and actor names are typed strings, not
verified identities.

## Run

```bash
cd prototype
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the Swagger UI.

## Test

```bash
cd prototype
. .venv/bin/activate
pytest -v
```
