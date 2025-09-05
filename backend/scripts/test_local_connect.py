import mysql.connector
import traceback

config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'banco_de_dados'
}

print('Using config:', config)
try:
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor()
    cur.execute('SELECT 1')
    print('SELECT 1 ->', cur.fetchone())
    cur.execute('SHOW TABLES')
    tables = cur.fetchall()
    print('TABLES ->', tables)
    cur.close()
    cnx.close()
except Exception:
    traceback.print_exc()
