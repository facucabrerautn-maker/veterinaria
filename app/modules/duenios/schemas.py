"""DTO de entrada (Create, Update) y de salida (Read) del módulo duenios."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        min_length=3,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]
Telefono = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
Direccion = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class FichaCreate(BaseModel):
    telefono: Telefono
    direccion: Direccion


class FichaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    duenio_id: int
    telefono: str
    direccion: str


class DuenioCreate(BaseModel):
    nombre: Nombre
    email: Email


class DuenioUpdate(BaseModel):
    """PATCH: todos los campos son opcionales; solo se aplican los enviados."""

    nombre: Nombre | None = None
    email: Email | None = None


class DuenioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    ficha: FichaRead | None = None
