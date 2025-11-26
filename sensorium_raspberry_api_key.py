import requests
import time
import os
from datetime import datetime
import json

class SensoriumSender:
    def __init__(self, api_base_url=None, token=None, api_key=None, dispositivo_id=None):
        """
        Inicializa o envio de dados para o Sensorium
        Aceita tanto token de usuário quanto chave de API para autenticação

        Args:
            api_base_url: URL base da API (ex: "https://sensoriumtech.online")
            token: Token de autenticação JWT do usuário (ex: "Bearer seu_token_aqui")
            api_key: Chave de API do sensor (obtida ao registrar o sensor)
            dispositivo_id: ID do dispositivo/sensor (opcional se usando chave de API)
        """
        self.api_base_url = api_base_url or os.getenv("SENSORIUM_API_BASE_URL", "http://localhost:8000")
        
        # Autenticação por chave de API (preferencial para sensores)
        self.api_key = api_key or os.getenv("SENSORIUM_API_KEY", "")
        
        # Autenticação por token de usuário (para compatibilidade)
        self.token = token or os.getenv("SENSORIUM_TOKEN", "")
        
        # ID do dispositivo (será sobrescrito se usar chave de API)
        self.dispositivo_id = dispositivo_id or int(os.getenv("SENSORIUM_DISPOSITIVO_ID", "0"))
        
        # Define os cabeçalhos com base no tipo de autenticação fornecida
        self.headers = {"Content-Type": "application/json"}
        
        if self.api_key and self.api_key != "INSIRA_SUA_CHAVE_API_AQUI":
            # Prioriza autenticação por chave de API
            self.headers["X-API-Key"] = self.api_key
            print("Usando autenticação por chave de API")
        elif self.token and self.token != "INSIRA_SEU_TOKEN_AQUI":
            # Usa autenticação por token de usuário
            token_formatted = self.token if self.token.startswith("Bearer ") else f"Bearer {self.token}"
            self.headers["Authorization"] = token_formatted
            print("Usando autenticação por token de usuário")
        else:
            raise ValueError(
                "Nenhuma forma de autenticação fornecida. "
                "Forneça uma chave de API (SENSORIUM_API_KEY) ou token de usuário (SENSORIUM_TOKEN)."
            )

    def enviar_leitura(self, ph, boia, status_boia=None, dispositivo_id=None):
        """
        Envia uma leitura de sensor para o servidor
        
        Args:
            ph: Valor de pH (ex: 7.2)
            boia: Valor da bóia (0 ou 1)
            status_boia: Status da bóia ("ALTO" ou "BAIXO"), se não fornecido, será determinado automaticamente
            dispositivo_id: ID do dispositivo (opcional, será sobrescrito se usar chave de API)
        """
        # Determina o status da bóia automaticamente se não for fornecido
        if status_boia is None:
            status_boia = "ALTO" if boia == 1 else "BAIXO"
        
        # Se estiver usando chave de API, o dispositivo_id será determinado automaticamente
        # pelo servidor com base na chave de API
        payload_dispositivo_id = dispositivo_id or self.dispositivo_id
        
        dados = {
            "ph": ph,
            "boia": boia,
            "status_boia": status_boia,
            "dispositivo_id": payload_dispositivo_id
        }
        
        url = f"{self.api_base_url}/api/v1/leituras/"
        
        try:
            response = requests.post(url, json=dados, headers=self.headers, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Dados enviados com sucesso: pH={ph}, boia={boia} ({status_boia})")
                if 'sensor_id' in response.json():
                    print(f"  Enviado para sensor ID: {response.json()['sensor_id']}")
                return True
            elif response.status_code == 401:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro de autenticação (401): Credenciais inválidas")
                return False
            elif response.status_code == 400:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro de requisição (400): {response.text}")
                return False
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro {response.status_code}: {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro na requisição: {e}")
            return False
    
    def testar_conexao(self):
        """
        Testa a conexão com o servidor
        """
        try:
            # Faz uma requisição simples para testar a conexão
            url = f"{self.api_base_url}/api/v1/leituras/"
            
            # Envia dados mínimos para testar
            dados_teste = {
                "ph": 7.0,
                "boia": 1,
                "status_boia": "ALTO",
                "dispositivo_id": self.dispositivo_id
            }
            
            response = requests.post(url, json=dados_teste, headers=self.headers, timeout=10)
            
            # Se receber 401, é autenticação; se receber 200/201, autenticação funcionou
            if response.status_code in [200, 201]:
                print("Conexão com o servidor Sensorium: OK (Autenticação válida)")
                return True
            elif response.status_code == 401:
                print("Conexão com o servidor Sensorium: Conectado, mas autenticação inválida")
                return False
            else:
                print(f"Conexão com o servidor Sensorium: Erro {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Conexão com o servidor Sensorium: Falhou - {e}")
            return False


def obter_token_login(email, senha, api_base_url="http://localhost:8000"):
    """
    Função para obter o token de acesso fazendo login
    
    Args:
        email: Email do usuário cadastrado
        senha: Senha do usuário
        api_base_url: URL base da API
    
    Returns:
        Token de acesso ou None se falhar
    """
    url = f"{api_base_url}/api/v1/auth/login"
    headers = {"Content-Type": "application/json"}
    dados = {
        "email": email,
        "senha": senha
    }
    
    try:
        response = requests.post(url, json=dados, headers=headers)
        if response.status_code == 200:
            resposta = response.json()
            token = resposta.get("access_token")
            print(f"Login realizado com sucesso! Token: Bearer {token[:10]}...")
            return f"Bearer {token}"
        else:
            print(f"Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        return None


def registrar_novo_sensor(token, api_base_url, nome_sensor, tipo_sensor, descricao=""):
    """
    Registra um novo sensor no sistema e obtém sua chave de API
    
    Args:
        token: Token de usuário para autenticação
        api_base_url: URL base da API
        nome_sensor: Nome do sensor
        tipo_sensor: Tipo do sensor (ex: "CISTERNA", "AQUARIO")
        descricao: Descrição opcional do sensor
    
    Returns:
        Dicionário com informações do sensor registrado, incluindo chave_api
    """
    url = f"{api_base_url}/api/v1/sensores/registrar-sensor"
    headers = {
        "Authorization": token if token.startswith("Bearer ") else f"Bearer {token}",
        "Content-Type": "application/json"
    }
    dados = {
        "nome": nome_sensor,
        "tipo": tipo_sensor,
        "descricao": descricao
    }
    
    try:
        response = requests.post(url, json=dados, headers=headers)
        
        if response.status_code == 201:
            resultado = response.json()
            print(f"Sensor registrado com sucesso!")
            print(f"ID: {resultado['id']}")
            print(f"Nome: {resultado['nome']}")
            print(f"Tipo: {resultado['tipo']}")
            print(f"Chave de API: {resultado['chave_api'][:10]}...")
            print(f"Descrição: {resultado['descricao'] or 'Nenhuma'}")
            return resultado
        else:
            print(f"Erro ao registrar sensor: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao registrar sensor: {e}")
        return None


# Exemplo de uso com sensores reais (substitua com a leitura dos seus sensores)
def exemplo_com_sensores_reais():
    """
    Função de exemplo para leitura de sensores reais
    Substitua esta função com a leitura real dos seus sensores
    """
    # Aqui você substituiria por leitura real dos seus sensores
    # Por exemplo, usando bibliotecas como RPi.GPIO para ler sensores GPIO
    # ou bibliotecas específicas para sensores de pH e nível
    
    # Valores simulados - substitua com leitura real dos sensores
    ph_atual = 7.2  # Valor de pH lido do sensor
    valor_boia = 1  # 0 ou 1 - valor do sensor de nível
    status_boia = "ALTO"  # ou "BAIXO" dependendo do valor da bóia
    
    return ph_atual, valor_boia, status_boia


if __name__ == "__main__":
    print("Configuração do envio de dados para o Sensorium - Com Suporte a Chave de API")
    print("="*80)
    
    try:
        # Inicializa o sender - tente primeiro com chave de API, depois com token de usuário
        sender = None
        
        # Tenta inicializar com chave de API primeiro (recomendado para sensores)
        api_key = os.getenv("SENSORIUM_API_KEY", "")
        if api_key and api_key != "INSIRA_SUA_CHAVE_API_AQUI":
            print("Tentando inicializar com chave de API...")
            sender = SensoriumSender(api_key=api_key)
        else:
            # Se não tiver chave de API, tenta com token de usuário
            token = os.getenv("SENSORIUM_TOKEN", "")
            if token and token != "INSIRA_SEU_TOKEN_AQUI":
                print("Tentando inicializar com token de usuário...")
                dispositivo_id = int(os.getenv("SENSORIUM_DISPOSITIVO_ID", "1"))
                sender = SensoriumSender(token=token, dispositivo_id=dispositivo_id)
            else:
                print("ERRO: Nenhuma forma de autenticação disponível!")
                print("\nPara configurar:")
                print("1. Obtenha uma chave de API registrando um sensor (veja função registrar_novo_sensor)")
                print("2. OU obtenha um token de usuário fazendo login (veja função obter_token_login)")
                print("\nConfiguração via variáveis de ambiente:")
                print("  Para chave de API: export SENSORIUM_API_KEY='sua_chave_de_api'")
                print("  Para token de usuário: export SENSORIUM_TOKEN='seu_token' SENSORIUM_DISPOSITIVO_ID=1")
                exit(1)
        
        print(f"URL da API: {sender.api_base_url}")
        print(f"Headers configurados: {'X-API-Key' if 'X-API-Key' in sender.headers else 'Authorization (Token)'}")
        
        # Testa a conexão
        if sender.testar_conexao():
            print("\nIniciando envio de dados de exemplo...")
            
            # Exemplo de envio de dados de teste
            sucesso = sender.enviar_leitura(ph=7.2, boia=1, status_boia="ALTO")
            if sucesso:
                print("Leitura de teste enviada com sucesso!")
                
                # Se quiser fazer envio contínuo, descomente o código abaixo:
                """
                print("\nIniciando envio contínuo de dados (pressione Ctrl+C para parar)...")
                contador = 0
                while True:
                    try:
                        # Obter dados reais dos sensores
                        ph, boia, status_boia = exemplo_com_sensores_reais()
                        
                        # Enviar dados para o servidor
                        sucesso = sender.enviar_leitura(ph, boia, status_boia)
                        
                        if sucesso:
                            contador += 1
                            print(f"Leitura #{contador} enviada com sucesso")
                        
                        # Espera 30 segundos antes de enviar a próxima leitura
                        time.sleep(30)
                        
                    except KeyboardInterrupt:
                        print("\nEnvio de dados interrompido pelo usuário")
                        break
                """
            else:
                print("Falha ao enviar leitura de teste.")
        else:
            print("Falha na conexão com o servidor")
            
    except ValueError as e:
        print(f"\nErro de configuração: {e}")
    except Exception as e:
        print(f"\nErro inesperado: {e}")