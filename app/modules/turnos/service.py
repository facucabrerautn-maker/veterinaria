"""Lógica del módulo turnos."""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import es_unicidad
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica
from app.modules.turnos.schemas import MascotaEnTurno, PracticaEnTurno, TurnoCreate, TurnoRead


def _a_read(turno: Turno) -> TurnoRead:
    """Arma la respuesta con datos ya cargados (no dispara cargas perezosas)."""
    reservas = sorted(turno.practicas, key=lambda r: r.practica_id)
    return TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=MascotaEnTurno.model_validate(turno.mascota),
        practicas=[
            PracticaEnTurno(
                practica_id=r.practica_id,
                nombre=r.practica.nombre,
                precio_unitario=r.precio_unitario,
            )
            for r in reservas
        ],
    )


async def _cargar(session: AsyncSession, turno_id: int) -> Turno:
    """Turno con mascota y prácticas, con un número FIJO de consultas.

    - mascota: relación "a uno"  -> joinedload  (un JOIN en la consulta principal)
    - practicas: colección       -> selectinload (una consulta más, con IN)
    - el nombre de cada práctica: "a uno" dentro de la colección -> joinedload
      encadenado, dentro de esa misma consulta de la colección.

    Son 2 consultas siempre, sin importar cuántas prácticas tenga el turno.
    """
    consulta = (
        select(Turno)
        .where(Turno.id == turno_id)
        .options(
            joinedload(Turno.mascota),
            selectinload(Turno.practicas).joinedload(TurnoPractica.practica),
        )
        .execution_options(populate_existing=True)
    )
    turno = (await session.exec(consulta)).first()
    if turno is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un turno con ese id.")
    return turno


async def obtener(session: AsyncSession, turno_id: int) -> TurnoRead:
    return _a_read(await _cargar(session, turno_id))


async def crear(session: AsyncSession, datos: TurnoCreate) -> TurnoRead:
    """Crea el turno y sus prácticas en UNA sola transacción: todo o nada."""
    ids = [p.practica_id for p in datos.practicas]

    # RN-06: el precio de cada práctica se copia del catálogo. Esta lectura es
    # necesaria para conocer los precios; todavía no se escribió nada.
    catalogo = (
        await session.exec(select(Practica).where(Practica.id.in_(list(set(ids)))))
    ).all()
    precios = {p.id: p.precio for p in catalogo}

    faltantes = sorted(set(ids) - precios.keys())
    if faltantes:
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"No existen las prácticas con id {faltantes}. No se guardó nada.",
        )

    # El total lo calcula el servidor. Si una práctica viniera repetida, la
    # base rechaza la escritura más abajo (RN-07), así que ese total no se guarda.
    total = sum((precios[i] for i in ids), Decimal("0"))

    turno = Turno(
        mascota_id=datos.mascota_id, fecha=datos.fecha, motivo=datos.motivo, total=total
    )
    session.add(turno)
    try:
        await session.flush()  # obtiene el id y hace que la base verifique mascota_id
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"La mascota con id {datos.mascota_id} no existe. No se guardó nada.",
        )

    filas = [
        {"turno_id": turno.id, "practica_id": i, "precio_unitario": precios[i]} for i in ids
    ]
    try:
        # Un único INSERT con todas las prácticas: si hay una repetida, la clave
        # primaria compuesta de turno_practica lo rechaza.
        await session.exec(insert(TurnoPractica.__table__).values(filas))
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        if es_unicidad(error):
            mensaje = "Una misma práctica no puede figurar dos veces en un turno."
        else:
            mensaje = "La base rechazó la reserva de las prácticas."
        raise HTTPException(status.HTTP_409_CONFLICT, f"{mensaje} No se guardó nada.")

    return await obtener(session, turno.id)


async def eliminar(session: AsyncSession, turno_id: int) -> None:
    turno = await session.get(Turno, turno_id)
    if turno is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe un turno con ese id.")
    # Las filas de turno_practica las borra la base (ON DELETE CASCADE, RN-09).
    await session.delete(turno)
    await session.commit()
