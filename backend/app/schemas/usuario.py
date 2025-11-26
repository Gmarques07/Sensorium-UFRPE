from pydantic import BaseModel, EmailStr, constr, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

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

    @field_validator('nome')
    def validar_nome(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Nome não pode ser vazio')
            if len(v.strip()) < 3:
                raise ValueError('Nome deve ter pelo menos 3 caracteres')
        return v

class UsuarioInDB(UsuarioBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Usuario(UsuarioBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ativo: bool = True
    
    model_config = ConfigDict(from_attributes=True)
