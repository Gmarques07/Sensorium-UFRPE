import os
import time
import requests
import pytest


@pytest.mark.integration
def test_login_and_profile_flow():
    base_url = os.getenv("API_BASE_URL", "http://localhost:8001")

    # Registro (idempotente): se existir, espera 400
    r = requests.post(
        f"{base_url}/api/v1/auth/registro",
        json={
            "nome": "User Int",
            "email": "int@example.com",
            "endereco": "Rua Int, 123",
            "senha": "senha_int_123"
        },
        timeout=10,
    )
    assert r.status_code in (200, 400)

    # Login
    r = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"email": "int@example.com", "senha": "senha_int_123"},
        timeout=10,
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    # Perfil
    r = requests.get(
        f"{base_url}/api/v1/usuarios/perfil",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "int@example.com"

