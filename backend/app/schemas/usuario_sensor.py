from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UsuarioSensorBase(BaseModel):
    usuario_id: int
    local_id: int

class UsuarioSensorCreate(UsuarioSensorBase):
    pass

class UsuarioSensorUpdate(BaseModel):
    usuario_id: Optional[int] = None
    local_id: Optional[int] = None

class UsuarioSensorInDB(UsuarioSensorBase):
    id: int
    data_atribuicao: datetime
    
    class Config:
        from_attributes = True

class UsuarioSensor(UsuarioSensorBase):
    id: int
    data_atribuicao: datetime
    
    class Config:
        from_attributes = True