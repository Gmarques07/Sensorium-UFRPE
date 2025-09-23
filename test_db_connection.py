import mysql.connector
from mysql.connector import errorcode

try:
    # Connect to MySQL
    connection = mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='rootpassword',
        database='banco_de_dados'
    )
    
    if connection.is_connected():
        print("Connected to MySQL database successfully!")
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()
        print(f"Currently connected to database: {database_name[0]}")
        
        # List all tables
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"Tables in the database: {tables}")
        
        cursor.close()
        connection.close()
        print("MySQL connection closed.")
        
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(f"Error: {err}")