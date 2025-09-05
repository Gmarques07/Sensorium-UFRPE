import sys
import os

# Adiciona o diretório raiz ao path para que os módulos possam ser importados
sys.path.insert(0, '/app')

from backend.app.db.session import engine
from backend.app.db.base_class import Base
# Importa os modelos para garantir que eles sejam registrados
from backend.app import models

def init_db():
    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db()