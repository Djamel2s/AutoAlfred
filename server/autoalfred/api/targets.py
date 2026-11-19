from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..deps import get_connector, get_or_404, get_session
from ..models import HarnessVersion, Mission, MissionStatus, Target
from ..robot import Connector, RobotConnection
from ..schemas import ActivateVersion, TargetCreate, TargetOut, TargetStatus

router = APIRouter(prefix="/targets", tags=["targets"])


@router.post("", response_model=TargetOut, status_code=201)
def create_target(body: TargetCreate, session: Session = Depends(get_session)):
    # A new target starts on the initial version; promoting another one is an explicit step.
    initial = session.scalar(select(HarnessVersion).order_by(HarnessVersion.number).limit(1))
    target = Target(**body.model_dump(), active_harness_version_id=initial.id if initial else None)
    session.add(target)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, f"Une cible nommée {body.name!r} existe déjà") from None
    return target


@router.get("", response_model=list[TargetOut])
def list_targets(session: Session = Depends(get_session)):
    return session.scalars(select(Target).order_by(Target.created_at)).all()


@router.get("/{target_id}", response_model=TargetOut)
def get_target(target_id: str, session: Session = Depends(get_session)):
    return get_or_404(session, Target, target_id)


@router.delete("/{target_id}", status_code=204)
def delete_target(target_id: str, session: Session = Depends(get_session)):
    target = get_or_404(session, Target, target_id)
    if session.scalar(select(Mission.id).where(Mission.target_id == target_id).limit(1)):
        raise HTTPException(409, "Cible utilisée par des missions : suppression impossible")
    session.delete(target)
    session.commit()


@router.get("/{target_id}/status", response_model=TargetStatus)
async def target_status(
    target_id: str, session: Session = Depends(get_session), connector: Connector = Depends(get_connector)
):
    target = get_or_404(session, Target, target_id)
    status = await RobotConnection(target.mcp_url, connector).status()
    if not status["online"]:
        return TargetStatus(target_id=target_id, state="offline", error=status.get("error"))
    busy = session.scalar(
        select(Mission.id).where(Mission.target_id == target_id, Mission.status == MissionStatus.running).limit(1)
    )
    return TargetStatus(
        target_id=target_id, state="busy" if busy else "online", info=status.get("info"), error=status.get("error")
    )


@router.get("/{target_id}/tools")
async def target_tools(
    target_id: str, session: Session = Depends(get_session), connector: Connector = Depends(get_connector)
):
    target = get_or_404(session, Target, target_id)
    try:
        return await RobotConnection(target.mcp_url, connector).list_tools()
    except Exception as e:
        raise HTTPException(502, f"Cible injoignable : {type(e).__name__}: {e}") from None


@router.post("/{target_id}/activate", response_model=TargetOut)
def activate_version(target_id: str, body: ActivateVersion, session: Session = Depends(get_session)):
    """Set the harness version used by new missions on this target. Also serves as rollback."""
    target = get_or_404(session, Target, target_id)
    get_or_404(session, HarnessVersion, body.harness_version_id)
    target.active_harness_version_id = body.harness_version_id
    session.commit()
    return target
