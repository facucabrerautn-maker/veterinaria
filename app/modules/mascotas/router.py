from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.database import SessionDep
from app.modules.mascotas import service
from app.modules.mascotas.schemas import (
    MascotaConDuenio,
    MascotaCreate,
    MascotaRead,
    PaginaMascotas,
)

router = APIRouter(prefix="/mascotas", tags=["mascotas"])


@router.post("/", response_model=MascotaRead, status_code=status.HTTP_201_CREATED)
async def crear_mascota(datos: MascotaCreate, session: SessionDep):
    return await service.crear(session, datos)


@router.get("/", response_model=PaginaMascotas)
async def listar_mascotas(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await service.listar(session, page, size)


@router.get("/{mascota_id}", response_model=MascotaConDuenio)
async def obtener_mascota(mascota_id: int, session: SessionDep):
    return await service.obtener(session, mascota_id)
