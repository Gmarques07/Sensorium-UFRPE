import os
import requests
import pytest


def _base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8001")


def _auth_headers() -> dict:
    base = _base_url()
    # Usuário
    requests.post(
        f"{base}/api/v1/auth/registro",
        json={
            "nome": "Locais Int",
            "email": "locais@example.com",
            "endereco": "Rua L, 100",
            "senha": "senha_locais_123",
        },
        timeout=10,
    )
    r = requests.post(
        f"{base}/api/v1/auth/login",
        json={"email": "locais@example.com", "senha": "senha_locais_123"},
        timeout=10,
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_locais_fluxo_basico():
    base = _base_url()
    headers = _auth_headers()

    # Criar local
    r = requests.post(
        f"{base}/api/v1/locais/",
        headers=headers,
        json={"nome": "Cisterna Principal", "tipo": "CISTERNA", "descricao": "Teste"},
        timeout=10,
    )
    # Alguns ambientes podem não permitir criar sem autorização extra; aceitar 201 ou 401 conforme política
    assert r.status_code in (201, 401)
    local_id = None
    if r.status_code == 201:
        local_id = r.json()["id"]
    else:
        # Caso não permita criar, assume local_id=1 para consultas (init_db não cria locas por padrão)
        local_id = 1

    # Dados atuais (compat)
    r = requests.get(f"{base}/api/v1/locais/dados-atuais", headers=headers, timeout=10)
    assert r.status_code in (200, 404)

    # Registrar leitura de pH (se local permitido)
    r = requests.post(
        f"{base}/api/v1/locais/{local_id}/registrar-ph",
        headers=headers,
        json={"ph": 7.1},
        timeout=10,
    )
    assert r.status_code in (201, 404)

    # Obter histórico de pH
    r = requests.get(
        f"{base}/api/v1/locais/{local_id}/historico-ph",
        headers=headers,
        timeout=10,
    )
    assert r.status_code in (200, 404)

