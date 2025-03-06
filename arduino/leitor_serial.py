import serial
import pymysql
import json
import time
import re  # Biblioteca para trabalhar com expressões regulares

# Configuração da porta serial do Arduino
try:
    porta_serial = serial.Serial('/dev/cu.usbserial-110', 9600, timeout=2)
    print("Conexão com a porta serial estabelecida com sucesso!")
except serial.SerialException as e:
    print(f"Erro ao abrir porta serial: {e}")
    time.sleep(2)
    exit()

# Conexão com o banco de dados MySQL usando PyMySQL
try:
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="",  # Adicione sua senha aqui, se necessário
        database="banco_de_dados",
        charset="utf8mb4",
        connect_timeout=10
    )
    cursor = db.cursor()
    print("Conexão ao MySQL estabelecida com sucesso!")
except pymysql.MySQLError as e:
    print(f"Erro ao conectar ao MySQL: {e}")
    time.sleep(2)
    exit()

# Variáveis para monitorar mudanças no status da boia e tempo de inserção
ultimo_status_boia = None
ultimo_tempo_ph = time.time()
ph_atual = None  # Armazena o último valor de pH recebido

# Intervalo de tempo para inserir dados de pH (30 segundos)
INTERVALO_INSERCAO_PH = 30  

# Função para processar mensagens de texto contendo "Valor do pH"
def processar_ph_texto(mensagem):
    match = re.search(r'Valor do pH:\s*([\d.]+)', mensagem)
    if match:
        return float(match.group(1))
    return None

# Loop principal
try:
    while True:
        try:
            dados = porta_serial.readline().decode('utf-8').strip()

            if dados:
                print(f"Dados recebidos: {dados}")

            # Verifica se os dados recebidos são um JSON válido
            if dados.startswith("{"):
                try:
                    dados_json = json.loads(dados)

                    ph = dados_json.get('ph')
                    boia = dados_json.get('boia')
                    status = dados_json.get('status')

                    if ph is not None:
                        ph_atual = ph  # Atualiza o último pH recebido

                    if boia is not None and status is not None:
                        print(f"pH: {ph}, Boia: {boia}, Status: {status}")

                        # Insere nível de água apenas quando houver mudança na boia
                        if boia != ultimo_status_boia:
                            try:
                                query_nivel = "INSERT INTO niveis_agua (boia, status) VALUES (%s, %s)"
                                cursor.execute(query_nivel, (boia, status))
                                db.commit()
                                print(f"Dados inseridos na tabela niveis_agua: Boia = {boia}, Status = {status}")
                                ultimo_status_boia = boia
                            except pymysql.MySQLError as e:
                                print(f"Erro ao inserir dados na tabela niveis_agua: {e}")

                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")

            # Caso os dados venham no formato de texto
            elif "Valor do pH:" in dados:
                ph_texto = processar_ph_texto(dados)
                if ph_texto is not None:
                    ph_atual = ph_texto  # Atualiza o último pH recebido

            # Insere pH no banco a cada 30 segundos
            if ph_atual is not None and (time.time() - ultimo_tempo_ph >= INTERVALO_INSERCAO_PH):
                try:
                    query_ph = "INSERT INTO ph_niveis (ph) VALUES (%s)"
                    cursor.execute(query_ph, (ph_atual,))
                    db.commit()
                    ultimo_tempo_ph = time.time()  # Atualiza o tempo da última inserção
                    print(f"Dados de pH inseridos no banco: pH = {ph_atual}")
                except pymysql.MySQLError as e:
                    print(f"Erro ao inserir dados na tabela ph_niveis: {e}")

        except Exception as e:
            print(f"Erro durante a execução: {e}")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")

finally:
    if 'porta_serial' in locals() and porta_serial.is_open:
        porta_serial.close()
        print("Conexão com a porta serial encerrada.")
    
    if 'db' in locals() and db.open:
        db.close()
        print("Conexão com o banco de dados encerrada.")
