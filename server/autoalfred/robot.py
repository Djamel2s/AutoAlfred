"""Connection to a target's MCP server.

The agent may only use ROBOT_PRIMITIVES (from the robot) and PLATFORM_TOOLS
(provided by the server itself). Anything else a target exposes, such as the
simulator's `sim_*` tools, is reserved to the platform (evaluation, status).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import anyio
from mcp import Client

ROBOT_PRIMITIVES = ["navigate_to", "look", "detect", "pick", "place", "read_text"]
PLATFORM_TOOLS = ["web_search", "ask_human"]
AGENT_TOOLS = ROBOT_PRIMITIVES + PLATFORM_TOOLS

STATUS_TIMEOUT_S = 3.0

# Builds what `mcp.Client` connects to from a target URL. Tests replace it with
# an in-process server.
Connector = Callable[[str], Any]


def default_connector(url: str) -> Any:
    return url


def result_payload(result: Any) -> Any:
    if result.structured_content is not None:
        return result.structured_content
    texts = [c.text for c in result.content if getattr(c, "type", None) == "text"]
    if len(texts) == 1:
        try:
            return json.loads(texts[0])
        except json.JSONDecodeError:
            return texts[0]
    return texts


class RobotConnection:
    def __init__(self, url: str, connector: Connector = default_connector):
        self.url = url
        self.connector = connector

    def client(self) -> Client:
        return Client(self.connector(self.url))

    async def list_tools(self) -> list[dict[str, Any]]:
        async with self.client() as client:
            tools = (await client.list_tools()).tools
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "agent_visible": t.name in ROBOT_PRIMITIVES,
            }
            for t in tools
        ]

    async def call(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        async with self.client() as client:
            result = await client.call_tool(name, arguments or {})
        return {"is_error": result.is_error, "data": result_payload(result)}

    async def status(self) -> dict[str, Any]:
        try:
            with anyio.fail_after(STATUS_TIMEOUT_S):
                info = await self.call("robot_info")
        except Exception as e:  # unreachable, timeout, protocol error...
            return {"online": False, "error": f"{type(e).__name__}: {e}"}
        if info["is_error"]:
            return {"online": True, "info": None, "error": str(info["data"])}
        return {"online": True, "info": info["data"]}
