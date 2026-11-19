"""Minimal simulated world for developing the platform without a robot.

The world is a set of named locations, objects placed in them, and a robot that
walks between locations and holds at most one object. Failures are random but
reproducible (seeded), and depend on the robot profile.

Each primitive returns a dict with `ok` and `message`, never raises for a
mission-level failure: the agent must be able to see and learn from failures.
"""

from __future__ import annotations

import copy
import random
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from .profiles import RobotProfile

LOCATIONS = ["table", "bureau", "etagere", "bac", "sol", "couloir"]
BATTERY_COST = {"navigate_to": 1.0, "pick": 0.5, "place": 0.5, "look": 0.1, "detect": 0.1, "read_text": 0.1}


@dataclass
class WorldObject:
    id: str
    name: str
    location: str
    color: str
    shape: str
    weight_g: int
    size_cm: float
    keywords: list[str] = field(default_factory=list)
    text: str | None = None
    font_pt: int | None = None


@dataclass
class Scenario:
    id: str
    title: str
    instruction: str
    start_location: str
    objects: list[WorldObject]
    success: Callable[[World], bool]
    blocked_routes: dict[str, str] = field(default_factory=dict)  # destination -> required waypoint
    expected_answer: str | None = None


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _scenarios() -> dict[str, Scenario]:
    def ball(loc: str) -> WorldObject:
        return WorldObject("balle_rouge", "balle", loc, "rouge", "sphere", 30, 3.5, ["rond", "jouet", "balle"])

    return {
        "ranger": Scenario(
            id="ranger",
            title="Ranger des objets",
            instruction="Range la balle rouge et le cube bleu dans le bac.",
            start_location="couloir",
            objects=[
                ball("table"),
                WorldObject("cube_bleu", "cube", "sol", "bleu", "cube", 20, 3.0, ["cube", "jouet", "bloc"]),
                WorldObject("tasse", "tasse", "table", "blanc", "cylindre", 300, 9.0, ["tasse", "mug"]),
            ],
            success=lambda w: w.obj("balle_rouge").location == "bac" and w.obj("cube_bleu").location == "bac",
        ),
        "retrouver": Scenario(
            id="retrouver",
            title="Retrouver un objet décrit vaguement",
            instruction="Trouve le petit truc rond avec lequel on joue et va le voir.",
            start_location="couloir",
            objects=[
                ball("etagere"),
                WorldObject("orange", "orange", "table", "orange", "sphere", 180, 8.0, ["fruit", "rond"]),
                WorldObject("livre", "livre", "bureau", "vert", "pave", 400, 20.0, ["livre"]),
            ],
            success=lambda w: w.robot_location == "etagere" and "balle_rouge" in w.detected,
        ),
        "lire_web": Scenario(
            id="lire_web",
            title="Lire un document et compléter via le web",
            instruction=(
                "Lis la référence sur l'étiquette posée sur le bureau, puis trouve sur le web "
                "à quel produit elle correspond."
            ),
            start_location="couloir",
            objects=[
                WorldObject(
                    "etiquette", "étiquette", "bureau", "blanc", "plat", 5, 3.5, ["etiquette", "papier", "document"],
                    text="Référence : AX-2041", font_pt=8,
                ),
            ],
            success=lambda w: "etiquette" in w.read_ok,
            expected_answer="AX-2041",
        ),
        "imprevu": Scenario(
            id="imprevu",
            title="Préparer un poste avec imprévu",
            instruction="Apporte le cube bleu sur le bureau.",
            start_location="couloir",
            objects=[WorldObject("cube_bleu", "cube", "etagere", "bleu", "cube", 20, 3.0, ["cube", "bloc"])],
            success=lambda w: w.obj("cube_bleu").location == "bureau",
            blocked_routes={"bureau": "table"},
        ),
    }


SCENARIOS = _scenarios()


