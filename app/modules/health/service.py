from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession


async def base_responde(session: AsyncSession) -> bool:
    """Ejecuta SELECT 1. Devuelve False ante cualquier falla de conexión."""
    try:
        await session.exec(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 - cualquier falla significa "base no disponible"
        return False
