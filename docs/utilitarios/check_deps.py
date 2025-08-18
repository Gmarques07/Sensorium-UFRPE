#!/usr/bin/env python3
"""
Script para verificar se todas as dependências estão instaladas corretamente.
"""

import sys
import importlib

def check_dependency(name, version=None):
    try:
        # Tratamento especial para alguns pacotes
        if name == "jose":
            module = importlib.import_module("jose.jwt")
        elif name == "dotenv":
            module = importlib.import_module("dotenv")
        elif name == "python_multipart":
            module = importlib.import_module("multipart")
        elif name == "mysql.connector":
            module = importlib.import_module("mysql.connector")
        else:
            module = importlib.import_module(name)
            
        if version:
            installed_version = getattr(module, '__version__', 'N/A')
            if installed_version == 'N/A':
                # Tentar obter versão de outra forma
                try:
                    installed_version = module.version
                except:
                    pass
            print(f"[OK] {name} ({installed_version})")
        else:
            print(f"[OK] {name}")
        return True
    except ImportError as e:
        print(f"[ERRO] {name} (nao instalado)")
        return False

def main():
    print("=== Verificando dependencias do projeto ===\n")
    
    dependencies = [
        ("fastapi", "0.103.1"),
        ("uvicorn", "0.23.2"),
        ("sqlalchemy", "2.0.20"),
        ("pydantic", "2.3.0"),
        ("pydantic_settings", "2.0.3"),
        ("jose", None),  # python-jose
        ("passlib", "1.7.4"),
        ("python_multipart", "0.0.6"),
        ("mysql.connector", None),  # mysql-connector-python
        ("email_validator", "2.0.0"),
        ("jinja2", "3.1.2"),
        ("aiofiles", "23.2.1"),
        ("dotenv", None),  # python-dotenv
    ]
    
    all_good = True
    for dep, version in dependencies:
        if not check_dependency(dep, version):
            all_good = False
    
    print("\n=== Resultado ===")
    if all_good:
        print("[SUCESSO] Todas as dependencias estao instaladas corretamente!")
    else:
        print("[FALHA] Algumas dependencias estao faltando. Execute:")
        print("  pip install -r requirements.txt")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)