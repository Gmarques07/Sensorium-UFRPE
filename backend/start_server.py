#!/usr/bin/env python3
"""
Script para iniciar o servidor Sensorium UFRPE.
"""

import uvicorn
import argparse
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
        default=8001,
        help="Porta para rodar o servidor (padrão: 8001)"
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
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1
    )

if __name__ == "__main__":
    main()