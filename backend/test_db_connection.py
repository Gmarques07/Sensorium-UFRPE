#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados Railway
"""

import mysql.connector
from mysql.connector import Error

def test_railway_connection():
    print("=== Testando conexão com Railway MySQL ===\n")
    
    # Configurações do banco de dados
    db_config = {
        'user': 'root',
        'password': 'osOvMtonkwxcbEphriXeJGPKdOxSfAzl',
        'host': 'ballast.proxy.rlwy.net',
        'port': 56724,
        'database': 'railway'
    }
    
    try:
        # Tentar conectar ao MySQL
        print("🔗 Tentando conectar ao banco de dados...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("✅ Conexão com MySQL estabelecida com sucesso!")
            print(f"📊 Versão do MySQL Server: {db_info}")
            
            # Verificar banco de dados atual
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            print(f"🗄️  Banco de dados atual: {database[0]}")
            
            # Listar tabelas
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"📋 Tabelas encontradas: {len(tables)}")
            
            if tables:
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("   ⚠️  Nenhuma tabela encontrada!")
            
            # Verificar se as tabelas principais existem
            expected_tables = ['usuarios', 'admin', 'local', 'notificacao']
            missing_tables = []
            
            for table in expected_tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}';")
                if not cursor.fetchone():
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n⚠️  Tabelas ausentes: {missing_tables}")
                print("💡 Execute o script init_db.py para criar as tabelas")
            else:
                print("\n✅ Todas as tabelas principais estão presentes!")
            
            cursor.close()
            connection.close()
            print("✅ Conexão fechada com sucesso!")
            return True
            
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        print("\n🔍 Possíveis soluções:")
        print("1. Verificar se o servidor Railway está ativo")
        print("2. Confirmar se as credenciais estão corretas")
        print("3. Verificar se o banco de dados existe")
        print("4. Verificar se o usuário tem permissões adequadas")
        print("5. Verificar se a porta está correta")
        return False

if __name__ == "__main__":
    test_railway_connection()
