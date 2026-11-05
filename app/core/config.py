"""Lectura de la configuración desde el entorno (archivo .env)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# La raíz del proyecto es la carpeta que contiene a "app/".
RAIZ = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Configuracion:
    database_url: str
    sql_echo: bool


def obtener_configuracion() -> Configuracion:
    """Lee DATABASE_URL (obligatoria) y SQL_ECHO (opcional) del entorno.

    El archivo .env no se versiona; en el repositorio solo está env.example.
    """
    load_dotenv(RAIZ / ".env")

    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta la variable de entorno DATABASE_URL. "
            "Copiar env.example a .env y completar los datos de la base."
        )

    echo = os.getenv("SQL_ECHO", "false").strip().lower() in {"1", "true", "yes", "si", "sí"}
    return Configuracion(database_url=url, sql_echo=echo)
