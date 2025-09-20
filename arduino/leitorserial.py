import serial
import json
import sys
import os

# Adicionar o diretório raiz do projeto ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configurar PYTHONPATH
os.environ['PYTHONPATH'] = project_root

from backend.app.db.session import engine, get_db
from backend.app.db.base_class import Base
from backend.app import models
from backend.app.models import *  # Isso garante que todos os modelos sejam registrados
from backend.app.crud import local as crud_local
from backend.app.schemas.local import PhNivelCreate, NivelAguaCreate

# Configura a porta e velocidade (ajuste a porta para a sua máquina)
porta = "/dev/cu.usbserial-110"   # No Linux
# porta = "/dev/ttyUSB1" # Caso tenha mais de um dispositivo
# porta = "COM3"         # No Windows
baud_rate = 9600

try:
    arduino = serial.Serial(porta, baud_rate, timeout=1)
    print(f"✅ Conectado à porta {porta} na taxa {baud_rate} baud")
except Exception as e:
    print("Erro ao conectar:", e)
    exit()

# Buscar local_id de arquivo de configuração
local_id_path = os.path.join(os.path.dirname(__file__), 'local_id.txt')
try:
    with open(local_id_path, 'r') as f:
        local_id = int(f.read().strip())
except Exception:
    local_id = 1  # padrão caso não exista o arquivo

# Obter uma sessão de banco de dados
db_gen = get_db()
db = next(db_gen)

while True:
    try:
        linha = arduino.readline().decode("utf-8").strip()
        if linha:
            try:
                dados = json.loads(linha)
                print("📡 Dados recebidos:", dados)
                # Exemplo: acessar campos
                print(f"pH: {dados['ph']}, Voltagem: {dados['voltagem']}, Nível: {dados['status']}")
                
                # Salvar dados no banco de dados
                # Criar leitura de pH
                ph_create = PhNivelCreate(ph=dados['ph'])
                ph_salvo = crud_local.criar_ph_nivel(db, ph_create, local_id=local_id)
                
                # Mapear o status do sensor para valores de boia
                # Sua boia tem apenas duas opções: "ALTO" e "BAIXO"
                if dados['status'] == 'BAIXO':
                    boia_value = 25
                    status_value = 'BAIXO'
                elif dados['status'] == 'ALTO':
                    boia_value = 75
                    status_value = 'ALTO'
                else:
                    # Valor padrão caso receba um status inesperado
                    boia_value = 50
                    status_value = 'NORMAL'
                
                # Criar leitura de nível
                nivel_create = NivelAguaCreate(boia=boia_value, status=status_value)
                nivel_salvo = crud_local.criar_nivel_agua(db, nivel_create, local_id=local_id)
                
                print(f"💾 Dados salvos no banco de dados - pH ID: {ph_salvo.id}, Nível ID: {nivel_salvo.id}")
                
            except json.JSONDecodeError:
                # Caso venha algum texto que não seja JSON (ex: mensagens de alerta)
                print("Mensagem:", linha)
    except KeyboardInterrupt:
        print("\n🔌 Encerrando conexão...")
        break
    except Exception as e:
        print("Erro ao salvar dados:", e)

# Fechar a sessão do banco de dados
db.close()