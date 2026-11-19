"""MCP server exposing the robot primitives over a simulated world.

Same contract as the real robot's MCP server:
- Primitives (the only tools the agent may use): navigate_to, look, detect, pick, place, read_text.
- `robot_info`: the robot sheet, read by the platform.
- `sim_*`: simulator-only tools for evaluation (reset a scenario, read ground truth).
  The platform must never expose them to the agent.

`web_search` and `ask_human` are not robot capabilities: the platform provides them.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from .profiles import get_profile
from .world import SCENARIOS, World

PRIMITIVES = ["navigate_to", "look", "detect", "pick", "place", "read_text"]


def build_server(profile_id: str = "ainex", scenario_id: str = "ranger", seed: int = 0) -> MCPServer:
    profile = get_profile(profile_id)
    world = World(profile, scenario_id, seed)
    mcp = MCPServer(name=f"autoalfred-robot-stub-{profile.id}", instructions="Robot simulé AutoAlfred.")

    @mcp.tool(description="Marcher jusqu'à un lieu nommé (table, bureau, etagere, bac, sol, couloir).")
    def navigate_to(location: str) -> dict[str, Any]:
        return world.navigate_to(location)

    @mcp.tool(description="Regarder autour : lieu actuel, objet tenu, objets visibles.")
    def look() -> dict[str, Any]:
        return world.look()

    @mcp.tool(description="Chercher ici les objets correspondant à une description (couleur, forme, usage).")
    def detect(query: str) -> dict[str, Any]:
        return world.detect(query)

    @mcp.tool(description="Saisir un objet visible ici, par son id. Une seule main libre à la fois.")
    def pick(object_id: str) -> dict[str, Any]:
        return world.pick(object_id)

    @mcp.tool(description="Poser l'objet tenu sur le lieu actuel (le robot doit y être).")
    def place(location: str) -> dict[str, Any]:
        return world.place(location)

    @mcp.tool(description="Lire le texte d'un objet visible ici ou tenu en main.")
    def read_text(object_id: str) -> dict[str, Any]:
        return world.read_text(object_id)

    @mcp.tool(description="Fiche du robot : modèle, capacités, limites, primitives disponibles.")
    def robot_info() -> dict[str, Any]:
        return {
            "profile": profile.id,
            "name": profile.name,
            "description": profile.description,
            "limits": profile.limits,
            "primitives": PRIMITIVES,
            "simulated": True,
        }

    @mcp.tool(description="[Simulateur] Réinitialiser le monde sur un scénario et une graine.")
    def sim_reset(scenario: str, seed: int = 0) -> dict[str, Any]:
        try:
            return world.reset(scenario, seed)
        except ValueError as e:
            return {"ok": False, "message": str(e)}

    @mcp.tool(description="[Simulateur] État réel du monde et critère de réussite du scénario.")
    def sim_state() -> dict[str, Any]:
        return world.state()

    @mcp.tool(description="[Simulateur] Liste des scénarios disponibles.")
    def sim_scenarios() -> dict[str, Any]:
        return {
            "scenarios": [
                {"id": s.id, "title": s.title, "instruction": s.instruction} for s in SCENARIOS.values()
            ]
        }

    return mcp
