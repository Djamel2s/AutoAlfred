"""Harness: everything self-improvement is allowed to change.

Guardrails, tool definitions, models and test sets are NOT part of the harness:
the agent cannot modify what judges it.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import HarnessVersion

INITIAL_CONFIG: dict[str, Any] = {
    "prompts": {
        "planner": (
            "Tu es le planificateur d'un robot humanoïde. Décompose la mission en étapes courtes "
            "utilisant uniquement les outils disponibles. Respecte les limites de la fiche robot."
        ),
        "executor": "Exécute l'étape courante avec un seul appel d'outil, puis observe le résultat.",
        "critic": (
            "Juge si la mission est accomplie, d'après les observations. Réponds succès ou échec, "
            "avec la raison."
        ),
        "reflexion": "Après un échec, formule une leçon courte et réutilisable pour les prochaines missions.",
    },
    "skills": {},
    "strategy": {"replan_on_failure": True, "max_retries_per_step": 1},
    "recovery_rules": [
        "Si un objet glisse, réessayer une fois avant de replanifier.",
        "Si un chemin est bloqué, suivre l'indication de passage si elle existe.",
    ],
    "routing": {"simple": "local", "complex": "api"},
}


def next_number(session: Session) -> int:
    return (session.scalar(select(func.max(HarnessVersion.number))) or 0) + 1


def ensure_initial_version(session: Session) -> HarnessVersion:
    existing = session.scalar(select(HarnessVersion).order_by(HarnessVersion.number).limit(1))
    if existing:
        return existing
    version = HarnessVersion(number=1, label="v1 — initiale", config=INITIAL_CONFIG, rationale="Version de départ.")
    session.add(version)
    session.commit()
    return version


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            out.update(_flatten(v, f"{prefix}.{k}" if prefix else str(k)))
        return out or {prefix: {}}
    return {prefix: value}


def diff_configs(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, Any]]:
    """Field-level diff. Lists are compared as whole values (rules, steps...)."""
    a, b = _flatten(old), _flatten(new)
    changes = []
    for path in sorted(a.keys() | b.keys()):
        if path not in b:
            changes.append({"path": path, "change": "removed", "old": a[path], "new": None})
        elif path not in a:
            changes.append({"path": path, "change": "added", "old": None, "new": b[path]})
        elif a[path] != b[path]:
            changes.append({"path": path, "change": "modified", "old": a[path], "new": b[path]})
    return changes
