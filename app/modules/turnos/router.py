from fastapi import APIRouter, Response, status

from app.core.database import SessionDep
from app.modules.turnos import service
from app.modules.turnos.schemas import TurnoCreate, TurnoRead

router = APIRouter(prefix="/turnos", tags=["turnos"])


@router.post("/", response_model=TurnoRead, status_code=status.HTTP_201_CREATED)
async def crear_turno(datos: TurnoCreate, session: SessionDep):
    return await service.crear(session, datos)


@router.get("/{turno_id}", response_model=TurnoRead)
async def obtener_turno(turno_id: int, session: SessionDep):
    return await service.obtener(session, turno_id)


@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_turno(turno_id: int, session: SessionDep) -> Response:
    await service.eliminar(session, turno_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
