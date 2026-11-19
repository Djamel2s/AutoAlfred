from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import MissionStatus, TargetKind


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- targets -------------------------------------------------------------------
class TargetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: TargetKind
    mcp_url: str = Field(min_length=1, max_length=500)
    robot_model: str | None = None


class TargetOut(ORM):
    id: str
    name: str
    kind: TargetKind
    mcp_url: str
    robot_model: str | None
    active_harness_version_id: str | None
    created_at: datetime


class TargetStatus(BaseModel):
    target_id: str
    state: str  # online | offline | busy
    info: dict[str, Any] | None = None
    error: str | None = None


class ActivateVersion(BaseModel):
    harness_version_id: str


# --- harness -------------------------------------------------------------------
class HarnessVersionCreate(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    parent_id: str | None = None
    config: dict[str, Any]
    rationale: str = ""
    author: str = "human"


class HarnessVersionOut(ORM):
    id: str
    number: int
    label: str
    parent_id: str | None
    config: dict[str, Any]
    rationale: str
    author: str
    created_at: datetime


class HarnessDiff(BaseModel):
    from_id: str
    to_id: str
    changes: list[dict[str, Any]]


# --- missions ------------------------------------------------------------------
class MissionCreate(BaseModel):
    instruction: str = Field(min_length=1)
    target_id: str
    harness_version_id: str | None = None  # defaults to the target's active version
    scenario: str | None = None


class MissionOut(ORM):
    id: str
    instruction: str
    target_id: str
    harness_version_id: str
    scenario: str | None
    status: MissionStatus
    result: dict[str, Any] | None
    input_tokens: int
    output_tokens: int
    cost_eur: float
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class TraceEventOut(ORM):
    id: str
    seq: int
    phase: str
    kind: str
    payload: dict[str, Any]
    duration_ms: int | None
    error: str | None
    created_at: datetime
