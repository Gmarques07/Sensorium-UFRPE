import sys
import os
from sqlalchemy import text

# Adiciona o diretório raiz ao path para que os módulos possam ser importados
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app.db.session import engine
from backend.app.db.base_class import Base
# Importa os modelos para garantir que eles sejam registrados
from backend.app import models

def init_db():
    """
    Initialize database.
    """
    try:
        with engine.connect() as connection:
            with connection.begin():
                # Desabilitar checagem de chave estrangeira
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                # Cria todas as tabelas definidas nos modelos
                Base.metadata.create_all(bind=connection)
                # Reabilitar checagem de chave estrangeira
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        raise e

if __name__ == "__main__":
    init_db()