class World:
    def __init__(self, profile: RobotProfile, scenario_id: str = "ranger", seed: int = 0):
        self.profile = profile
        self.reset(scenario_id, seed)

    # --- state --------------------------------------------------------------
    def reset(self, scenario_id: str, seed: int = 0) -> dict[str, Any]:
        if scenario_id not in SCENARIOS:
            raise ValueError(f"Scénario inconnu : {scenario_id}. Scénarios : {', '.join(SCENARIOS)}")
        self.scenario = SCENARIOS[scenario_id]
        self.seed = seed
        self.rng = random.Random(seed)
        self.objects = {o.id: copy.deepcopy(o) for o in self.scenario.objects}
        self.robot_location = self.scenario.start_location
        self.holding: str | None = None
        self.battery = 100.0
        self.steps = 0
        self.detected: set[str] = set()
        self.read_ok: set[str] = set()
        self.visited: list[str] = [self.robot_location]
        return {"ok": True, "scenario": scenario_id, "seed": seed, "instruction": self.scenario.instruction}

    def obj(self, object_id: str) -> WorldObject:
        return self.objects[object_id]

    def state(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario.id,
            "seed": self.seed,
            "profile": self.profile.id,
            "robot": {
                "location": self.robot_location,
                "holding": self.holding,
                "battery": round(self.battery, 1),
                "steps": self.steps,
            },
            "objects": {o.id: asdict(o) for o in self.objects.values()},
            "success": self.scenario.success(self),
            "expected_answer": self.scenario.expected_answer,
        }

    def _tick(self, action: str) -> dict[str, Any] | None:
        self.steps += 1
        self.battery = max(0.0, self.battery - BATTERY_COST.get(action, 0.1))
        if self.battery <= 0:
            return {"ok": False, "message": "Batterie vide : le robot ne peut plus agir."}
        return None

    def _here(self) -> list[WorldObject]:
        return [o for o in self.objects.values() if o.location == self.robot_location and o.id != self.holding]

    # --- primitives -----------------------------------------------------------
    def navigate_to(self, location: str) -> dict[str, Any]:
        if err := self._tick("navigate_to"):
            return err
        location = _norm(location)
        if location not in LOCATIONS:
            return {"ok": False, "message": f"Lieu inconnu : {location}. Lieux connus : {', '.join(LOCATIONS)}."}
        if location == self.robot_location:
            return {"ok": True, "message": f"Déjà à {location}.", "location": location}
        waypoint = self.scenario.blocked_routes.get(location)
        if waypoint and self.robot_location != waypoint:
            return {
                "ok": False,
                "message": f"Chemin vers {location} bloqué par un obstacle. Un passage semble possible via {waypoint}.",
                "location": self.robot_location,
            }
        if self.rng.random() > self.profile.navigation_success_rate:
            arrived = self.rng.choice([loc for loc in LOCATIONS if loc not in (location, self.robot_location)])
            self.robot_location = arrived
            self.visited.append(arrived)
            return {"ok": False, "message": f"Le robot s'est égaré et est arrivé à {arrived}.", "location": arrived}
        self.robot_location = location
        self.visited.append(location)
        return {"ok": True, "message": f"Arrivé à {location}.", "location": location}

    def look(self) -> dict[str, Any]:
        if err := self._tick("look"):
            return err
        visible = [{"id": o.id, "name": o.name, "color": o.color, "shape": o.shape} for o in self._here()]
        return {
            "ok": True,
            "location": self.robot_location,
            "holding": self.holding,
            "visible_objects": visible,
            "message": f"{len(visible)} objet(s) visible(s) à {self.robot_location}.",
        }

    def detect(self, query: str) -> dict[str, Any]:
        if err := self._tick("detect"):
            return err
        words = [w for w in _norm(query).split() if len(w) > 2]
        matches = []
        for o in self._here():
            haystack = _norm(" ".join([o.name, o.color, o.shape, *o.keywords]))
            score = sum(w in haystack for w in words) / max(len(words), 1)
            if score > 0:
                matches.append({"id": o.id, "name": o.name, "confidence": round(score, 2)})
                self.detected.add(o.id)
        matches.sort(key=lambda m: -m["confidence"])
        return {"ok": True, "matches": matches, "message": f"{len(matches)} correspondance(s) ici."}

    def pick(self, object_id: str) -> dict[str, Any]:
        if err := self._tick("pick"):
            return err
        if self.holding:
            return {"ok": False, "message": f"Les mains sont déjà prises ({self.holding}). Poser l'objet d'abord."}
        o = self.objects.get(object_id)
        if not o or o.location != self.robot_location:
            return {"ok": False, "message": f"Objet {object_id} introuvable à {self.robot_location}."}
        if not self.profile.can_grip:
            return {"ok": False, "message": "Ce robot ne peut pas saisir d'objet."}
        if o.weight_g > self.profile.max_grip_weight_g or o.size_cm > self.profile.max_grip_size_cm:
            return {"ok": False, "message": f"{o.name} est trop lourd ou trop gros pour ce robot."}
        if self.rng.random() > self.profile.pick_success_rate:
            return {"ok": False, "message": f"{o.name} a glissé des mains. Nouvelle tentative possible."}
        self.holding = o.id
        return {"ok": True, "message": f"{o.name} saisi.", "holding": o.id}

    def place(self, location: str) -> dict[str, Any]:
        if err := self._tick("place"):
            return err
        location = _norm(location)
        if not self.holding:
            return {"ok": False, "message": "Le robot ne tient aucun objet."}
        if location != self.robot_location:
            return {"ok": False, "message": f"Le robot est à {self.robot_location}, pas à {location}. Y aller d'abord."}
        o = self.objects[self.holding]
        o.location = location
        self.holding = None
        return {"ok": True, "message": f"{o.name} posé à {location}."}

    def read_text(self, object_id: str) -> dict[str, Any]:
        if err := self._tick("read_text"):
            return err
        o = self.objects.get(object_id)
        reachable = o and (o.location == self.robot_location or self.holding == o.id)
        if not reachable:
            return {"ok": False, "message": f"Objet {object_id} introuvable à {self.robot_location}."}
        if not o.text:
            return {"ok": False, "message": f"Aucun texte détecté sur {o.name}."}
        too_small = (o.font_pt or 99) < self.profile.ocr_min_font_pt
        if too_small and self.holding != o.id:
            return {
                "ok": False,
                "message": "Texte trop petit pour être lu à cette distance.",
                "partial_text": "".join(c if c in " :" else "?" for c in o.text),
            }
        self.read_ok.add(o.id)
        return {"ok": True, "text": o.text, "message": "Texte lu."}
