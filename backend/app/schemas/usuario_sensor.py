from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UsuarioSensorBase(BaseModel):
    usuario_id: int
    sensor_id: int

class UsuarioSensorCreate(UsuarioSensorBase):
    pass

class UsuarioSensorUpdate(BaseModel):
    usuario_id: Optional[int] = None
    sensor_id: Optional[int] = None

class UsuarioSensorInDB(UsuarioSensorBase):
    usuario_id: int
    sensor_id: int
    data_atribuicao: datetime
    ativo: bool
    
    class Config:
        from_attributes = True

class UsuarioSensor(UsuarioSensorBase):
    usuario_id: int
    sensor_id: int
    data_atribuicao: datetime
    ativo: bool
    
    class Config:
        from_attributes = True