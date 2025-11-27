from fastapi.testclient import TestClient
from backend.app.core.config import settings

def test_login(client: TestClient, usuario_normal):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": usuario_normal["email"], "senha": "senha123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_perfil(client: TestClient, usuario_normal):
    # Primeiro, faz o login para obter o cookie de autenticação
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": usuario_normal["email"], "senha": "senha123"}
    )
    assert login_response.status_code == 200

    # Agora, a TestClient tem o cookie e o enviará automaticamente
    response = client.get(
        f"{settings.API_V1_STR}/usuarios/perfil"
    )
    assert response.status_code == 200
    dados = response.json()
    assert "email" in dados
    assert dados["email"] == usuario_normal["email"]

def test_dados_cisterna(client: TestClient, usuario_normal, dados_cisterna):
    # Login para obter o cookie
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": usuario_normal["email"], "senha": "senha123"}
    )
    assert login_response.status_code == 200

    # O cookie é enviado automaticamente
    response = client.get(
        f"{settings.API_V1_STR}/locais/dados-atuais"
    )
    assert response.status_code == 200
    dados = response.json()
    assert "ph_atual" in dados
    assert "nivel_atual" in dados
    
def test_registrar_leitura_ph(client: TestClient, usuario_normal, dados_cisterna):
    # Login para obter o cookie
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": usuario_normal["email"], "senha": "senha123"}
    )
    assert login_response.status_code == 200

    # O cookie é enviado automaticamente
    response = client.post(
        f"{settings.API_V1_STR}/locais/{dados_cisterna['local_id']}/registrar-ph",
        json={"ph": 7.2}
    )
    assert response.status_code == 201
    dados = response.json()
    assert dados["ph"] == 7.2

def test_acesso_nao_autorizado(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/usuarios/perfil")
    assert response.status_code == 401