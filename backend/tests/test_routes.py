from fastapi.testclient import TestClient
from app.core.config import settings

def test_login(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "12345678901", "password": "senha123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_perfil(client: TestClient, headers_autenticado):
    response = client.get(
        f"{settings.API_V1_STR}/usuarios/perfil",
        headers=headers_autenticado
    )
    assert response.status_code == 200
    dados = response.json()
    assert dados["email"] == "teste@example.com"

def test_dados_cisterna(client: TestClient, headers_autenticado, dados_cisterna):
    response = client.get(
        f"{settings.API_V1_STR}/cisterna/dados-atuais",
        headers=headers_autenticado
    )
    assert response.status_code == 200
    dados = response.json()
    assert "ph_atual" in dados
    assert "nivel_atual" in dados
    
def test_registrar_leitura_ph(client: TestClient, headers_autenticado):
    response = client.post(
        f"{settings.API_V1_STR}/cisterna/registrar-leitura",
        headers=headers_autenticado,
        json={"tipo": "ph", "valor": 7.2}
    )
    assert response.status_code == 200
    dados = response.json()
    assert dados["ph"] == 7.2

def test_acesso_nao_autorizado(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/usuarios/perfil")
    assert response.status_code == 401
