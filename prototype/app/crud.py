from datetime import date, datetime
from typing import Optional

from sqlmodel import Session, select

from app.models import (
    EDITABLE_FIELDS,
    Correction,
    CorrectionEntry,
    CorrectionRequest,
    CreatedRecord,
    CurrentValues,
    HiringDecision,
    HiringDecisionCreate,
    RecordDetail,
    RecordListItem,
    Void,
    VoidEntry,
    VoidRequest,
)


def create_record(session: Session, payload: HiringDecisionCreate) -> CreatedRecord:
    record = HiringDecision(**payload.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return CreatedRecord(
        id=record.id,
        candidate_id=record.candidate_id,
        job_role=record.job_role,
        ai_tool=record.ai_tool,
        decision=record.decision,
        decision_date=record.decision_date,
        reviewer_name=record.reviewer_name,
        created_at=record.created_at,
    )


def _current_values(record: HiringDecision, corrections: list[Correction]) -> CurrentValues:
    values = {f: getattr(record, f) for f in EDITABLE_FIELDS}
    for c in corrections:
        for f in EDITABLE_FIELDS:
            v = getattr(c, f)
            if v is not None:
                values[f] = v
    return CurrentValues(**values)


def _corrections_for(session: Session, record_id: str) -> list[Correction]:
    stmt = select(Correction).where(Correction.record_id == record_id).order_by(Correction.created_at)
    return list(session.exec(stmt).all())


def _void_for(session: Session, record_id: str) -> Optional[Void]:
    stmt = select(Void).where(Void.record_id == record_id).order_by(Void.created_at).limit(1)
    return session.exec(stmt).first()


def is_voided(session: Session, record_id: str) -> bool:
    return _void_for(session, record_id) is not None


def _original_values(record: HiringDecision) -> CurrentValues:
    return CurrentValues(**{f: getattr(record, f) for f in EDITABLE_FIELDS})


def list_records(session: Session, candidate_id: Optional[str]) -> list[RecordListItem]:
    stmt = select(HiringDecision).order_by(HiringDecision.created_at)
    if candidate_id is not None:
        stmt = stmt.where(HiringDecision.candidate_id == candidate_id)
    out: list[RecordListItem] = []
    for record in session.exec(stmt).all():
        corrections = _corrections_for(session, record.id)
        void = _void_for(session, record.id)
        out.append(
            RecordListItem(
                id=record.id,
                candidate_id=record.candidate_id,
                created_at=record.created_at,
                voided=void is not None,
                current=_current_values(record, corrections),
            )
        )
    return out


def get_record_detail(session: Session, record_id: str) -> Optional[RecordDetail]:
    record = session.get(HiringDecision, record_id)
    if record is None:
        return None
    corrections = _corrections_for(session, record_id)
    void = _void_for(session, record_id)
    return RecordDetail(
        id=record.id,
        candidate_id=record.candidate_id,
        created_at=record.created_at,
        original=_original_values(record),
        corrections=[
            CorrectionEntry(
                id=c.id,
                job_role=c.job_role,
                ai_tool=c.ai_tool,
                decision=c.decision,
                decision_date=c.decision_date,
                reviewer_name=c.reviewer_name,
                reason=c.reason,
                actor_name=c.actor_name,
                created_at=c.created_at,
            )
            for c in corrections
        ],
        void=(
            VoidEntry(id=void.id, reason=void.reason, actor_name=void.actor_name, created_at=void.created_at)
            if void is not None
            else None
        ),
        current=_current_values(record, corrections),
        voided=void is not None,
    )


class RecordNotFound(Exception):
    pass


class RecordVoided(Exception):
    pass


class AlreadyVoided(Exception):
    pass


def apply_correction(session: Session, record_id: str, req: CorrectionRequest) -> RecordDetail:
    record = session.get(HiringDecision, record_id)
    if record is None:
        raise RecordNotFound(record_id)
    if is_voided(session, record_id):
        raise RecordVoided(record_id)
    correction = Correction(
        record_id=record_id,
        job_role=req.job_role,
        ai_tool=req.ai_tool,
        decision=req.decision,
        decision_date=req.decision_date,
        reviewer_name=req.reviewer_name,
        reason=req.reason,
        actor_name=req.actor_name,
    )
    session.add(correction)
    session.commit()
    detail = get_record_detail(session, record_id)
    assert detail is not None
    return detail


def apply_void(session: Session, record_id: str, req: VoidRequest) -> RecordDetail:
    record = session.get(HiringDecision, record_id)
    if record is None:
        raise RecordNotFound(record_id)
    if is_voided(session, record_id):
        raise AlreadyVoided(record_id)
    void = Void(record_id=record_id, reason=req.reason, actor_name=req.actor_name)
    session.add(void)
    session.commit()
    detail = get_record_detail(session, record_id)
    assert detail is not None
    return detail
