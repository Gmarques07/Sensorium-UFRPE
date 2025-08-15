from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Criando o engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexão antes de usar
    pool_recycle=300,    # Reconectar após 5 minutos
    echo=False           # Set to True para ver as queries SQL
)

# Criando a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Função para obter o DB
def get_db():
    """
    Dependency para injetar a sessão do banco nas rotas.
    Uso:
    ```
    @app.get("/users/")
    def read_users(db: Session = Depends(get_db)):
        ...
    ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para testar a conexão
def test_connection():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return False
