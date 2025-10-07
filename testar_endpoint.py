import requests
import json

def testar_endpoint():
    url = "http://localhost:8001/api/v1/estados-luz"
    
    # Testar com estado "ligado"
    payload = {"estado": "ligado"}
    headers = {"Content-Type": "application/json"}
    
    print("Enviando requisição para testar o endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro ao fazer requisição: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Testar com estado "desligado"
    payload = {"estado": "desligado"}
    print("Enviando segunda requisição...")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro ao fazer requisição: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Testar o endpoint GET
    print("Testando endpoint GET para buscar estados...")
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro ao fazer requisição GET: {e}")

if __name__ == "__main__":
    testar_endpoint()