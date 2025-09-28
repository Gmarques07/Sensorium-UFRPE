import pytest
from fastapi.testclient import TestClient
from typing import Dict, Generator
import uuid

@pytest.fixture(scope="function")
def test_config(client: TestClient, admin_auth_headers: Dict[str, str]) -> Generator[Dict, None, None]:
    """
    Fixture para criar uma configuração de teste e limpá-la após o uso.
    """
    test_key = f"test_key_{uuid.uuid4().hex[:8]}"
    config_data = {
        "chave": test_key,
        "valor": "initial_value",
        "descricao": "A test configuration"
    }
    
    # Criar a configuração
    r = client.post("/api/v1/admin/configuracoes", headers=admin_auth_headers, json=config_data)
    assert r.status_code in [200, 201]
    
    created_config = r.json()
    yield created_config  # Fornece a configuração criada para o teste
    
    # Limpeza: Deleta a configuração após a conclusão do teste
    client.delete(f"/api/v1/admin/configuracoes/{test_key}", headers=admin_auth_headers)


@pytest.mark.integration
def test_list_configurations(client: TestClient, admin_auth_headers: Dict[str, str], test_config: Dict):
    """
    Testa a listagem de configurações de administrador.
    """
    r = client.get("/api/v1/admin/configuracoes", headers=admin_auth_headers)
    assert r.status_code == 200
    
    response_data = r.json()
    assert isinstance(response_data, list)
    
    # Verifica se a configuração de teste está na lista
    assert any(c["chave"] == test_config["chave"] for c in response_data)


@pytest.mark.integration
def test_update_configuration(client: TestClient, admin_auth_headers: Dict[str, str], test_config: Dict):
    """
    Testa a atualização de uma configuração de administrador.
    """
    update_data = {
        "valor": "updated_value",
        "descricao": "Updated description"
    }
    
    r = client.put(
        f"/api/v1/admin/configuracoes/{test_config['chave']}",
        headers=admin_auth_headers,
        json=update_data
    )
    assert r.status_code == 200
    
    updated_config = r.json()
    assert updated_config["valor"] == update_data["valor"]
    assert updated_config["descricao"] == update_data["descricao"]


@pytest.mark.integration
def test_delete_configuration(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Testa a exclusão de uma configuração de administrador.
    """
    # Cria uma configuração específica para ser deletada neste teste
    test_key = f"delete_test_key_{uuid.uuid4().hex[:8]}"
    config_data = {"chave": test_key, "valor": "to_be_deleted", "descricao": "Test delete"}
    
    r_create = client.post("/api/v1/admin/configuracoes", headers=admin_auth_headers, json=config_data)
    assert r_create.status_code in [200, 201]
    
    # Deleta a configuração
    r_delete = client.delete(f"/api/v1/admin/configuracoes/{test_key}", headers=admin_auth_headers)
    assert r_delete.status_code == 204  # No Content
    
    # Verifica se o item foi realmente removido
    r_list = client.get("/api/v1/admin/configuracoes", headers=admin_auth_headers)
    assert r_list.status_code == 200
    assert not any(c["chave"] == test_key for c in r_list.json())