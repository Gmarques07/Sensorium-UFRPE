from app.db.database import test_connection

def test_db():
    """Testa a conexão com o banco de dados"""
    if test_connection():
        print("✅ Conexão com o banco de dados estabelecida com sucesso!")
    else:
        print("❌ Erro ao conectar com o banco de dados!")

if __name__ == "__main__":
    test_db()
