from fastapi import APIRouter, Response, status

from app.core.database import SessionDep
from app.modules.duenios import service
from app.modules.duenios.schemas import (
    DuenioCreate,
    DuenioRead,
    DuenioUpdate,
    FichaCreate,
    FichaRead,
)
from app.modules.mascotas.schemas import MascotaRead

router = APIRouter(prefix="/duenios", tags=["duenios"])


@router.post("/", response_model=DuenioRead, status_code=status.HTTP_201_CREATED)
async def crear_duenio(datos: DuenioCreate, session: SessionDep):
    return await service.crear(session, datos)


@router.get("/{duenio_id}", response_model=DuenioRead)
async def obtener_duenio(duenio_id: int, session: SessionDep):
    return await service.obtener(session, duenio_id)


@router.patch("/{duenio_id}", response_model=DuenioRead)
async def actualizar_duenio(duenio_id: int, datos: DuenioUpdate, session: SessionDep):
    return await service.actualizar(session, duenio_id, datos)


@router.delete("/{duenio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_duenio(duenio_id: int, session: SessionDep) -> Response:
    await service.eliminar(session, duenio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{duenio_id}/ficha", response_model=FichaRead, status_code=status.HTTP_201_CREATED
)
async def crear_ficha(duenio_id: int, datos: FichaCreate, session: SessionDep):
    return await service.crear_ficha(session, duenio_id, datos)


@router.get("/{duenio_id}/mascotas", response_model=list[MascotaRead])
async def mascotas_del_duenio(duenio_id: int, session: SessionDep):
    return await service.mascotas_del_duenio(session, duenio_id)
