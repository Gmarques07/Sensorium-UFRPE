import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Set the database name before importing config
os.environ['MYSQL_DATABASE'] = 'banco_de_dados'

from backend.app.db.session import engine
from sqlalchemy import text

try:
    connection = engine.connect()
    result = connection.execute(text('SELECT id, nome, email, endereco FROM usuarios LIMIT 5'))
    rows = result.fetchall()
    print('Usuários:')
    for row in rows:
        print(f'  ID: {row[0]}, Nome: {row[1]}, Email: {row[2]}, Endereço: {row[3]}')
    connection.close()
except Exception as e:
    print(f'Erro: {e}')