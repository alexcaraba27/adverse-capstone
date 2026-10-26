from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field as PField, model_validator
from sqlmodel import Field, SQLModel


class Decision(str, Enum):
    advance = "advance"
    reject = "reject"
    hold = "hold"


EDITABLE_FIELDS = ("job_role", "ai_tool", "decision", "decision_date", "reviewer_name")


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class HiringDecision(SQLModel, table=True):
    __tablename__ = "hiring_decisions"
    id: str = Field(default_factory=_uuid, primary_key=True)
    candidate_id: str
    job_role: str
    ai_tool: str
    decision: Decision
    decision_date: date
    reviewer_name: str
    created_at: datetime = Field(default_factory=_now)


class Correction(SQLModel, table=True):
    __tablename__ = "corrections"
    id: str = Field(default_factory=_uuid, primary_key=True)
    record_id: str = Field(foreign_key="hiring_decisions.id", index=True)
    job_role: Optional[str] = None
    ai_tool: Optional[str] = None
    decision: Optional[Decision] = None
    decision_date: Optional[date] = None
    reviewer_name: Optional[str] = None
    reason: str
    actor_name: str
    created_at: datetime = Field(default_factory=_now)


class Void(SQLModel, table=True):
    __tablename__ = "voids"
    id: str = Field(default_factory=_uuid, primary_key=True)
    record_id: str = Field(foreign_key="hiring_decisions.id", index=True)
    reason: str
    actor_name: str
    created_at: datetime = Field(default_factory=_now)


class HiringDecisionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str = PField(min_length=1)
    job_role: str = PField(min_length=1)
    ai_tool: str = PField(min_length=1)
    decision: Decision
    decision_date: date
    reviewer_name: str = PField(min_length=1)


class CorrectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_role: Optional[str] = PField(default=None, min_length=1)
    ai_tool: Optional[str] = PField(default=None, min_length=1)
    decision: Optional[Decision] = None
    decision_date: Optional[date] = None
    reviewer_name: Optional[str] = PField(default=None, min_length=1)
    reason: str = PField(min_length=1)
    actor_name: str = PField(min_length=1)

    @model_validator(mode="after")
    def _at_least_one_change(self):
        if not any(getattr(self, f) is not None for f in EDITABLE_FIELDS):
            raise ValueError("at least one editable field must be provided")
        return self


class VoidRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = PField(min_length=1)
    actor_name: str = PField(min_length=1)


class CorrectionEntry(BaseModel):
    id: str
    job_role: Optional[str]
    ai_tool: Optional[str]
    decision: Optional[Decision]
    decision_date: Optional[date]
    reviewer_name: Optional[str]
    reason: str
    actor_name: str
    created_at: datetime


class VoidEntry(BaseModel):
    id: str
    reason: str
    actor_name: str
    created_at: datetime


class CurrentValues(BaseModel):
    job_role: str
    ai_tool: str
    decision: Decision
    decision_date: date
    reviewer_name: str


class RecordListItem(BaseModel):
    id: str
    candidate_id: str
    created_at: datetime
    voided: bool
    current: CurrentValues


class RecordDetail(BaseModel):
    id: str
    candidate_id: str
    created_at: datetime
    original: CurrentValues
    corrections: list[CorrectionEntry]
    void: Optional[VoidEntry]
    current: CurrentValues
    voided: bool


class CreatedRecord(BaseModel):
    id: str
    candidate_id: str
    job_role: str
    ai_tool: str
    decision: Decision
    decision_date: date
    reviewer_name: str
    created_at: datetime
