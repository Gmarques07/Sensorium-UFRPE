from app.db.session import engine
from app.db.base_class import Base
from app import models

def init_db():
    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db()