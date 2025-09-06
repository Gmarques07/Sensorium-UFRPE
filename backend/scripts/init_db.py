import sys
import os
import time

# Adiciona o diretório raiz ao path para que os módulos possam ser importados
sys.path.insert(0, '/app')

from backend.app.db.session import engine
from backend.app.db.base_class import Base
# Importa os modelos para garantir que eles sejam registrados
from backend.app import models

def init_db(max_retries=10, retry_delay=2):
    """
    Initialize database with retry logic
    """
    for attempt in range(max_retries):
        try:
            # Cria todas as tabelas definidas nos modelos
            Base.metadata.create_all(bind=engine)
            print("Tabelas criadas com sucesso!")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Tentativa {attempt + 1} falhou: {e}")
                print(f"Aguardando {retry_delay} segundos antes de tentar novamente...")
                time.sleep(retry_delay)
            else:
                print(f"Todas as {max_retries} tentativas falharam.")
                raise e

if __name__ == "__main__":
    init_db()