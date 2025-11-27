from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal, List

class LeituraBase(BaseModel):
    local_id: int
    sensor_tipo: Literal['PH', 'UMIDADE', 'BOIA']

class LeituraCreate(LeituraBase):
    pass

class Leitura(LeituraBase):
    id: int
    data: datetime

    model_config = ConfigDict(from_attributes=True)

class PhNivelBase(BaseModel):
    ph: float = Field(..., ge=0, le=14)

class PhNivelCreate(PhNivelBase):
    pass

class PhNivel(PhNivelBase):
    leitura_id: int

    model_config = ConfigDict(from_attributes=True)

class UmidadeNivelBase(BaseModel):
    raw: int
    umidade_percentual: float
    status: Literal['SECO', 'UMIDO', 'ENCHARCADO']

class UmidadeNivelCreate(UmidadeNivelBase):
    pass

class UmidadeNivel(UmidadeNivelBase):
    leitura_id: int

    model_config = ConfigDict(from_attributes=True)

class BoiaNivelBase(BaseModel):
    valor: int
    status: Literal['BAIXO', 'ALTO']

class BoiaNivelCreate(BoiaNivelBase):
    pass

class BoiaNivel(BoiaNivelBase):
    leitura_id: int

    model_config = ConfigDict(from_attributes=True)

class EstadoLuzBase(BaseModel):
    estado: str
    horario: datetime

class EstadoLuzCreate(EstadoLuzBase):
    pass

class EstadoLuz(EstadoLuzBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class DadosCisternaResponse(BaseModel):
    ph_atual: Optional[PhNivel]
    nivel_atual: Optional[BoiaNivel]
    umidade_atual: Optional[UmidadeNivel]
    historico_ph: List[PhNivel]
    historico_nivel: List[BoiaNivel]
    historico_umidade: List[UmidadeNivel]

    model_config = ConfigDict(from_attributes=True)

class LeituraPayload(BaseModel):
    ph: float
    boia: int
    status_boia: str
    umidade_raw: Optional[int] = None
    umidade_percentual: Optional[float] = None
    umidade_status: Optional[str] = None
    dispositivo_id: int
