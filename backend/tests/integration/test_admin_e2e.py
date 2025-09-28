import pytest
from fastapi.testclient import TestClient
from typing import Dict

@pytest.mark.integration
def test_admin_dashboard_endpoint(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Testa o endpoint do dashboard de admin com autenticação.
    Espera-se uma resposta bem-sucedida com dados do dashboard.
    """
    r = client.get("/api/v1/admin/dashboard", headers=admin_auth_headers)
    assert r.status_code == 200
    # Adicione aqui asserções mais específicas sobre o conteúdo do dashboard, se aplicável
    # Exemplo: assert "total_users" in r.json()


@pytest.mark.integration
def test_admin_list_users_endpoint(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Testa o endpoint de listagem de usuários pelo admin com autenticação.
    Espera-se uma resposta bem-sucedida contendo uma lista de usuários.
    """
    r = client.get("/api/v1/admin/usuarios", headers=admin_auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.integration
def test_admin_list_configurations_endpoint(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Testa o endpoint de listagem de configurações pelo admin com autenticação.
    Espera-se uma resposta bem-sucedida contendo as configurações.
    """
    r = client.get("/api/v1/admin/configuracoes", headers=admin_auth_headers)
    assert r.status_code == 200
    # A resposta pode ser uma lista ou um dicionário, dependendo da implementação
    assert isinstance(r.json(), (list, dict))


@pytest.mark.integration
def test_admin_create_configuration_endpoint(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Testa o endpoint de criação de configuração pelo admin com autenticação.
    """
    config_data = {"chave": "teste_chave", "valor": "teste_valor", "descricao": "Configuração de teste"}
    r = client.post("/api/v1/admin/configuracoes", headers=admin_auth_headers, json=config_data)
    
    # O status code de sucesso para criação pode ser 200 ou 201
    assert r.status_code in [200, 201]
    
    response_data = r.json()
    assert response_data["chave"] == config_data["chave"]
    assert response_data["valor"] == config_data["valor"]