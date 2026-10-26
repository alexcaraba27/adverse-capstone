from sqlmodel import SQLModel

from app.models import Decision, HiringDecision, Correction, Void  # noqa: F401


def test_decision_enum_members():
    assert {d.value for d in Decision} == {"advance", "reject", "hold"}


def test_tables_registered(session):
    names = set(SQLModel.metadata.tables.keys())
    assert {"hiring_decisions", "corrections", "voids"}.issubset(names)
