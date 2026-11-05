# Carpeta test/

Casos de prueba del trabajo práctico. Cada caso indica en un comentario la respuesta esperada.
Se corren **después** de `python reiniciar.py`, con el servidor levantado.

| Archivo | Casos que cubre |
|---|---|
| `00_health.http` | Salud del servicio (ejercicio 1) |
| `01_duenios.http` | C-01, C-02 (email), C-03, C-05 (dueño), PATCH, fichas |
| `02_practicas.http` | C-02 (nombre), RN-04 |
| `03_mascotas.http` | C-04 (mascota), paginación |
| `04_turnos.http` | C-04 (turno), C-05 (turno), C-06, C-07, RN-05, RN-07 |
| `05_laboratorio.http` | Laboratorio y C-09 (manual) |
| `c09_concurrencia.py` | C-09 automático (3 consultas al laboratorio + `/health/live`) |
| `c08_check_precio.sql` | C-08 (CHECK de la base) |
| `verificaciones.sql` | Comprobaciones en la base para C-04 y C-05 |

Los `.http` usan la sintaxis de la extensión **REST Client** de VS Code.
