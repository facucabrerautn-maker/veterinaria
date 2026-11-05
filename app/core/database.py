"""Motor asincrónico, fábrica de sesiones y dependencia get_session.

El motor y la fábrica NO se crean al importar este módulo: se crean en el
lifespan de la aplicación (app/main.py) y se guardan en app.state.
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


def crear_motor(database_url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
        # Si la base no contesta, /health/ready tiene que fallar rápido.
        connect_args={"timeout": 5},
    )


def crear_fabrica_sesiones(motor: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: después del commit los objetos conservan sus
    # atributos; si no, leerlos dispararía una carga perezosa, que en un
    # contexto asincrónico falla con MissingGreenlet.
    return async_sessionmaker(bind=motor, class_=AsyncSession, expire_on_commit=False)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Una sesión por petición, que se cierra al terminar."""
    fabrica: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with fabrica() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
