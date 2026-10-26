import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session):
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def payload(**over):
    base = {
        "candidate_id": "C1",
        "job_role": "SWE II",
        "ai_tool": "ResumeRanker v3",
        "decision": "advance",
        "decision_date": "2026-10-20",
        "reviewer_name": "Alex C.",
    }
    base.update(over)
    return base
