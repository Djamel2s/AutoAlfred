import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from autoalfred.db import Database
from autoalfred.main import create_app


def stub_connector(url: str):
    """stub://<profile> -> in-process simulated robot; anything else is unreachable."""
    if url.startswith("stub://"):
        from robot_stub.server import build_server

        return build_server(url.removeprefix("stub://"))
    return "http://127.0.0.1:9/mcp"  # closed port: offline target


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    app = create_app(Database(engine=engine), connector=stub_connector)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def target(client):
    res = client.post(
        "/targets", json={"name": "sim-ainex", "kind": "simulator", "mcp_url": "stub://ainex", "robot_model": "ainex"}
    )
    assert res.status_code == 201, res.text
    return res.json()
