"""AutoAlfred server.

Run: uvicorn autoalfred.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import harness, missions, targets
from .db import Database
from .harness import ensure_initial_version
from .robot import AGENT_TOOLS, Connector, default_connector


def create_app(db: Database | None = None, connector: Connector = default_connector) -> FastAPI:
    database = db or Database()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        database.create_all()
        with database.sessionmaker() as session:
            ensure_initial_version(session)
        yield

    app = FastAPI(title="AutoAlfred", version="0.1.0", lifespan=lifespan)
    app.state.db = database
    app.state.connector = connector

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "ok", "agent_tools": AGENT_TOOLS}

    app.include_router(targets.router)
    app.include_router(harness.router)
    app.include_router(missions.router)
    return app


app = create_app()
