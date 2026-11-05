"""DTO del módulo practicas."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class PracticaCreate(BaseModel):
    nombre: Nombre
    # RN-04: el precio es mayor que cero (la base lo vuelve a verificar con un CHECK).
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class PracticaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal
