from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    cpf: Optional[str] = None

class Login(BaseModel):
    cpf: constr(regex=r'^\d{11}$')  # CPF com 11 dígitos
    senha: str

class RegistroUsuario(BaseModel):
    nome: constr(min_length=3, max_length=100)
    cpf: constr(regex=r'^\d{11}$')
    email: EmailStr
    endereco: constr(max_length=200)
    senha: constr(min_length=6)

class RecuperacaoSenha(BaseModel):
    email: EmailStr

class ResetarSenha(BaseModel):
    token: str
    nova_senha: constr(min_length=6)
