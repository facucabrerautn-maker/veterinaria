from pydantic import BaseModel


class StockRead(BaseModel):
    vacuna: str
    stock: int
