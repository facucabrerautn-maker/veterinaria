from fastapi import APIRouter

from app.modules.laboratorio import service
from app.modules.laboratorio.schemas import StockRead

router = APIRouter(prefix="/laboratorio", tags=["laboratorio"])


@router.get("/stock/{vacuna}", response_model=StockRead)
async def stock_de_vacuna(vacuna: str):
    return await service.stock_de(vacuna)
