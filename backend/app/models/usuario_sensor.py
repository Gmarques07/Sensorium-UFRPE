from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.base_class import Base

class UsuarioSensor(Base):
    __tablename__ = "usuario_sensor"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=False)
    data_atribuicao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="sensores_atribuidos")
    sensor = relationship("Local", back_populates="usuarios_atribuidos")