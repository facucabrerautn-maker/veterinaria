"""Deja la base en un estado conocido.

Borra las tablas, las crea con SQLModel.metadata.create_all y carga los datos
iniciales. Uso:  python reiniciar.py

ATENCIÓN: borra todos los datos de las tablas de la aplicación.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlmodel import SQLModel

import app.models  # noqa: F401  (registra todas las tablas)
from app.core.config import obtener_configuracion
from app.core.database import crear_fabrica_sesiones, crear_motor
from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica

ARGENTINA = timezone(timedelta(hours=-3))


async def cargar_datos_iniciales(session) -> None:
    # Dos dueños, uno con ficha.
    ana = Duenio(nombre="Ana García", email="ana@example.com")
    bruno = Duenio(nombre="Bruno Pérez", email="bruno@example.com")
    session.add_all([ana, bruno])
    await session.flush()  # asigna los ids

    session.add(
        FichaDuenio(duenio_id=ana.id, telefono="261-555-0101", direccion="San Martín 123, Las Heras")
    )

    # Tres mascotas.
    toby = Mascota(nombre="Toby", especie="perro", duenio_id=ana.id)
    michi = Mascota(nombre="Michi", especie="gato", duenio_id=ana.id)
    luna = Mascota(nombre="Luna", especie="perro", duenio_id=bruno.id)
    session.add_all([toby, michi, luna])

    # Cuatro prácticas (ids 1 a 4, en este orden).
    consulta = Practica(nombre="Consulta", precio=Decimal("15000.00"))
    desparasitacion = Practica(nombre="Desparasitación", precio=Decimal("8000.00"))
    vacuna = Practica(nombre="Vacuna antirrábica", precio=Decimal("12000.00"))
    limpieza = Practica(nombre="Limpieza dental", precio=Decimal("35000.00"))
    session.add_all([consulta, desparasitacion, vacuna, limpieza])
    await session.flush()

    # Un turno con dos prácticas; el precio se copia del catálogo y el total se calcula.
    reservadas = [consulta, desparasitacion]
    turno = Turno(
        mascota_id=toby.id,
        fecha=datetime(2026, 11, 10, 9, 0, tzinfo=ARGENTINA),
        motivo="Consulta y desparasitación",
        total=sum((p.precio for p in reservadas), Decimal("0")),
    )
    session.add(turno)
    await session.flush()
    session.add_all(
        [
            TurnoPractica(turno_id=turno.id, practica_id=p.id, precio_unitario=p.precio)
            for p in reservadas
        ]
    )
    await session.commit()


async def main() -> None:
    configuracion = obtener_configuracion()
    motor = crear_motor(configuracion.database_url, echo=False)
    try:
        async with motor.begin() as conexion:
            await conexion.run_sync(SQLModel.metadata.drop_all)
            await conexion.run_sync(SQLModel.metadata.create_all)
        print("Tablas recreadas.")

        fabrica = crear_fabrica_sesiones(motor)
        async with fabrica() as session:
            await cargar_datos_iniciales(session)
        print("Datos iniciales cargados: 2 dueños (1 con ficha), 3 mascotas, 4 prácticas, 1 turno con 2 prácticas.")
    finally:
        await motor.dispose()


if __name__ == "__main__":
    asyncio.run(main())
