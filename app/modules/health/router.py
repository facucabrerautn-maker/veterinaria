from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.database import SessionDep
from app.modules.health import service
from app.modules.health.schemas import EstadoLive, EstadoReady

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=EstadoLive)
async def live() -> EstadoLive:
    """Indica que el proceso está vivo. No toca la base."""
    return EstadoLive(estado="vivo")


@router.get("/ready", response_model=EstadoReady, responses={503: {"model": EstadoReady}})
async def ready(session: SessionDep):
    """Indica si la base contesta (SELECT 1). Responde 503 si no lo hace."""
    if await service.base_responde(session):
        return EstadoReady(estado="listo", base_de_datos="ok")
    return JSONResponse(
        status_code=503,
        content={"estado": "no disponible", "base_de_datos": "sin respuesta"},
    )
