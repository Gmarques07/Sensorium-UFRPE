import requests
import random
import time
import os

def enviar_dados_teste():
    # Configurações básicas
    url = f"{os.getenv('SENSORIUM_API_BASE_URL', 'http://localhost:8000')}/api/v1/leituras/"

    # Token de acesso (substitua pelo seu token real)
    token = os.getenv("SENSORIUM_TOKEN", "INSIRA_SEU_TOKEN_AQUI")

    # ID do dispositivo (substitua pelo ID do seu sensor real)
    dispositivo_id = int(os.getenv("SENSORIUM_DISPOSITIVO_ID", "1"))

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
    print("Testando envio de dados para o endpoint /api/v1/leituras/")
    print("="*60)
    print(f"Token: {'OK' if os.getenv('SENSORIUM_TOKEN', '') != 'INSIRA_SEU_TOKEN_AQUI' else '<<< ATENÇÃO: Insira seu token no .env ou aqui! >>>'}")
    print(f"Dispositivo ID: {int(os.getenv('SENSORIUM_DISPOSITIVO_ID', '1'))}")
    print(f"API Base URL: {os.getenv('SENSORIUM_API_BASE_URL', 'http://localhost:8000')}")
    print()

    if os.getenv('SENSORIUM_TOKEN', '') == 'INSIRA_SEU_TOKEN_AQUI':
        print("ANTES DE EXECUTAR:")
        print("1. Crie um arquivo .env na raiz do projeto (se não existir)")
        print("2. Adicione as seguintes variáveis no .env:")
        print("   SENSORIUM_TOKEN=\"Bearer SEU_TOKEN_AQUI\"")
        print("   SENSORIUM_DISPOSITIVO_ID=1")
        print("   SENSORIUM_API_BASE_URL=http://localhost:8000 (ou a URL da sua API)")
        print("3. Substitua 'SEU_TOKEN_AQUI' pelo seu token real e ajuste o DISPOSITIVO_ID")
        print()
        print("Para obter seu token:")
        print("- Faça login na aplicação web")
        print("- Verifique o armazenamento local do navegador (F12 > Application > Local Storage)")
        print("- Ou use a rota de login da API para obter um token")
        print()
    else:
        confirmacao = input("Deseja enviar um dado de teste? (s/n): ").strip().lower()
        if confirmacao == 's':
            enviar_dados_teste()
        else:
            print("Execução cancelada.")