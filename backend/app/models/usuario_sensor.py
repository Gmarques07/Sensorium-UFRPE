from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.base_class import Base

class UsuarioSensor(Base):
    __tablename__ = "usuario_sensor"

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True, nullable=False)
    sensor_id = Column(Integer, ForeignKey("locais.id"), primary_key=True, nullable=False)
    data_atribuicao = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="sensores_atribuidos")
    sensor = relationship("Local", back_populates="usuarios_atribuidos")