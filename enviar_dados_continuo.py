import requests
import random
import time
from datetime import datetime
import os

def enviar_dados_cisterna_principal(token, dispositivo_id=1):
    """
    Envia dados aleatórios a cada 15 segundos para o sensor da cisterna principal
    """
    url = f"{os.getenv('SENSORIUM_API_BASE_URL', 'http://localhost:8001')}/api/v1/leituras/"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    print(f"Iniciando envio de dados para o dispositivo {dispositivo_id}")
    print("Taxa: 1 leitura a cada 15 segundos")
    print("Pressione Ctrl+C para interromper")
    print("-" * 50)
    
    contador = 0
    
    try:
        while True:
            # Gerar dados realistas para uma cisterna
            # pH variando entre 6.0 e 8.0 normalmente, com algumas variações para testar alertas
            if random.random() < 0.1:  # 10% de chance de pH fora da faixa normal
                ph = round(random.uniform(5.0, 6.0), 2)  # pH ácido
            elif random.random() < 0.1:  # 10% de chance de pH fora da faixa normal
                ph = round(random.uniform(8.5, 9.5), 2)  # pH alcalino
            else:
                ph = round(random.uniform(6.5, 8.0), 2)  # pH normal
            
            # Nível da cisterna com comportamento realístico
            # A cisterna normalmente está cheia, mas pode esvaziar ocasionalmente
            if random.random() < 0.15:  # 15% de chance de nível baixo
                boia = 0
                status_boia = "BAIXO"
            else:
                boia = 1
                status_boia = "ALTO"
            
            dados = {
                "ph": ph,
                "boia": boia,
                "status_boia": status_boia,
                "dispositivo_id": dispositivo_id
            }
            
            # Enviar dados
            try:
                response = requests.post(url, json=dados, headers=headers)
                
                if response.status_code in [200, 201]:
                    contador += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] #{contador:3d} pH:{dados['ph']:4.2f} | Nível:{dados['status_boia']:4s} | Dispositivo:{dados['dispositivo_id']}")
                    
                    # Mostrar quando condições de alerta são atingidas
                    condicoes_alerta = []
                    if dados['ph'] < 6.5:
                        condicoes_alerta.append(f"pH ácido ({dados['ph']})")
                    elif dados['ph'] > 8.5:
                        condicoes_alerta.append(f"pH alcalino ({dados['ph']})")
                    
                    if dados['boia'] == 0:
                        condicoes_alerta.append("nível baixo")
                    
                    if condicoes_alerta:
                        print(f"                            >>> ALERTA: {', '.join(condicoes_alerta)}")
                        
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro na requisição: {e}")
            
            # Esperar 15 segundos
            time.sleep(15)
    
    except KeyboardInterrupt:
        print("\n" + "="*50)
        print("Envio de dados interrompido")
        print(f"Total de leituras enviadas: {contador}")
        print("Teste concluído.")

# Configurações - ATUALIZE ESTES VALORES COM SEUS DADOS
TOKEN = os.getenv("SENSORIUM_TOKEN", "INSIRA_SEU_TOKEN_AQUI")  # Ex: "Bearer seu_token_aqui"
DISPOSITIVO_ID = int(os.getenv("SENSORIUM_DISPOSITIVO_ID", "1"))  # Atualize com o ID do seu sensor de cisterna

if __name__ == "__main__":
    print("Script para envio contínuo de dados para cisterna principal")
    print("="*60)
    print(f"Token: {'OK' if TOKEN and TOKEN != 'INSIRA_SEU_TOKEN_AQUI' else '<<< ATENÇÃO: Insira seu token >>>'}")
    print(f"Dispositivo ID: {DISPOSITIVO_ID}")
    print()
    
    if TOKEN == "INSIRA_SEU_TOKEN_AQUI":
        print("ANTES DE EXECUTAR:")
        print("1. Substitua 'INSIRA_SEU_TOKEN_AQUI' com seu token real")
        print("2. Atualize DISPOSITIVO_ID com o ID correto do seu sensor")
        print()
        print("Para obter seu token:")
        print("- Faça login na aplicação")
        print("- Verifique o armazenamento local do navegador (F12 > Application > Local Storage)")
        print("- Ou use a rota de login da API para obter um token")
        print()
    else:
        confirmacao = input("Deseja iniciar o envio de dados? (s/n): ").strip().lower()
        if confirmacao == 's':
            enviar_dados_cisterna_principal(TOKEN, DISPOSITIVO_ID)
        else:
            print("Execução cancelada.")