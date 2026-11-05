"""Tablas duenio y ficha_duenio."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota


class Duenio(SQLModel, table=True):
    __tablename__ = "duenio"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    email: str = Field(max_length=254, unique=True)  # RN-01

    # passive_deletes=True: el ORM no carga ni toca estas filas al borrar un
    # dueño; lo decide la base (ficha: CASCADE, mascotas: RESTRICT -> RN-08).
    # Uno a uno: "ficha" devuelve un objeto (uselist=False), no una lista.
    ficha: Optional["FichaDuenio"] = Relationship(
        back_populates="duenio",
        passive_deletes=True,
        sa_relationship_kwargs={"uselist": False},
    )
    mascotas: list["Mascota"] = Relationship(back_populates="duenio", passive_deletes=True)


class FichaDuenio(SQLModel, table=True):
    __tablename__ = "ficha_duenio"

    id: int | None = Field(default=None, primary_key=True)
    # UNIQUE sobre la clave foránea: eso es lo que convierte el 1-a-N en 1-a-1 (RN-03).
    duenio_id: int = Field(foreign_key="duenio.id", unique=True, ondelete="CASCADE")
    telefono: str = Field(max_length=30)
    direccion: str = Field(max_length=200)

    duenio: Optional[Duenio] = Relationship(back_populates="ficha")
