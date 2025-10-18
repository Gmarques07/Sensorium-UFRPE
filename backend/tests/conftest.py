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
from backend.app.models import Usuario, Local, Leitura, PhNivel, BoiaNivel

import os

# Usa o banco de dados de teste MySQL fornecido pelo ambiente Docker
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootpassword")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
# Importante: Usar o banco de dados de teste, que é definido no docker-compose para o serviço mysql
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE_TEST", "sensorium_test_db") 

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
    # Cria um usuário único para cada teste usando timestamp
    import time
    timestamp = int(time.time() * 1000)
    email = f"teste{timestamp}@example.com"
    
    usuario = Usuario(
        nome="Usuario Teste",
        email=email,
        endereco="Rua de Teste, 123",
        ativo=True,
    )
    usuario.set_senha("senha123")
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

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

    leitura_ph = Leitura(local_id=local.id, sensor_tipo='PH')
    db.add(leitura_ph)
    db.commit()
    db.refresh(leitura_ph)

    ph = PhNivel(leitura_id=leitura_ph.id, ph=7.0)
    db.add(ph)
    db.commit()
    db.refresh(ph)

    leitura_boia = Leitura(local_id=local.id, sensor_tipo='BOIA')
    db.add(leitura_boia)
    db.commit()
    db.refresh(leitura_boia)

    nivel = BoiaNivel(leitura_id=leitura_boia.id, valor=80, status='ALTO')
    db.add(nivel)
    db.commit()
    db.refresh(nivel)

    return {"local_id": local.id, "ph_leitura_id": leitura_ph.id, "boia_leitura_id": leitura_boia.id}