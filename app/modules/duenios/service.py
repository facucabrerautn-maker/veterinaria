"""Lógica del módulo duenios.

Ninguna regla se verifica con una consulta previa de tipo "¿ya existe?": se
escribe, y si la base rechaza la escritura se deshace la transacción y se
responde 409 con un mensaje propio.
"""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import es_clave_foranea
from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.duenios.schemas import DuenioCreate, DuenioUpdate, FichaCreate
from app.modules.mascotas.models import Mascota


async def obtener(session: AsyncSession, duenio_id: int) -> Duenio:
    """Dueño con su ficha, en una sola consulta (joinedload: relación "a uno")."""
    consulta = (
        select(Duenio)
        .where(Duenio.id == duenio_id)
        .options(joinedload(Duenio.ficha))
        .execution_options(populate_existing=True)
    )
    duenio = (await session.exec(consulta)).first()
    if duenio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un dueño con ese id.")
    return duenio


async def crear(session: AsyncSession, datos: DuenioCreate) -> Duenio:
    duenio = Duenio(**datos.model_dump())
    session.add(duenio)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Ya existe un dueño con el email {datos.email}."
        )
    # Se relee con la ficha cargada para no depender de la carga perezosa.
    return await obtener(session, duenio.id)


async def actualizar(session: AsyncSession, duenio_id: int, datos: DuenioUpdate) -> Duenio:
    duenio = await session.get(Duenio, duenio_id)
    if duenio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un dueño con ese id.")

    # exclude_unset: solo los campos que el cliente envió. Un null explícito se
    # ignora, porque ninguna de las columnas admite NULL.
    cambios = {c: v for c, v in datos.model_dump(exclude_unset=True).items() if v is not None}
    for campo, valor in cambios.items():
        setattr(duenio, campo, valor)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Ya existe otro dueño con ese email."
        )
    return await obtener(session, duenio_id)


async def eliminar(session: AsyncSession, duenio_id: int) -> None:
    duenio = await session.get(Duenio, duenio_id)
    if duenio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un dueño con ese id.")

    await session.delete(duenio)
    try:
        await session.commit()
    except IntegrityError:
        # ON DELETE RESTRICT en mascota.duenio_id (RN-08).
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No se puede borrar el dueño: tiene mascotas a su nombre.",
        )


async def crear_ficha(session: AsyncSession, duenio_id: int, datos: FichaCreate) -> FichaDuenio:
    ficha = FichaDuenio(duenio_id=duenio_id, **datos.model_dump())
    session.add(ficha)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        if es_clave_foranea(error):
            # El dueño no existe: la clave foránea lo detectó, sin consulta previa.
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un dueño con ese id.")
        # UNIQUE sobre ficha_duenio.duenio_id (RN-03).
        raise HTTPException(status.HTTP_409_CONFLICT, "El dueño ya tiene una ficha cargada.")
    return ficha


async def mascotas_del_duenio(session: AsyncSession, duenio_id: int) -> list[Mascota]:
    if await session.get(Duenio, duenio_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un dueño con ese id.")
    consulta = select(Mascota).where(Mascota.duenio_id == duenio_id).order_by(Mascota.id)
    return list((await session.exec(consulta)).all())
