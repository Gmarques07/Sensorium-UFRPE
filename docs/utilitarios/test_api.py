#!/usr/bin/env python3
"""
Script para testar a API do Sensorium UFRPE.
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def test_api():
    print("=== Testando API Sensorium UFRPE ===\n")
    
    # Testar endpoint de teste
    print("1. Testando endpoint de teste...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/test")
        if response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Resposta: {response.json()}")
        else:
            print(f"   ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    # Testar registro de usuário
    print("\n2. Testando registro de usuário...")
    usuario_data = {
        "nome": "Teste Usuario",
        "cpf": "12345678901",
        "email": "teste@example.com",
        "endereco": "Rua Teste, 123",
        "senha": "senha123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/registro",
            json=usuario_data
        )
        if response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
            token_data = response.json()
            print(f"   ✓ Token gerado: {token_data.get('access_token', 'N/A')}")
        elif response.status_code == 400:
            print(f"   ! Status: {response.status_code} (usuário já existe)")
        else:
            print(f"   ✗ Status: {response.status_code}")
            print(f"   ✗ Detalhes: {response.text}")
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    print("\n=== Testes concluídos ===")

if __name__ == "__main__":
    test_api()