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
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)

class PhNivelBase(BaseModel):
    ph: float = Field(..., ge=0, le=14, description="Nível de pH da água (0-14)")
    data: datetime = Field(default_factory=datetime.now)

    @field_validator('ph')
    def validar_ph(cls, v):
        if not 0 <= v <= 14:
            raise ValueError('O pH deve estar entre 0 e 14')
        return round(v, 2)

class PhNivelCreate(PhNivelBase):
    pass

class PhNivel(PhNivelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class NivelAguaBase(BaseModel):
    boia: int = Field(..., ge=0, le=100, description="Nível da boia em porcentagem")
    status: Literal['NORMAL', 'BAIXO', 'CRITICO'] = Field(
        ..., 
        description="Status do nível de água"
    )
    data: datetime = Field(default_factory=datetime.now)

    @field_validator('status')
    def validar_status(cls, v):
        status_permitidos = ['NORMAL', 'BAIXO', 'CRITICO']
        if v not in status_permitidos:
            raise ValueError(f'Status deve ser um dos seguintes: {status_permitidos}')
        return v

    @field_validator('boia')
    def validar_boia(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('O nível da boia deve estar entre 0 e 100')
        return v

class NivelAguaCreate(NivelAguaBase):
    pass

class NivelAgua(NivelAguaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class DadosCisternaResponse(BaseModel):
    ph_atual: Optional[PhNivel]
    nivel_atual: Optional[NivelAgua]
    historico_ph: list[PhNivel]
    historico_nivel: list[NivelAgua]

    model_config = ConfigDict(from_attributes=True)
