from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class NotificacaoBase(BaseModel):
    mensagem: str
    pedido_id: int
    cpf_usuario: Optional[str] = None
    cnpj_empresa: Optional[str] = None

class NotificacaoCreate(NotificacaoBase):
    pass

class NotificacaoUpdate(BaseModel):
    mensagem: Optional[str] = None
    lida: Optional[bool] = None

class Notificacao(NotificacaoBase):
    id: int
    data_criacao: datetime
    lida: bool = False
    data_leitura: Optional[datetime] = None

    class Config:
        orm_mode = True

class NotificacaoAdmin(BaseModel):
    id: int
    tipo: str
    titulo: str
    mensagem: str
    data_criacao: datetime
    lida: bool = False
    data_leitura: Optional[datetime] = None

    class Config:
        orm_mode = True
