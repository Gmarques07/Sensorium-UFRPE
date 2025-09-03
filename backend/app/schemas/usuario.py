from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    cpf: constr(pattern=r'^\d{11}$')  # Validação de CPF com 11 dígitos
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

class UsuarioInDB(UsuarioBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Usuario(UsuarioBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ativo: bool = True
    
    class Config:
        from_attributes = True
