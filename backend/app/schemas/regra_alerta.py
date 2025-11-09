from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RegraAlertaBase(BaseModel):
    usuario_email: str
    local_id: int
    sensor_tipo: str  # PH, UMIDADE, BOIA
    campo_sensor: str  # Campo do sensor (ex: 'ph', 'valor', 'umidade_percentual')
    operador: str  # Operador de comparação (>, <, >=, <=, ==, !=)
    valor_limite: float
    mensagem_alerta: Optional[str] = None
    ativa: bool = True


class RegraAlertaCreate(RegraAlertaBase):
    pass


class RegraAlertaUpdate(BaseModel):
    sensor_tipo: Optional[str] = None
    campo_sensor: Optional[str] = None
    operador: Optional[str] = None
    valor_limite: Optional[float] = None
    mensagem_alerta: Optional[str] = None
    ativa: Optional[bool] = None


class RegraAlerta(RegraAlertaBase):
    id: int
    data_criacao: datetime
    data_atualizacao: datetime

    model_config = ConfigDict(from_attributes=True)