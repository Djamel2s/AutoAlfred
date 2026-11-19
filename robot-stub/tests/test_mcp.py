import json

import pytest
from mcp import Client

from robot_stub.server import PRIMITIVES, build_server

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def payload(result):
    if result.structured_content is not None:
        data = result.structured_content
        return data.get("result", data) if isinstance(data, dict) and set(data) == {"result"} else data
    return json.loads(result.content[0].text)


async def test_tools_listed():
    async with Client(build_server("tonypi")) as client:
        names = {t.name for t in (await client.list_tools()).tools}
    assert set(PRIMITIVES) <= names
    assert {"robot_info", "sim_reset", "sim_state", "sim_scenarios"} <= names


async def test_robot_info_reports_profile():
    async with Client(build_server("tonypi")) as client:
        info = payload(await client.call_tool("robot_info", {}))
    assert info["profile"] == "tonypi" and info["limits"]


async def test_primitive_roundtrip():
    async with Client(build_server("ainex", "ranger")) as client:
        res = payload(await client.call_tool("navigate_to", {"location": "table"}))
        assert "ok" in res
        await client.call_tool("sim_reset", {"scenario": "retrouver", "seed": 1})
        state = payload(await client.call_tool("sim_state", {}))
    assert state["scenario"] == "retrouver" and state["robot"]["location"] == "couloir"
