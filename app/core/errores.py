"""Ayudas para traducir errores de la base a respuestas HTTP.

Las reglas de negocio (unicidad, claves foráneas, comprobaciones) las hace
cumplir la base. Los services atrapan IntegrityError, deshacen la transacción
y responden con un mensaje propio; este módulo solo ayuda a distinguir qué
tipo de restricción se violó, mirando el código SQLSTATE de PostgreSQL.
"""

from sqlalchemy.exc import IntegrityError

VIOLACION_UNICIDAD = "23505"
VIOLACION_CLAVE_FORANEA = "23503"
VIOLACION_COMPROBACION = "23514"


def sqlstate(error: IntegrityError) -> str | None:
    """Devuelve el código SQLSTATE del error original del controlador."""
    original = error.orig
    for candidato in (original, getattr(original, "__cause__", None)):
        codigo = getattr(candidato, "sqlstate", None) or getattr(candidato, "pgcode", None)
        if codigo:
            return codigo
    return None


def es_clave_foranea(error: IntegrityError) -> bool:
    return sqlstate(error) == VIOLACION_CLAVE_FORANEA


def es_unicidad(error: IntegrityError) -> bool:
    return sqlstate(error) == VIOLACION_UNICIDAD
