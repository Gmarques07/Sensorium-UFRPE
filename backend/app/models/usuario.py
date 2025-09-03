from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.core.security import get_password_hash, verify_password

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    endereco = Column(String(200), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def set_senha(self, senha: str):
        self.senha_hash = get_password_hash(senha)

    def verificar_senha(self, senha: str) -> bool:
        return verify_password(senha, self.senha_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "endereco": self.endereco,
            "ativo": self.ativo,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
