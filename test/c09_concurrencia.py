"""C-09: tres consultas simultáneas al laboratorio y un GET /health/live.

Uso (con el servidor levantado):
    python test/c09_concurrencia.py

Resultado esperado:
- /health/live responde en pocos milisegundos, aunque haya 3 consultas al
  laboratorio en curso (cada una tarda ~1 s).
- Las 3 consultas al laboratorio terminan casi juntas (~1 s en total), no en
  serie (~3 s): el servidor las atiende en paralelo.
"""

import asyncio
import time

import httpx

BASE = "http://localhost:8000"


async def pedir(cliente: httpx.AsyncClient, etiqueta: str, ruta: str, inicio: float) -> None:
    respuesta = await cliente.get(ruta)
    transcurrido = time.perf_counter() - inicio
    print(f"{etiqueta:<14} -> {respuesta.status_code}  a los {transcurrido * 1000:7.0f} ms  {respuesta.text}")


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE, timeout=30) as cliente:
        inicio = time.perf_counter()
        tareas = [
            asyncio.create_task(pedir(cliente, f"laboratorio {i}", f"/laboratorio/stock/vacuna{i}", inicio))
            for i in range(1, 4)
        ]
        await asyncio.sleep(0.2)  # las 3 consultas ya están en curso
        await pedir(cliente, "health/live", "/health/live", inicio)
        await asyncio.gather(*tareas)
        print(f"\nTotal: {(time.perf_counter() - inicio) * 1000:.0f} ms (esperado: cerca de 1000 ms, no 3000)")


if __name__ == "__main__":
    asyncio.run(main())
