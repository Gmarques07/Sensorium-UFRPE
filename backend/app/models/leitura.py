from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.base_class import Base

class Leitura(Base):
    __tablename__ = 'leituras'
    id = Column(Integer, primary_key=True, autoincrement=True)
    local_id = Column(Integer, ForeignKey('locais.id'), nullable=False)
    sensor_tipo = Column(Enum('PH', 'UMIDADE', 'BOIA'), nullable=False)
    data = Column(DateTime, nullable=False, default=func.now())
    local = relationship("Local", back_populates="leituras")

class PhNivel(Base):
    __tablename__ = 'ph_niveis'
    leitura_id = Column(Integer, ForeignKey('leituras.id'), primary_key=True)
    ph = Column(Float, nullable=False)
    leitura = relationship("Leitura")

class UmidadeNivel(Base):
    __tablename__ = 'umidade_niveis'
    leitura_id = Column(Integer, ForeignKey('leituras.id'), primary_key=True)
    raw = Column(Integer, nullable=False)
    umidade_percentual = Column(Float, nullable=False)
    status = Column(Enum('SECO', 'UMIDO', 'ENCHARCADO'), nullable=False)
    leitura = relationship("Leitura")

class BoiaNivel(Base):
    __tablename__ = 'boia_niveis'
    leitura_id = Column(Integer, ForeignKey('leituras.id'), primary_key=True)
    valor = Column(Integer, nullable=False)
    status = Column(Enum('BAIXO', 'ALTO'), nullable=False)
    leitura = relationship("Leitura")

class EstadoLuz(Base):
    __tablename__ = 'estados_luz'
    id = Column(Integer, primary_key=True, autoincrement=True)
    estado = Column(String(20), nullable=False)
    horario = Column(DateTime, nullable=False)
