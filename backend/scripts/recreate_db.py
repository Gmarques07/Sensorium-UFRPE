#!/usr/bin/env python3
"""
Script para verificar e recriar as tabelas do banco de dados.
"""

from app.db.session import engine
from app.db.base_class import Base
from app import models

def recreate_tables():
    print("Recriando tabelas...")
    try:
        # Remover todas as tabelas existentes
        Base.metadata.drop_all(bind=engine)
        print("Tabelas antigas removidas.")
    except Exception as e:
        print(f"Aviso: Não foi possível remover tabelas antigas: {e}")
    
    # Criar todas as tabelas novamente
    Base.metadata.create_all(bind=engine)
    print("Tabelas recriadas com sucesso!")

if __name__ == "__main__":
    recreate_tables()