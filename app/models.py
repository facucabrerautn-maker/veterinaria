"""Importa todos los modelos de tabla para que SQLModel conozca el esquema completo.

Las relaciones entre módulos se declaran con nombres de clase (strings), así que
todas las clases tienen que estar importadas antes de usar la base.
"""

from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica

__all__ = ["Duenio", "FichaDuenio", "Mascota", "Practica", "Turno", "TurnoPractica"]
