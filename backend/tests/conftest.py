import pytest
from typing import Generator, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.app.db.base_class import Base
from backend.app.main import app
from backend.app.api.deps import get_db as app_get_db
from backend.app.core.security import create_access_token
from backend.app.models import Usuario, PhNivel, NivelAgua, Local

# Banco SQLite em memória compartilhado entre conexões
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator:
    # Isola cada teste com um schema limpo
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client() -> Generator:
    def override_get_db() -> Generator:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    # Override da dependência de DB para usar o SQLite de testes
    from backend.app.api import deps
    deps.get_db = override_get_db
    app.dependency_overrides[app_get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def usuario_normal(db) -> Dict[str, str]:
    # Evita violação de UNIQUE ao reutilizar email em múltiplos testes
    existing = db.query(Usuario).filter(Usuario.email == "teste@example.com").first()
    if existing is None:
        usuario = Usuario(
            nome="Usuario Teste",
            email="teste@example.com",
            endereco="Rua de Teste, 123",
            ativo=True,
        )
        usuario.set_senha("senha123")
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    else:
        usuario = existing

    token = create_access_token({"sub": usuario.email})
    return {
        "id": str(usuario.id),
        "email": usuario.email,
        "token": f"Bearer {token}",
    }

@pytest.fixture(scope="function")
def headers_autenticado(usuario_normal) -> Dict[str, str]:
    return {"Authorization": usuario_normal["token"]}

@pytest.fixture(scope="function")
def dados_cisterna(db) -> Dict[str, int]:
    local = Local(nome="Cisterna Principal", tipo="CISTERNA", descricao="Teste")
    db.add(local)
    db.commit()
    db.refresh(local)

    ph = PhNivel(local_id=local.id, ph=7.0)
    nivel = NivelAgua(local_id=local.id, boia=80, status=NivelAgua.calcular_status(80))
    db.add(ph)
    db.add(nivel)
    db.commit()
    db.refresh(ph)
    db.refresh(nivel)

    return {"local_id": local.id, "ph_id": ph.id, "nivel_id": nivel.id}