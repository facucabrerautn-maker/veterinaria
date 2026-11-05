import asyncio

from app.modules.laboratorio.cliente import consultar_stock
from app.modules.laboratorio.schemas import StockRead


async def stock_de(vacuna: str) -> StockRead:
    """Consulta el stock sin bloquear el bucle de eventos.

    consultar_stock es sincrónica (time.sleep) y no se puede modificar. Llamarla
    directo desde un handler async congelaría TODO el servidor durante un
    segundo. asyncio.to_thread la ejecuta en un hilo aparte y el bucle de
    eventos sigue atendiendo otras peticiones (por ejemplo /health/live).
    """
    cantidad = await asyncio.to_thread(consultar_stock, vacuna)
    return StockRead(vacuna=vacuna, stock=cantidad)
