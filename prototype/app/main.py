from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlmodel import Session

from app import crud
from app.database import get_session, init_db
from app.models import (
    CorrectionRequest,
    CreatedRecord,
    HiringDecisionCreate,
    RecordDetail,
    RecordListItem,
    VoidRequest,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Adverse",
    description="AI hiring decision records (prototype). No authentication; no cryptographic tamper-evidence.",
    lifespan=lifespan,
)


@app.post("/records", status_code=201, response_model=CreatedRecord)
def create_record(payload: HiringDecisionCreate, session: Session = Depends(get_session)) -> CreatedRecord:
    return crud.create_record(session, payload)


@app.get("/records", response_model=list[RecordListItem])
def list_records(
    candidate_id: Optional[str] = None,
    session: Session = Depends(get_session),
) -> list[RecordListItem]:
    return crud.list_records(session, candidate_id)


@app.get("/records/{record_id}", response_model=RecordDetail)
def get_record(record_id: str, session: Session = Depends(get_session)) -> RecordDetail:
    detail = crud.get_record_detail(session, record_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="record not found")
    return detail


@app.patch("/records/{record_id}", response_model=RecordDetail)
def patch_record(
    record_id: str,
    req: CorrectionRequest,
    session: Session = Depends(get_session),
) -> RecordDetail:
    try:
        return crud.apply_correction(session, record_id, req)
    except crud.RecordNotFound:
        raise HTTPException(status_code=404, detail="record not found")
    except crud.RecordVoided:
        raise HTTPException(status_code=409, detail="record is voided; cannot correct")


@app.post("/records/{record_id}/void", response_model=RecordDetail)
def void_record(
    record_id: str,
    req: VoidRequest,
    session: Session = Depends(get_session),
) -> RecordDetail:
    try:
        return crud.apply_void(session, record_id, req)
    except crud.RecordNotFound:
        raise HTTPException(status_code=404, detail="record not found")
    except crud.AlreadyVoided:
        raise HTTPException(status_code=409, detail="record is already voided")
