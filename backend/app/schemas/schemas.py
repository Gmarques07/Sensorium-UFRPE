from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    endereco: str

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    senha: Optional[str] = None

class Usuario(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PhNivelBase(BaseModel):
    ph: float
    dispositivo_id: int

class PhNivel(PhNivelBase):
    id: int
    data: datetime

    class Config:
        from_attributes = True

class NivelAguaBase(BaseModel):
    boia: float
    status: str
    dispositivo_id: int

class NivelAgua(NivelAguaBase):
    id: int
    data: datetime

    class Config:
        from_attributes = True
