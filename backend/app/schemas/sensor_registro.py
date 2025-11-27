from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SensorRegistroCreate(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome do sensor/local")
    tipo: str = Field(..., max_length=50, description="Tipo do sensor (CISTERNA, AQUARIO, etc)")
    descricao: Optional[str] = Field(None, max_length=200, description="Descrição opcional do sensor")

from .usuario import Usuario

class SensorRegistroResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    descricao: Optional[str]
    chave_api: str
    data_criacao: datetime

    class Config:
        from_attributes = True


class SensorDetalhesResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    descricao: Optional[str]
    chave_api: str
    data_criacao: datetime
    usuarios_associados: list[Usuario]

    class Config:
        from_attributes = True