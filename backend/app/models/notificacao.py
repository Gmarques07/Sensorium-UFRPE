from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    mensagem = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    cpf_usuario = Column(String(11))
    cnpj_empresa = Column(String(14))
    lida = Column(Boolean, default=False)
    data_leitura = Column(DateTime, nullable=True)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="notificacoes")


class NotificacaoAdmin(Base):
    __tablename__ = "notificacoes_admin"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    titulo = Column(String(200), nullable=False)
    mensagem = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    lida = Column(Boolean, default=False)
    data_leitura = Column(DateTime, nullable=True)
