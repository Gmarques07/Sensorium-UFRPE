import sys
import os
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório raiz ao path para que os módulos possam ser importados
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app.db.session import engine
from backend.app.db.base_class import Base
# Importa os modelos para garantir que eles sejam registrados
from backend.app import models
from backend.app.core.config import settings
from backend.app.models.admin import Admin
from backend.app.core.security import get_password_hash

def init_db():
    """
    Initialize database.
    """
    try:
        # Criar banco de teste se não existir
        with engine.connect() as connection:
            connection.execute(text("CREATE DATABASE IF NOT EXISTS sensorium_test_db"))
            print("Banco de teste criado/verificado com sucesso!")
        
        with engine.connect() as connection:
            with connection.begin():
                # Desabilitar checagem de chave estrangeira
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                # Cria todas as tabelas definidas nos modelos
                Base.metadata.create_all(bind=connection)
                # Reabilitar checagem de chave estrangeira
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print("Tabelas criadas com sucesso!")

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        admin = db.query(Admin).filter(Admin.email == settings.FIRST_SUPERUSER).first()
        if not admin:
            admin = Admin(
                nome="Admin",
                cpf="00000000000",
                email=settings.FIRST_SUPERUSER,
                senha_hash=get_password_hash("admin"),
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Usuário administrador criado com sucesso!")
        else:
            print("Usuário administrador já existe.")

        from backend.app.models.local import Local
        
        # Check if a default local exists
        local = db.query(Local).first()
        if not local:
            default_local = Local(
                nome="Cisterna Principal",
                tipo="CISTERNA",
                descricao="Cisterna principal para coleta de água da chuva."
            )
            db.add(default_local)
            db.commit()
            print("Local padrão criado com sucesso!")
        else:
            print("Pelo menos um local já existe.")

        from backend.app.models.usuario import Usuario

        # Verifica se o usuário padrão existe
        user = db.query(Usuario).filter(Usuario.email == "teste@hotmail.com").first()
        if not user:
            default_user = Usuario(
                nome="Usuario Teste",
                email="teste@hotmail.com",
                endereco="Endereço Padrão",
                ativo=True,
            )
            default_user.set_senha("teste123")
            db.add(default_user)
            db.commit()
            print("Usuário padrão 'teste@hotmail.com' criado com sucesso!")
        else:
            print("Usuário padrão 'teste@hotmail.com' já existe.")
            
        db.close()

    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        raise e

if __name__ == "__main__":
    init_db()
