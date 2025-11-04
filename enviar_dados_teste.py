import requests
import random
import time

def enviar_dados_teste():
    # Configurações básicas
    url = "http://localhost:8000/api/v1/leituras/"
    
    # Token de acesso (substitua pelo seu token real)
    token = "INSIRA_SEU_TOKEN_AQUI"
    
    # ID do dispositivo (substitua pelo ID do seu sensor real)
    dispositivo_id = 1
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("Iniciando envio de dados de teste...")
    print("Lembre-se de substituir 'INSIRA_SEU_TOKEN_AQUI' pelo seu token real")
    print("E ajustar 'dispositivo_id' para o ID do seu sensor")
    print()
    
    for i in range(20):  # Envia 20 leituras de teste
        # Gerar dados aleatórios
        ph = round(random.uniform(6.0, 8.5), 2)  # Faixa normal de pH
        boia = random.randint(0, 1)
        status_boia = "ALTO" if boia == 1 else "BAIXO"
        
        dados = {
            "ph": ph,
            "boia": boia,
            "status_boia": status_boia,
            "dispositivo_id": dispositivo_id
        }
        
        try:
            response = requests.post(url, json=dados, headers=headers)
            if response.status_code in [200, 201]:
                print(f"{i+1:2d}. Dados enviados: pH={ph}, boia={boia} ({status_boia}) - Dispositivo {dispositivo_id}")
            else:
                print(f"{i+1:2d}. Erro {response.status_code}: {response.text}")
        except Exception as e:
            print(f"{i+1:2d}. Falha na requisição: {e}")
        
        time.sleep(1)  # Espera 1 segundo entre envios

if __name__ == "__main__":
    enviar_dados_teste()