# backend/tests/integration/conftest.py
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Import all necessary models
from backend.app.db.base_class import Base
from backend.app.main import app
from backend.app.api.deps import get_db as app_get_db
from backend.app.models import Usuario, PhNivel, NivelAgua, Local, Notificacao, UsuarioSensor

# Banco SQLite em memória compartilhado entre conexões para testes de integração
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator:
    """Cria um banco de dados limpo e isolado para cada teste de integração"""
    # Isola cada teste com um schema limpo
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Cliente de teste com banco de dados isolado"""
    def override_get_db():
        yield db

    # Override da dependência de DB para usar o banco de testes
    app.dependency_overrides[app_get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()