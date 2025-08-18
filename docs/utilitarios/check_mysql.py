#!/usr/bin/env python3
"""
Script para verificar se o MySQL está disponível e mostrar instruções de configuração.
"""

import sys
import mysql.connector
from mysql.connector import Error

def check_mysql_connection():
    print("=== Verificando conexão com MySQL ===\n")
    
    try:
        # Tentar conectar ao MySQL
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password=''
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("[OK] Conexão com MySQL estabelecida com sucesso!")
            print(f"[INFO] Versão do MySQL Server: {db_info}")
            
            # Criar o banco de dados se não existir
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS sensorium_db")
            print("[OK] Banco de dados 'sensorium_db' criado/verificado com sucesso!")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"[ERRO] Erro ao conectar ao MySQL: {e}")
        print("\n=== Instruções para configurar o MySQL ===")
        print("1. Certifique-se de que o MySQL Server está instalado e em execução")
        print("2. Verifique se o serviço do MySQL está ativo")
        print("3. Confirme as credenciais no arquivo .env")
        print("4. Crie o banco de dados 'sensorium_db' manualmente se necessário")
        print("\n=== Comandos úteis ===")
        print("# No MySQL:")
        print("CREATE DATABASE IF NOT EXISTS sensorium_db;")
        print("CREATE USER 'sensorium_user'@'localhost' IDENTIFIED BY 'sensorium_password';")
        print("GRANT ALL PRIVILEGES ON sensorium_db.* TO 'sensorium_user'@'localhost';")
        print("FLUSH PRIVILEGES;")
        return False

def main():
    print("Sensorium UFRPE - Verificação do Banco de Dados\n")
    
    if check_mysql_connection():
        print("\n[SUCESSO] Pronto para inicializar o banco de dados!")
        print("Execute: python init_db.py")
    else:
        print("\n[FALHA] Não foi possível conectar ao MySQL.")
        print("Corrija os problemas acima e tente novamente.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())