from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class Login(BaseModel):
    email: EmailStr
    senha: str

class RegistroUsuario(BaseModel):
    nome: constr(min_length=3, max_length=100)
    email: EmailStr
    endereco: constr(max_length=200)
    senha: constr(min_length=6)

class OAuthUserResponse(BaseModel):
    id: int
    nome: str
    email: str

class OAuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: OAuthUserResponse

class RecuperacaoSenha(BaseModel):
    email: EmailStr

class ResetarSenha(BaseModel):
    token: str
    nova_senha: constr(min_length=6)
