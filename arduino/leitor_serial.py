import serial
import pymysql
import json
import time
import re  # Biblioteca para trabalhar com expressões regulares

# Configuração da porta serial do Arduino
try:
    porta_serial = serial.Serial('COM5', 9600, timeout=2)
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
        charset="utf8mb4",  # Garante compatibilidade com o charset da tabela
        connect_timeout=10  # Timeout para evitar travamentos
    )
    cursor = db.cursor()
    print("Conexão ao MySQL estabelecida com sucesso!")
except pymysql.MySQLError as e:
    print(f"Erro ao conectar ao MySQL: {e}")
    time.sleep(2)
    exit()

# Variáveis para monitorar mudanças no status da boia
ultimo_status_boia = None

# Faixa segura para o pH
FAIXA_PH_MIN = 3.0
FAIXA_PH_MAX = 9.0

# Função para processar mensagens de texto contendo "Valor do pH"
def processar_ph_texto(mensagem):
    # Usa expressão regular para encontrar valores numéricos em "Valor do pH: X.XX"
    match = re.search(r'Valor do pH:\s*([\d.]+)', mensagem)
    if match:
        return float(match.group(1))  # Retorna o valor numérico como float
    return None

# Loop principal
try:
    while True:
        try:
            # Lê a linha da serial enviada pelo Arduino
            dados = porta_serial.readline().decode('utf-8').strip()

            # Exibe os dados recebidos no terminal (para debug)
            if dados:
                print(f"Dados recebidos: {dados}")

            # Verifica se os dados recebidos são um JSON válido
            if dados.startswith("{"):
                try:
                    # Converte os dados JSON em um dicionário Python
                    dados_json = json.loads(dados)

                    # Extraindo os valores do JSON
                    ph = dados_json.get('ph')
                    boia = dados_json.get('boia')
                    status = dados_json.get('status')

                    # Exibe os valores extraídos (para debug)
                    if ph is not None and boia is not None and status is not None:
                        print(f"pH: {ph}, Boia: {boia}, Status: {status}")

                        # Insere os valores de pH na tabela `ph_niveis` apenas se estiver fora da faixa segura
                        if ph < FAIXA_PH_MIN or ph > FAIXA_PH_MAX:
                            try:
                                query_ph = "INSERT INTO ph_niveis (ph) VALUES (%s)"
                                cursor.execute(query_ph, (ph,))
                                db.commit()
                                print(f"ALERTA! pH fora da faixa segura. Dados inseridos na tabela ph_niveis: pH = {ph}")
                            except pymysql.MySQLError as e:
                                print(f"Erro ao inserir dados na tabela ph_niveis: {e}")

                        # Insere os valores de nível de água na tabela `niveis_agua` apenas quando houver mudança na boia
                        if boia != ultimo_status_boia:
                            try:
                                query_nivel = "INSERT INTO niveis_agua (boia, status) VALUES (%s, %s)"
                                cursor.execute(query_nivel, (boia, status))
                                db.commit()
                                print(f"Dados inseridos na tabela niveis_agua: Boia = {boia}, Status = {status}")
                                ultimo_status_boia = boia  # Atualiza o último estado da boia
                            except pymysql.MySQLError as e:
                                print(f"Erro ao inserir dados na tabela niveis_agua: {e}")

                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")

            # Verifica se a mensagem contém "Valor do pH"
            elif "Valor do pH:" in dados:
                ph_texto = processar_ph_texto(dados)
                if ph_texto is not None and (ph_texto < FAIXA_PH_MIN or ph_texto > FAIXA_PH_MAX):
                    try:
                        query_ph = "INSERT INTO ph_niveis (ph) VALUES (%s)"
                        cursor.execute(query_ph, (ph_texto,))
                        db.commit()
                        print(f"ALERTA! pH fora da faixa segura. Dados inseridos na tabela ph_niveis (mensagem de texto): pH = {ph_texto}")
                    except pymysql.MySQLError as e:
                        print(f"Erro ao inserir dados na tabela ph_niveis (mensagem de texto): {e}")

        except Exception as e:
            print(f"Erro durante a execução: {e}")
            time.sleep(1)  # Aguarda antes de tentar novamente

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")

finally:
    # Fecha conexões antes de sair
    if 'porta_serial' in locals() and porta_serial.is_open:
        porta_serial.close()
        print("Conexão com a porta serial encerrada.")
    
    if 'db' in locals() and db.open:
        db.close()
        print("Conexão com o banco de dados encerrada.")
