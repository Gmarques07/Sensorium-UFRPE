from fastapi.testclient import TestClient
from backend.app.core.config import settings
from backend.app.core.security import create_access_token

def test_criar_token(client: TestClient, usuario_normal):
    token = create_access_token({"sub": usuario_normal["email"]})
    assert token is not None
    assert len(token) > 0

def test_login_sucesso(client: TestClient, usuario_normal):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "email": usuario_normal["email"],
            "senha": "senha123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

def test_login_invalido(client: TestClient, usuario_normal):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "email": usuario_normal["email"],
            "senha": "senha_errada"
        }
    )
    assert response.status_code == 401

def test_token_invalido(client: TestClient):
    response = client.get(
        f"{settings.API_V1_STR}/usuarios/perfil",
        headers={"Authorization": "Bearer token_invalido"}
    )
    assert response.status_code == 401

def test_registro_usuario(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/auth/registro",
        json={
            "nome": "Novo Usuario",
            "email": "novo@example.com",
            "endereco": "Novo Endereco",
            "senha": "novasenha123"
        }
    )
    assert response.status_code == 200
    dados = response.json()
    assert "access_token" in dados