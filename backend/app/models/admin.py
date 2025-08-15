from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from ..db.base_class import Base

class Configuracao(Base):
    __tablename__ = "configuracoes"

    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String(50), unique=True, index=True, nullable=False)
    valor = Column(Text, nullable=False)
    descricao = Column(Text)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
