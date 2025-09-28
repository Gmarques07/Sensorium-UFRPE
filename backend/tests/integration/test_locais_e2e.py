import pytest
from fastapi.testclient import TestClient
from typing import Dict, Generator

@pytest.fixture(scope="function")
def test_local(client: TestClient, user_auth_headers: Dict[str, str]) -> Generator[Dict, None, None]:
    """Fixture para criar um local de teste e disponibilizá-lo para outros testes."""
    local_data = {"nome": "Cisterna de Teste", "tipo": "CISTERNA", "descricao": "Local para testes de integração"}
    r = client.post("/api/v1/locais/", headers=user_auth_headers, json=local_data)
    assert r.status_code == 201
    created_local = r.json()
    yield created_local
    # A limpeza é desnecessária, pois o banco de dados é recriado a cada teste.

@pytest.mark.integration
def test_create_local(client: TestClient, user_auth_headers: Dict[str, str]):
    """Testa a criação de um novo local."""
    local_data = {"nome": "Cisterna Principal", "tipo": "CISTERNA", "descricao": "Teste de criação"}
    r = client.post("/api/v1/locais/", headers=user_auth_headers, json=local_data)
    assert r.status_code == 201
    response_data = r.json()
    assert response_data["nome"] == local_data["nome"]
    assert "id" in response_data

@pytest.mark.integration
def test_get_dados_atuais_compatibilidade(client: TestClient, user_auth_headers: Dict[str, str], test_local: Dict):
    """Testa o endpoint de compatibilidade para obter dados atuais."""
    r = client.get("/api/v1/locais/dados-atuais", headers=user_auth_headers)
    assert r.status_code == 200
    response_data = r.json()
    assert isinstance(response_data, dict)
    # Verifica a estrutura da resposta
    assert "ph_atual" in response_data
    assert "nivel_atual" in response_data
    assert "historico_ph" in response_data
    assert "historico_nivel" in response_data

@pytest.mark.integration
def test_registrar_e_obter_historico_ph(client: TestClient, user_auth_headers: Dict[str, str], test_local: Dict):
    """Testa o registro de uma leitura de pH e a subsequente obtenção do histórico."""
    local_id = test_local["id"]
    
    # 1. Registrar uma nova leitura de pH
    ph_data = {"ph": 7.1}
    r_reg = client.post(f"/api/v1/locais/{local_id}/registrar-ph", headers=user_auth_headers, json=ph_data)
    assert r_reg.status_code == 201
    
    # 2. Obter o histórico de pH para verificar se o registro foi salvo
    r_hist = client.get(f"/api/v1/locais/{local_id}/historico-ph", headers=user_auth_headers)
    assert r_hist.status_code == 200
    historico = r_hist.json()
    assert isinstance(historico, list)
    assert len(historico) > 0
    assert historico[0]["ph"] == ph_data["ph"]

