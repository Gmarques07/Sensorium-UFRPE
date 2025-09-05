#!/usr/bin/env python3
"""
Script para inicializar o banco de dados e criar um usuário admin padrão.
"""

import os
import sys
from sqlalchemy.orm import Session

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine, get_db
from app.db.base_class import Base
from app import models
from app.core.security import get_password_hash
from app.models import *  # Isso garante que todos os modelos sejam registrados

def init_db():
    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
    return next(get_db())

def create_admin_user(db: Session):
    # Verificar se já existe um admin
    existing_admin = db.query(models.Admin).first()
    if existing_admin:
        print("Já existe um usuário admin cadastrado.")
        return existing_admin
    
    # Criar um usuário admin padrão
    admin = models.Admin(
        cpf="12345678901",
        nome="admin",
        email="admin@hotmail.com",
        senha_hash=get_password_hash("admin")  # Senha padrão: admin
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("Usuário admin criado com sucesso!")
    print(f"Email: {admin.email}")
    print(f"Senha: admin123 (por favor, altere após o primeiro login)")
    
    return admin

if __name__ == "__main__":
    print("Inicializando banco de dados...")
    db = init_db()
    
    print("Criando usuário admin padrão...")
    create_admin_user(db)
    
    print("Inicialização concluída!")