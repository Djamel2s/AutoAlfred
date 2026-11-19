from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_or_404, get_session
from ..models import ACTIVE_STATUSES, HarnessVersion, Mission, MissionStatus, Target, TraceEvent
from ..schemas import MissionCreate, MissionOut, TraceEventOut

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", response_model=MissionOut, status_code=201)
def create_mission(body: MissionCreate, session: Session = Depends(get_session)):
    target = get_or_404(session, Target, body.target_id)
    version_id = body.harness_version_id or target.active_harness_version_id
    if not version_id:
        raise HTTPException(400, "Aucune version du harness indiquée ni active sur cette cible")
    get_or_404(session, HarnessVersion, version_id)
    mission = Mission(
        instruction=body.instruction, target_id=target.id, harness_version_id=version_id, scenario=body.scenario
    )
    session.add(mission)
    session.commit()
    # The agent loop picks up pending missions (next step of development).
    return mission


@router.get("", response_model=list[MissionOut])
def list_missions(
    status: MissionStatus | None = None,
    target_id: str | None = None,
    limit: int = 50,
    session: Session = Depends(get_session),
):
    query = select(Mission).order_by(Mission.created_at.desc()).limit(min(limit, 500))
    if status:
        query = query.where(Mission.status == status)
    if target_id:
        query = query.where(Mission.target_id == target_id)
    return session.scalars(query).all()


@router.get("/{mission_id}", response_model=MissionOut)
def get_mission(mission_id: str, session: Session = Depends(get_session)):
    return get_or_404(session, Mission, mission_id)


@router.post("/{mission_id}/cancel", response_model=MissionOut)
def cancel_mission(mission_id: str, session: Session = Depends(get_session)):
    mission = get_or_404(session, Mission, mission_id)
    if mission.status not in ACTIVE_STATUSES:
        raise HTTPException(409, f"Mission déjà terminée ({mission.status.value})")
    mission.status = MissionStatus.cancelled
    mission.finished_at = datetime.now(timezone.utc)
    session.commit()
    return mission


@router.get("/{mission_id}/events", response_model=list[TraceEventOut])
def mission_events(mission_id: str, after_seq: int = -1, session: Session = Depends(get_session)):
    get_or_404(session, Mission, mission_id)
    query = (
        select(TraceEvent)
        .where(TraceEvent.mission_id == mission_id, TraceEvent.seq > after_seq)
        .order_by(TraceEvent.seq)
    )
    return session.scalars(query).all()
