from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from app.db.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(11), unique=True, index=True)
    nome = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    endereco = Column(String(200))
    senha_hash = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PhNivel(Base):
    __tablename__ = "ph_niveis"

    id = Column(Integer, primary_key=True, index=True)
    ph = Column(Float)
    data = Column(DateTime, default=datetime.utcnow)
    dispositivo_id = Column(Integer)

class NivelAgua(Base):
    __tablename__ = "niveis_agua"

    id = Column(Integer, primary_key=True, index=True)
    boia = Column(Float)
    status = Column(String(50))
    data = Column(DateTime, default=datetime.utcnow)
    dispositivo_id = Column(Integer)
