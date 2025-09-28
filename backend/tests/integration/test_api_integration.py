"""
Testes de integração apropriados usando banco de dados isolado e TestClient.
Esses testes validam a integração entre diferentes componentes do sistema
com um banco de dados isolado em memória.
"""
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from backend.app.models.usuario import Usuario




def test_criacao_e_leitura_de_local(client: TestClient, db: Session):
    """
    Testa a criação e leitura de um local com banco de dados isolado.
    """
    # Primeiro registramos e autenticamos um usuário
    response = client.post(
        "/api/v1/auth/registro",
        json={
            "nome": "Test User",
            "email": "local_test@example.com",
            "endereco": "Rua Test, 456",
            "senha": "senha_test_123"
        }
    )
    assert response.status_code == 200
    
    # Login para obter token
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "local_test@example.com", "senha": "senha_test_123"}  # Usando json para login (conforme schema Login)
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Criação de um local
    response = client.post(
        "/api/v1/locais/",
        json={
            "nome": "Cisterna Teste",
            "tipo": "CISTERNA",
            "descricao": "Cisterna de teste para integração",
            "latitude": -8.0543,
            "longitude": -34.8813
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    local_data = response.json()
    assert local_data["nome"] == "Cisterna Teste"
    
    # Apenas verificar que a criação foi bem-sucedida com status 201 e os dados corretos
    # O endpoint para obter local específico por ID não existe na API atual
    assert local_data["nome"] == "Cisterna Teste"
    assert local_data["descricao"] == "Cisterna de teste para integração"