from fastapi import APIRouter, status

from app.core.database import SessionDep
from app.modules.practicas import service
from app.modules.practicas.schemas import PracticaCreate, PracticaRead

router = APIRouter(prefix="/practicas", tags=["practicas"])


@router.post("/", response_model=PracticaRead, status_code=status.HTTP_201_CREATED)
async def crear_practica(datos: PracticaCreate, session: SessionDep):
    return await service.crear(session, datos)


@router.get("/", response_model=list[PracticaRead])
async def listar_practicas(session: SessionDep):
    return await service.listar(session)
