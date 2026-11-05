"""Lógica del módulo mascotas."""

from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.mascotas.models import Mascota
from app.modules.mascotas.schemas import MascotaCreate, MascotaRead, PaginaMascotas


async def crear(session: AsyncSession, datos: MascotaCreate) -> Mascota:
    mascota = Mascota(**datos.model_dump())
    session.add(mascota)
    try:
        await session.commit()
    except IntegrityError:
        # La clave foránea mascota.duenio_id rechazó un dueño inexistente.
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"El dueño con id {datos.duenio_id} no existe."
        )
    return mascota


async def obtener(session: AsyncSession, mascota_id: int) -> Mascota:
    """Mascota con su dueño, en una sola consulta (joinedload: relación "a uno")."""
    consulta = (
        select(Mascota)
        .where(Mascota.id == mascota_id)
        .options(joinedload(Mascota.duenio))
        .execution_options(populate_existing=True)
    )
    mascota = (await session.exec(consulta)).first()
    if mascota is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe una mascota con ese id.")
    return mascota


async def listar(session: AsyncSession, page: int, size: int) -> PaginaMascotas:
    total = (await session.exec(select(func.count()).select_from(Mascota))).one()
    pages = ceil(total / size)

    # Una página más allá de "pages" es un error del cliente (422), pero la
    # primera página siempre responde, aunque no haya resultados.
    if page > pages and page != 1:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"La página {page} no existe: hay {pages} página(s).",
        )

    consulta = select(Mascota).order_by(Mascota.id).offset((page - 1) * size).limit(size)
    mascotas = (await session.exec(consulta)).all()
    return PaginaMascotas(
        items=[MascotaRead.model_validate(m) for m in mascotas],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
