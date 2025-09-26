import os
import requests
import pytest


def _base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8001")


def _auth_headers(email: str, senha: str) -> dict:
    base = _base_url()
    # Registro idempotente
    requests.post(
        f"{base}/api/v1/auth/registro",
        json={
            "nome": "Notif Int",
            "email": email,
            "endereco": "Rua N, 100",
            "senha": senha,
        },
        timeout=10,
    )
    r = requests.post(
        f"{base}/api/v1/auth/login",
        json={"email": email, "senha": senha},
        timeout=10,
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_notificacoes_fluxo_basico():
    base = _base_url()
    headers = _auth_headers("notif@example.com", "senha_notif_123")

    # Listar notificações (pode estar vazio)
    r = requests.get(f"{base}/api/v1/notificacoes/", headers=headers, timeout=10)
    assert r.status_code == 200
    lista = r.json()
    assert isinstance(lista, list)

    # Não lidas (subset)
    r = requests.get(f"{base}/api/v1/notificacoes/nao-lidas", headers=headers, timeout=10)
    assert r.status_code == 200

