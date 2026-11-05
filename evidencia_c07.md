# Evidencia del caso C-07

> **PENDIENTE: este archivo es una plantilla. Reemplazar los bloques vacíos con la salida real de la consola.**

Detalle de un turno con una práctica y con tres: la cantidad de consultas debe ser la misma.

## Cómo generar la evidencia

1. En `.env`, poner `SQL_ECHO=true`.
2. Correr `python reiniciar.py` y arrancar el servidor (`fastapi dev app/main.py`).
3. Con `test/04_turnos.http`, crear el turno con **una** práctica y el turno con **tres**
   (pedidos «C-07 (preparación)»).
4. Pedir el detalle de cada uno (pedidos «C-07: detalle...») y copiar de la consola
   **solo las consultas del `GET`**, desde el primer `SELECT` hasta el último.
5. Volver a poner `SQL_ECHO=false`.

## Detalle de un turno con UNA práctica

```
SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, mascota_1.id AS id_1, mascota_1.nombre, mascota_1.especie, mascota_1.duenio_id FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id WHERE turno.id = $1::INTEGER
```

Cantidad de consultas: ___

## Detalle de un turno con TRES prácticas

```
(pegar aquí las consultas de la consola)
```

Cantidad de consultas: ___

## Conclusión

La cantidad de consultas es la misma en los dos casos (2 `SELECT`: uno sobre `turno` con `JOIN` a `mascota`, y
otro sobre `turno_practica` con `JOIN` a `practica`), porque la mascota se carga con `joinedload` y las prácticas
con `selectinload`, en lugar de una consulta por cada práctica (problema N+1).
