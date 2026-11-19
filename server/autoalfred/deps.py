from collections.abc import Iterator
from typing import TypeVar

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from .db import Base
from .robot import Connector


def get_session(request: Request) -> Iterator[Session]:
    yield from request.app.state.db.session()


def get_connector(request: Request) -> Connector:
    return request.app.state.connector


T = TypeVar("T", bound=Base)


def get_or_404(session: Session, model: type[T], id_: str) -> T:
    obj = session.get(model, id_)
    if obj is None:
        raise HTTPException(404, f"{model.__name__} {id_} introuvable")
    return obj
