from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    mensagem = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=True)
    cpf_usuario = Column(String(11), nullable=True)
    tipo = Column(String(50), nullable=False)  # NIVEL_BAIXO, PH_ALTERADO, MANUTENCAO, etc
    lida = Column(Boolean, default=False)
    data_leitura = Column(DateTime, nullable=True)

    # Relacionamentos
    local = relationship("Local", foreign_keys=[local_id], overlaps="notificacoes")


class NotificacaoAdmin(Base):
    __tablename__ = "notificacoes_admin"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    titulo = Column(String(200), nullable=False)
    mensagem = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    lida = Column(Boolean, default=False)
    data_leitura = Column(DateTime, nullable=True)
