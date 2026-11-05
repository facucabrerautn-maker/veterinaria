"""Tablas turno y turno_practica."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota
    from app.modules.practicas.models import Practica


class Turno(SQLModel, table=True):
    __tablename__ = "turno"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_turno_total_no_negativo"),)

    id: int | None = Field(default=None, primary_key=True)
    # Asociación: el turno conoce a la mascota, pero ninguno es parte del otro.
    mascota_id: int = Field(foreign_key="mascota.id", index=True)
    fecha: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    motivo: str = Field(max_length=200)
    total: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))

    mascota: Optional["Mascota"] = Relationship(back_populates="turnos")
    # Composición: las prácticas reservadas nacen y mueren con el turno.
    # passive_deletes=True: el ORM no intenta vaciar ni borrar esas filas por su
    # cuenta al borrar un turno; lo decide la base con ON DELETE CASCADE (RN-09).
    practicas: list["TurnoPractica"] = Relationship(back_populates="turno", passive_deletes=True)


class TurnoPractica(SQLModel, table=True):
    """Tabla intermedia turno <-> práctica, con un dato propio: el precio cobrado."""

    __tablename__ = "turno_practica"
    __table_args__ = (
        CheckConstraint("precio_unitario > 0", name="ck_turno_practica_precio_positivo"),
    )

    # Clave primaria compuesta: impide repetir una práctica en un turno (RN-07).
    # turno_id es la PRIMERA columna de la clave primaria: ese índice ya sirve
    # para buscar por turno_id, por eso no lleva index=True propio.
    turno_id: int = Field(foreign_key="turno.id", primary_key=True, ondelete="CASCADE")
    # practica_id es la segunda columna: la clave primaria no sirve para buscar
    # por ella, así que lleva su propio índice.
    practica_id: int = Field(foreign_key="practica.id", primary_key=True, index=True)
    # Precio congelado al reservar: es de la relación, no de la práctica (RN-06).
    precio_unitario: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))

    turno: Optional[Turno] = Relationship(back_populates="practicas")
    practica: Optional["Practica"] = Relationship(back_populates="reservas")
