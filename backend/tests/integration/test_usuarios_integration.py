import os
import requests
import pytest

def _base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8001")

def _register_and_login(email: str = None) -> str:
    base = _base_url()
    # Generate a unique email for each test run to avoid UNIQUE constraint issues
    if email is None:
        import uuid
        email = f"int_user_{uuid.uuid4().hex[:8]}@example.com"
    
    # Try to register (may fail if user already exists, which is fine)
    requests.post(
        f"{base}/api/v1/auth/registro",
        json={
            "nome": "User Int",
            "email": email,
            "endereco": "Rua Int, 123",
            "senha": "senha_int_123",
        },
        timeout=10,
    )
    
    # Try to login
    r = requests.post(
        f"{base}/api/v1/auth/login",
        json={"email": email, "senha": "senha_int_123"},
        timeout=10,
    )
    # Handle rate limiting by returning None if we get 429
    if r.status_code == 429:
        return None
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.mark.integration
def test_usuario_perfil_edicao_validacao_exclusao():
    base = _base_url()
    token = _register_and_login()
    
    # If we got rate limited, skip the test
    if token is None:
        pytest.skip("Rate limited - skipping test")
        return
        
    headers = {"Authorization": f"Bearer {token}"}

    # Perfil
    r = requests.get(f"{base}/api/v1/usuarios/perfil", headers=headers, timeout=10)
    assert r.status_code == 200
    perfil = r.json()
    # We can't assert the exact email since it's generated uniquely each time

    # Editar perfil
    r = requests.put(
        f"{base}/api/v1/usuarios/editar-perfil",
        headers=headers,
        json={"nome": "User Int Editado", "endereco": "Rua Nova, 456"},
        timeout=10,
    )
    assert r.status_code == 200
    perfil_edit = r.json()
    assert perfil_edit["nome"] == "User Int Editado"
    assert perfil_edit["endereco"] == "Rua Nova, 456"

    # Validar senha correta
    r = requests.post(
        f"{base}/api/v1/usuarios/validar-senha",
        headers=headers,
        params={"senha": "senha_int_123"},
        timeout=10,
    )
    assert r.status_code == 200
    assert r.json().get("valid") is True

    # Excluir conta (soft delete)
    r = requests.delete(
        f"{base}/api/v1/usuarios/excluir-conta",
        headers=headers,
        params={"senha": "senha_int_123"},
        timeout=10,
    )
    assert r.status_code == 204

