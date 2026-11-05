from pydantic import BaseModel


class EstadoLive(BaseModel):
    estado: str


class EstadoReady(BaseModel):
    estado: str
    base_de_datos: str
