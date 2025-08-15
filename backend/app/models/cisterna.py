from sqlalchemy import Column, Integer, Float, String, DateTime, func
from app.db.base_class import Base

class PhNivel(Base):
    __tablename__ = "ph_niveis"

    id = Column(Integer, primary_key=True, index=True)
    ph = Column(Float, nullable=False)
    data = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "ph": self.ph,
            "data": self.data
        }

class NivelAgua(Base):
    __tablename__ = "niveis_agua"

    id = Column(Integer, primary_key=True, index=True)
    boia = Column(Integer, nullable=False)  # Valor em porcentagem (0-100)
    status = Column(String(10), nullable=False)  # NORMAL, BAIXO, CRITICO
    data = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "boia": self.boia,
            "status": self.status,
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
