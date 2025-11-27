import pytest
from fastapi.testclient import TestClient
from typing import Dict
from backend.app.models.usuario import Usuario

@pytest.mark.integration
def test_get_user_profile(client: TestClient, user_auth_headers: Dict[str, str], test_user: Usuario):
    """Testa a obtenção do perfil do usuário logado."""
    r = client.get("/api/v1/usuarios/perfil", headers=user_auth_headers)
    assert r.status_code == 200
    profile_data = r.json()
    assert profile_data["email"] == test_user.email
    assert profile_data["nome"] == test_user.nome

@pytest.mark.integration
def test_edit_user_profile(client: TestClient, user_auth_headers: Dict[str, str]):
    """Testa a edição do perfil do usuário."""
    update_data = {"nome": "Nome Editado", "endereco": "Endereco Editado"}
    r = client.put("/api/v1/usuarios/editar-perfil", headers=user_auth_headers, json=update_data)
    assert r.status_code == 200
    updated_profile = r.json()
    assert updated_profile["nome"] == update_data["nome"]
    assert updated_profile["endereco"] == update_data["endereco"]

@pytest.mark.integration
def test_validate_correct_password(client: TestClient, user_auth_headers: Dict[str, str]):
    """Testa a validação de uma senha correta."""
    r = client.post("/api/v1/usuarios/validar-senha", headers=user_auth_headers, params={"senha": "testpassword"})
    assert r.status_code == 200
    assert r.json()["valid"] is True

@pytest.mark.integration
def test_validate_incorrect_password(client: TestClient, user_auth_headers: Dict[str, str]):
    """Testa a validação de uma senha incorreta."""
    r = client.post("/api/v1/usuarios/validar-senha", headers=user_auth_headers, params={"senha": "wrongpassword"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Senha incorreta"

@pytest.mark.integration
def test_delete_account(client: TestClient, user_auth_headers: Dict[str, str], test_user: Usuario):
    """Testa a exclusão (soft delete) da conta do usuário."""
    # Este teste deleta o usuário criado pela fixture `test_user`.
    # Como o banco de dados é limpo a cada teste, esta operação é segura.
    r = client.delete("/api/v1/usuarios/excluir-conta", headers=user_auth_headers, params={"senha": "testpassword"})
    assert r.status_code == 204

    # Verifica que o usuário não consegue mais fazer login
    login_data = {"email": test_user.email, "senha": "testpassword"}
    r_login = client.post("/api/v1/auth/login", json=login_data)
    assert r_login.status_code == 400  # Bad Request (Usuário inativo)
