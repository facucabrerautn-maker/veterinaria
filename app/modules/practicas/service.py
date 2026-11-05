"""Lógica del módulo practicas."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.practicas.models import Practica
from app.modules.practicas.schemas import PracticaCreate


async def crear(session: AsyncSession, datos: PracticaCreate) -> Practica:
    practica = Practica(**datos.model_dump())
    session.add(practica)
    try:
        await session.commit()
    except IntegrityError:
        # UNIQUE sobre practica.nombre (RN-02).
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Ya existe una práctica llamada '{datos.nombre}'."
        )
    # Se relee para devolver el precio con el formato de la base (dos decimales).
    await session.refresh(practica)
    return practica


async def listar(session: AsyncSession) -> list[Practica]:
    return list((await session.exec(select(Practica).order_by(Practica.id))).all())
