from sqlalchemy import Column, Integer, Float, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base_class import Base

class Local(Base):
    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)  # CISTERNA, AQUARIO, CASA, etc
    descricao = Column(String(200))
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamentos
    notificacoes = relationship("Notificacao", foreign_keys="[Notificacao.local_id]")
    usuarios_atribuidos = relationship("UsuarioSensor", back_populates="sensor")
    leituras = relationship("Leitura", back_populates="local")
    regras_alerta = relationship("RegraAlerta", back_populates="local")
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "data_criacao": self.data_criacao
        }