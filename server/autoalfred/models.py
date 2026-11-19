"""Data model.

- Target: where a mission runs (simulator or physical robot), reached through MCP.
- HarnessVersion: an immutable snapshot of what self-improvement may change
  (prompts, skills, strategy, recovery rules, routing). Never updated in place.
- Mission: one run of an instruction on a target with a given harness version.
- TraceEvent: an ordered step of a mission (plan, tool call, model call, critic...).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _id() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TargetKind(str, enum.Enum):
    simulator = "simulator"
    physical = "physical"


class MissionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


ACTIVE_STATUSES = {MissionStatus.pending, MissionStatus.running}


class HarnessVersion(Base):
    __tablename__ = "harness_versions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_id)
    number: Mapped[int] = mapped_column(Integer, unique=True)
    label: Mapped[str] = mapped_column(String(200))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("harness_versions.id"))
    config: Mapped[dict[str, Any]] = mapped_column(JSON)
    rationale: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(100), default="human")  # "human" or "self-improvement"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_id)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    kind: Mapped[TargetKind] = mapped_column(Enum(TargetKind))
    mcp_url: Mapped[str] = mapped_column(String(500))
    robot_model: Mapped[str | None] = mapped_column(String(100))  # e.g. "tonypi", "ainex"
    active_harness_version_id: Mapped[str | None] = mapped_column(ForeignKey("harness_versions.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    active_harness_version: Mapped[HarnessVersion | None] = relationship()


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_id)
    instruction: Mapped[str] = mapped_column(Text)
    target_id: Mapped[str] = mapped_column(ForeignKey("targets.id"))
    harness_version_id: Mapped[str] = mapped_column(ForeignKey("harness_versions.id"))
    scenario: Mapped[str | None] = mapped_column(String(100))  # simulator scenario, if any
    status: Mapped[MissionStatus] = mapped_column(Enum(MissionStatus), default=MissionStatus.pending)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_eur: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    target: Mapped[Target] = relationship()
    harness_version: Mapped[HarnessVersion] = relationship()
    events: Mapped[list[TraceEvent]] = relationship(
        back_populates="mission", order_by="TraceEvent.seq", cascade="all, delete-orphan"
    )


class TraceEvent(Base):
    __tablename__ = "trace_events"
    __table_args__ = (UniqueConstraint("mission_id", "seq"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_id)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), index=True)
    seq: Mapped[int] = mapped_column(Integer)
    phase: Mapped[str] = mapped_column(String(20))  # perceive | plan | execute | analyze
    kind: Mapped[str] = mapped_column(String(30))  # plan | tool_call | model_call | critic | reflexion | ask_human | status
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    mission: Mapped[Mission] = relationship(back_populates="events")
