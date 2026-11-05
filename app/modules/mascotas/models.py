"""Tabla mascota."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.duenios.models import Duenio
    from app.modules.turnos.models import Turno


class Mascota(SQLModel, table=True):
    __tablename__ = "mascota"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    especie: str = Field(max_length=50)
    # Agregación: la mascota existe por sí misma y puede cambiar de dueño, pero
    # mientras un dueño tenga mascotas no se lo puede borrar (RN-08).
    # PostgreSQL no indexa solo las claves foráneas, por eso index=True.
    duenio_id: int = Field(foreign_key="duenio.id", ondelete="RESTRICT", index=True)

    duenio: Optional["Duenio"] = Relationship(back_populates="mascotas")
    turnos: list["Turno"] = Relationship(back_populates="mascota", passive_deletes=True)
