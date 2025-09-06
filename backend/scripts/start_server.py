#!/usr/bin/env python3
"""
Script para iniciar o servidor Sensorium UFRPE.
"""

import uvicorn
import argparse
import sys
import os
from pathlib import Path

# Obter o diretório backend (dois níveis acima do diretório scripts)
backend_dir = Path(__file__).resolve().parents[1]
project_root = backend_dir.parent
sys.path.insert(0, str(backend_dir))

def main():
    parser = argparse.ArgumentParser(description="Iniciar servidor Sensorium UFRPE")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host para rodar o servidor (padrão: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8002,
        help="Porta para rodar o servidor (padrão: 8002)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Ativar hot-reload durante o desenvolvimento"
    )
    
    args = parser.parse_args()
    
    print(f"Iniciando servidor Sensorium UFRPE...")
    print(f"Host: {args.host}")
    print(f"Porta: {args.port}")
    print(f"Hot-reload: {'Ativado' if args.reload else 'Desativado'}")
    print(f"Diretório raiz: {project_root}")
    print(f"Diretório backend: {backend_dir}")
    
    # Mudar para o diretório backend antes de iniciar
    os.chdir(backend_dir)
    
    # Verificar se o módulo app.main existe
    try:
        import app.main
        print("Módulo app.main encontrado com sucesso!")
    except ImportError as e:
        print(f"Erro ao importar app.main: {e}")
        print("Conteúdo do diretório backend:")
        if backend_dir.exists():
            for item in os.listdir(backend_dir):
                print(f"  {item}")
        sys.exit(1)
    
    # Verificar se a pasta templates existe
    templates_dir = project_root / "templates"
    if templates_dir.exists():
        print(f"Pasta templates encontrada: {templates_dir}")
    else:
        print(f"ATENÇÃO: Pasta templates não encontrada: {templates_dir}")
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1
    )

if __name__ == "__main__":
    main()
