from sqlalchemy import Column, Integer, Float, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Local(Base):
    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)  # CISTERNA, AQUARIO, CASA, etc
    descricao = Column(String(200))
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamentos
    leituras_ph = relationship("PhNivel", back_populates="local")
    leituras_nivel = relationship("NivelAgua", back_populates="local")
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "data_criacao": self.data_criacao
        }

class PhNivel(Base):
    __tablename__ = "ph_niveis"

    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=False)
    ph = Column(Float, nullable=False)
    data = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamento
    local = relationship("Local", back_populates="leituras_ph")
    
    def to_dict(self):
        return {
            "id": self.id,
            "local_id": self.local_id,
            "ph": self.ph,
            "data": self.data
        }

class NivelAgua(Base):
    __tablename__ = "niveis_agua"

    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=False)
    boia = Column(Integer, nullable=False)  # Valor em porcentagem (0-100)
    status = Column(String(10), nullable=False)  # NORMAL, BAIXO, CRITICO
    data = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamento
    local = relationship("Local", back_populates="leituras_nivel")
    
    def to_dict(self):
        return {
            "id": self.id,
            "local_id": self.local_id,
            "boia": self.boia,
            "status": self.status,
            "data": self.data
        }
            "data": self.data
        }
    
    @staticmethod
    def calcular_status(boia: int) -> str:
        if boia >= 50:
            return "NORMAL"
        elif boia >= 25:
            return "BAIXO"
        else:
            return "CRITICO"
