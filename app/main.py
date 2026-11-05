"""Aplicación FastAPI: lifespan y registro de routers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (registra todas las tablas y relaciones)
from app.core.config import obtener_configuracion
from app.core.database import crear_fabrica_sesiones, crear_motor
from app.modules.duenios.router import router as duenios_router
from app.modules.health.router import router as health_router
from app.modules.laboratorio.router import router as laboratorio_router
from app.modules.mascotas.router import router as mascotas_router
from app.modules.practicas.router import router as practicas_router
from app.modules.turnos.router import router as turnos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configuracion = obtener_configuracion()
    motor = crear_motor(configuracion.database_url, configuracion.sql_echo)
    app.state.engine = motor
    app.state.session_factory = crear_fabrica_sesiones(motor)
    try:
        yield
    finally:
        await motor.dispose()


app = FastAPI(title="Veterinaria", version="1.0.0", lifespan=lifespan)

app.include_router(health_router)
app.include_router(duenios_router)
app.include_router(mascotas_router)
app.include_router(practicas_router)
app.include_router(turnos_router)
app.include_router(laboratorio_router)
