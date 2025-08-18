from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_usuarios: int
    total_pedidos: int
    total_notificacoes: int
    usuarios_ativos: int
    dados_cisterna: dict

class ConfiguracaoBase(BaseModel):
    chave: str
    valor: str
    descricao: str

class ConfiguracaoCreate(ConfiguracaoBase):
    pass

class ConfiguracaoUpdate(BaseModel):
    valor: str
    descricao: Optional[str] = None

class Configuracao(ConfiguracaoBase):
    id: int
    data_atualizacao: datetime

    class Config:
        from_attributes = True

class AdminDashboard(BaseModel):
    stats: DashboardStats
    ultimas_notificacoes: List[dict]
    usuarios_recentes: List[dict]
    configuracoes: List[Configuracao]
