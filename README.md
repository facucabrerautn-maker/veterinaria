# Veterinaria — API con FastAPI y PostgreSQL
## Integrantes: Facundo Cabrera, Nahuel Olmos, Agustin Pereyra, Ignacio Ariza

Trabajo práctico de Programación III (Tecnicatura Universitaria en Programación, UTN).
API asincrónica para registrar dueños, mascotas, prácticas y turnos de una veterinaria.

**Tecnologías:** Python 3.12, FastAPI, SQLModel, SQLAlchemy 2.0 (asincrónico), asyncpg, PostgreSQL 16.

---

## Cómo levantar el proyecto desde cero (Windows)

### 1. Requisitos
- Python 3.12 o superior (`python --version`).
- PostgreSQL 16 instalado y en marcha (instalador de https://www.postgresql.org/download/windows/).
  Alternativa con Docker:
  ```
  docker run --name pg-veterinaria -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=veterinaria -p 5432:5432 -d postgres:16
  ```
  (con esta opción la base `veterinaria` ya queda creada y se puede saltar el paso 2).

### 2. Crear la base de datos
Con `psql` (o desde pgAdmin, botón derecho en *Databases → Create → Database*):
```
psql -U postgres -c "CREATE DATABASE veterinaria;"
```

### 3. Entorno virtual y dependencias
En PowerShell, parado en la carpeta del proyecto:
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Si PowerShell bloquea el script de activación, ejecutar una vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, o usar `cmd` con `.venv\Scripts\activate.bat`.

### 4. Configurar el archivo `.env`
```
copy env.example .env
```
Abrir `.env` y completar `DATABASE_URL` con el usuario, la contraseña, el puerto y la base:
```
DATABASE_URL=postgresql+asyncpg://postgres:TU_CONTRASENA@localhost:5432/veterinaria
```
Si la contraseña tiene caracteres especiales (`@`, `:`, `/`, `#`, `%`) hay que codificarlos
(por ejemplo, `@` se escribe `%40`). El archivo `.env` no se sube al repositorio.

### 5. Crear el esquema y cargar los datos iniciales
```
python reiniciar.py
```
Borra las tablas, las crea con `SQLModel.metadata.create_all` y carga: 2 dueños (uno con ficha),
3 mascotas, 4 prácticas y 1 turno con 2 prácticas. Se puede correr las veces que haga falta.

### 6. Arrancar el servidor
```
fastapi dev app/main.py
```
(o `uvicorn app.main:app --reload`). La documentación interactiva queda en http://localhost:8000/docs.

### 7. Probar
Los casos de prueba están en la carpeta `test/` (archivos `.http` para la extensión *REST Client*
de VS Code, más dos `.sql` y un script de concurrencia). Ver `test/README.md`.
Siempre se corren después de `python reiniciar.py`.

---

## Estructura

```
app/
  main.py                  aplicación, lifespan y registro de routers
  models.py                importa todos los modelos (registra el esquema completo)
  core/
    config.py              lectura de DATABASE_URL desde el entorno
    database.py            motor, fábrica de sesiones y dependencia get_session
    errores.py             ayuda para distinguir el tipo de restricción violada
  modules/<módulo>/
    models.py              tablas, restricciones y relaciones
    schemas.py             DTO de entrada (Create, Update) y de salida (Read)
    service.py             lógica, traducción de errores y lecturas con precarga
    router.py              rutas HTTP: reciben, delegan y declaran la respuesta
reiniciar.py               borra, crea y carga los datos iniciales
test/                      casos de prueba
```
Módulos: `health`, `duenios` (con `FichaDuenio`), `mascotas`, `practicas`, `turnos` (con `TurnoPractica`) y `laboratorio`.

---

## Decisiones de diseño

### Lado de cada clave foránea

| Relación | Clave foránea | Por qué va de ese lado |
|---|---|---|
| Uno a uno: dueño–ficha | `ficha_duenio.duenio_id` **UNIQUE** | La ficha es la parte opcional y depende del dueño; con la clave del lado de la ficha no hace falta una columna que admita nulos en `duenio`. El `UNIQUE` es lo que convierte el 1-a-N en 1-a-1 (RN-03). Se agregó `ON DELETE CASCADE` para que borrar un dueño sin mascotas borre también su ficha. |
| Agregación: dueño–mascota | `mascota.duenio_id` `ON DELETE RESTRICT` | Un dueño tiene muchas mascotas: la clave va del lado «muchos». `RESTRICT` impide borrar un dueño con mascotas (RN-08), porque la mascota existe por sí misma. |
| Asociación: turno–mascota | `turno.mascota_id` | Un turno es de una sola mascota; la clave va del lado «muchos» (turno). Ninguno es parte del otro, por eso no hay cascada. |
| Composición: turno–prácticas | `turno_practica.turno_id` `ON DELETE CASCADE` | Una práctica reservada nace y muere con su turno (RN-09). |
| Muchos a muchos con datos | `turno_practica.turno_id` + `turno_practica.practica_id` | La tabla intermedia lleva las dos claves y el dato propio de la relación: `precio_unitario`, el precio congelado al reservar (RN-06). |

### Por qué `turno_practica.turno_id` no lleva índice propio

`turno_id` es la **primera columna de la clave primaria compuesta** `(turno_id, practica_id)`, y PostgreSQL
ya crea un índice único para esa clave que sirve para buscar por `turno_id`; un índice aparte sería redundante.
En cambio `practica_id` es la segunda columna, así que la clave primaria no sirve para buscar por ella y
por eso sí lleva su propio índice.

### Garantías que delega en la base
- `UNIQUE`: `duenio.email` (RN-01), `practica.nombre` (RN-02), `ficha_duenio.duenio_id` (RN-03).
- `CHECK`: `practica.precio > 0` (RN-04), `turno.total >= 0`, `turno_practica.precio_unitario > 0`.
- Clave primaria compuesta de `turno_practica`: una práctica no se repite en un turno (RN-07).
- `ON DELETE RESTRICT` y `CASCADE`: RN-08 y RN-09.

Ninguna regla se verifica con una consulta previa «¿ya existe?»: se escribe, y si la base rechaza la
escritura, el `service` atrapa `IntegrityError`, deshace la transacción y responde 409 con un mensaje propio.
La única lectura previa es la del catálogo al reservar un turno, que es necesaria para copiar los precios (RN-06).

### Borrados y `passive_deletes`
Las relaciones `Duenio.ficha`, `Duenio.mascotas`, `Mascota.turnos` y `Turno.practicas` se declaran con
`passive_deletes=True`: el ORM no carga ni intenta vaciar esas filas al borrar el objeto padre, y deja que
decida la base (`CASCADE` o `RESTRICT`). Además evita una carga perezosa, que en un contexto asincrónico fallaría
con `MissingGreenlet`.

### Lecturas sin N+1
| Lectura | Estrategia | Consultas |
|---|---|---|
| Dueño con su ficha | `joinedload` (relación «a uno») | 1 |
| Mascota con su dueño | `joinedload` | 1 |
| Turno con mascota y prácticas | `joinedload(mascota)` + `selectinload(practicas)` con `joinedload(practica)` encadenado | 2, siempre |

La sesión se crea con `expire_on_commit=False`, y después de cada escritura el `service` relee el objeto con sus
relaciones cargadas antes de responder, para no depender nunca de la carga perezosa.

### Asincronía
Todos los handlers son `async def`. La biblioteca del laboratorio (`consultar_stock`) es sincrónica y no se
modifica: se la llama con `asyncio.to_thread`, en un hilo aparte, así el bucle de eventos sigue atendiendo
(por ejemplo `/health/live`) mientras el laboratorio responde.

### Dinero y fechas
El dinero se representa con `Decimal` en Python y `NUMERIC` en la base, nunca con `float`. Las fechas del turno
llevan zona horaria (`TIMESTAMPTZ`); la API rechaza con 422 una fecha sin zona horaria y responde en UTC.

---

## Evidencia del caso C-07
Ver `evidencia_c07.md`.
