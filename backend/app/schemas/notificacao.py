from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class NotificacaoBase(BaseModel):
    mensagem: str
    local_id: Optional[int] = None
    email_usuario: Optional[str] = None
    tipo: str

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
        from_attributes = True

class NotificacaoAdmin(BaseModel):
    id: int
    tipo: str
    titulo: str
    mensagem: str
    data_criacao: datetime
    lida: bool = False
    data_leitura: Optional[datetime] = None

    class Config:
        from_attributes = True
