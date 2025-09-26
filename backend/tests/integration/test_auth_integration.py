"""
Testes de autenticação de integração usando banco de dados isolado e TestClient.
"""
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from backend.app.models.usuario import Usuario


def test_registro_login_perfil_flow(client: TestClient, db: Session):
    """
    Testa o fluxo completo de registro, login e acesso ao perfil com banco de dados isolado.
    """
    # Registro
    response = client.post(
        "/api/v1/auth/registro",
        json={
            "nome": "User Int",
            "email": "int@example.com",
            "endereco": "Rua Int, 123",
            "senha": "senha_int_123"
        }
    )
    assert response.status_code == 200  # Novo registro deve ter status 200
    
    # Verifica se o usuário foi criado no banco de dados isolado
    created_user = db.query(Usuario).filter(Usuario.email == "int@example.com").first()
    assert created_user is not None
    assert created_user.nome == "User Int"

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "int@example.com", "senha": "senha_int_123"}  # Usando json para login (conforme schema Login)
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    token = token_data["access_token"]

    # Acesso ao perfil com token
    response = client.get(
        "/api/v1/usuarios/perfil",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    perfil_data = response.json()
    assert perfil_data["email"] == "int@example.com"
    assert perfil_data["nome"] == "User Int"

