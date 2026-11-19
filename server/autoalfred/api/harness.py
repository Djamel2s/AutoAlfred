"""Harness versions are append-only: there is no update or delete endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_or_404, get_session
from ..harness import diff_configs, next_number
from ..models import HarnessVersion
from ..schemas import HarnessDiff, HarnessVersionCreate, HarnessVersionOut

router = APIRouter(prefix="/harness-versions", tags=["harness"])


@router.post("", response_model=HarnessVersionOut, status_code=201)
def create_version(body: HarnessVersionCreate, session: Session = Depends(get_session)):
    if body.parent_id:
        get_or_404(session, HarnessVersion, body.parent_id)
    version = HarnessVersion(number=next_number(session), **body.model_dump())
    session.add(version)
    session.commit()
    return version


@router.get("", response_model=list[HarnessVersionOut])
def list_versions(session: Session = Depends(get_session)):
    return session.scalars(select(HarnessVersion).order_by(HarnessVersion.number)).all()


@router.get("/{version_id}", response_model=HarnessVersionOut)
def get_version(version_id: str, session: Session = Depends(get_session)):
    return get_or_404(session, HarnessVersion, version_id)


@router.get("/{from_id}/diff/{to_id}", response_model=HarnessDiff)
def diff_versions(from_id: str, to_id: str, session: Session = Depends(get_session)):
    old = get_or_404(session, HarnessVersion, from_id)
    new = get_or_404(session, HarnessVersion, to_id)
    return HarnessDiff(from_id=from_id, to_id=to_id, changes=diff_configs(old.config, new.config))
