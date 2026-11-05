"""DTO del módulo mascotas."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Especie = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


class MascotaCreate(BaseModel):
    nombre: Nombre
    especie: Especie
    duenio_id: int  # agregación: viaja un id, el dueño ya existe


class MascotaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    especie: str
    duenio_id: int


class DuenioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class MascotaConDuenio(MascotaRead):
    duenio: DuenioResumen


class PaginaMascotas(BaseModel):
    """Envoltorio de paginación: { items, total, page, size, pages }."""

    items: list[MascotaRead]
    total: int
    page: int
    size: int
    pages: int
