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

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_senha(self, senha: str):
        from backend.app.core.security import get_password_hash
        self.senha_hash = get_password_hash(senha)

    def verificar_senha(self, senha: str) -> bool:
        from backend.app.core.security import verify_password
        return verify_password(senha, self.senha_hash)
