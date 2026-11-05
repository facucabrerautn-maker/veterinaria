"""DTO del módulo turnos."""

from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints

Motivo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class PracticaReservadaCreate(BaseModel):
    """Una práctica dentro del alta del turno: solo viaja el id.

    Ni el precio ni el total viajan en el DTO: los pone el servidor (RN-06).
    """

    practica_id: int


class TurnoCreate(BaseModel):
    mascota_id: int  # asociación: viaja un id
    fecha: AwareDatetime  # con zona horaria
    motivo: Motivo
    # Composición: las prácticas viajan dentro del cuerpo, y hay al menos una (RN-05).
    practicas: list[PracticaReservadaCreate] = Field(min_length=1)


class MascotaEnTurno(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    especie: str


class PracticaEnTurno(BaseModel):
    practica_id: int
    nombre: str
    precio_unitario: Decimal


class TurnoRead(BaseModel):
    id: int
    fecha: AwareDatetime
    motivo: str
    total: Decimal
    mascota: MascotaEnTurno
    practicas: list[PracticaEnTurno]
