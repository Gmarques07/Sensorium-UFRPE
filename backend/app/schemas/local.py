from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Literal

class LocalBase(BaseModel):
    nome: str = Field(..., max_length=100)
    tipo: str = Field(..., max_length=50)  # CISTERNA, AQUARIO, CASA, etc
    descricao: Optional[str] = Field(None, max_length=200)

class LocalCreate(LocalBase):
    pass

class Local(LocalBase):
    id: int
    chave_api: Optional[str] = None
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
