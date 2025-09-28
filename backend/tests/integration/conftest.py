# backend/tests/integration/conftest.py
import pytest
from typing import Generator, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Import all necessary models
from backend.app.db.base_class import Base
from backend.app.main import app
from backend.app.api.deps import get_db as app_get_db
from backend.app.models import Usuario, PhNivel, NivelAgua, Local, Notificacao, UsuarioSensor
from backend.app.models.admin import Admin
from backend.app.core.security import get_password_hash
from backend.app.core.config import settings

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

@pytest.fixture(scope="function")
def test_admin(db) -> Admin:
    """Fixture para criar e salvar um usuário administrador no banco de dados de teste."""
    admin_obj = Admin(
        nome="Admin Teste",
        cpf="12345678901",
        email=settings.FIRST_SUPERUSER,
        senha_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
    )
    db.add(admin_obj)
    db.commit()
    db.refresh(admin_obj)
    return admin_obj

@pytest.fixture(scope="function")
def admin_auth_headers(client, test_admin) -> Dict[str, str]:
    """Fixture para obter os cabeçalhos de autenticação para o usuário administrador de teste."""
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"/api/v1/admin/login", data=login_data)
    if r.status_code != 200:
        raise Exception(f"Não foi possível fazer login do usuário admin para os testes. Status: {r.status_code}, Body: {r.text}")
    
    response_json = r.json()
    token = response_json.get("access_token")
    if not token:
        raise Exception(f"A resposta do login de admin não incluiu um access_token. Resposta: {response_json}")
        
    headers = {"Authorization": f"Bearer {token}"}
    return headers

@pytest.fixture(scope="function")
def test_user(db) -> Usuario:
    """Fixture para criar e salvar um usuário comum no banco de dados de teste."""
    user_obj = Usuario(
        nome="Test User",
        email="test.user@example.com",
        senha_hash=get_password_hash("testpassword"),
        endereco="123 Test St"
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

@pytest.fixture(scope="function")
def user_auth_headers(client, test_user) -> Dict[str, str]:
    """Fixture para obter os cabeçalhos de autenticação para um usuário comum de teste."""
    login_data = {
        "email": test_user.email,
        "senha": "testpassword",
    }
    r = client.post(f"/api/v1/auth/login", json=login_data)
    if r.status_code != 200:
        raise Exception(f"Não foi possível fazer login do usuário para os testes. Status: {r.status_code}, Body: {r.text}")
    
    response_json = r.json()
    token = response_json.get("access_token")
    if not token:
        raise Exception(f"A resposta do login de usuário não incluiu um access_token. Resposta: {response_json}")
        
    headers = {"Authorization": f"Bearer {token}"}
    return headers