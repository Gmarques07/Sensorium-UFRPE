#!/usr/bin/env python3
"""
Script de instalação automatizada para o Sensorium UFRPE Backend
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step, message):
    """Imprime uma etapa do processo de instalação"""
    print(f"\n{'='*50}")
    print(f"ETAPA {step}: {message}")
    print(f"{'='*50}")

def run_command(command, description):
    """Executa um comando e trata erros"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Sucesso!")
        if result.stdout.strip():
            print(f"   Saída: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro:")
        print(f"   Comando: {command}")
        if e.stdout.strip():
            print(f"   Saída: {e.stdout.strip()}")
        if e.stderr.strip():
            print(f"   Erro: {e.stderr.strip()}")
        
        # Verifica se é apenas um aviso sobre atualização do pip
        if "To update, run" in e.stderr and "pip" in description:
            print(f"   ⚠️  Aviso sobre atualização do pip - Continuando...")
            return True
        
        return False

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print_step(1, "Verificando versão do Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 ou superior é necessário!")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatível!")
    return True

def create_venv():
    """Cria ambiente virtual"""
    print_step(2, "Criando ambiente virtual")
    
    if os.path.exists("venv"):
        print("⚠️  Ambiente virtual já existe. Pulando criação...")
        return True
    
    return run_command("python -m venv venv", "Criando ambiente virtual")

def install_dependencies():
    """Instala as dependências"""
    print_step(3, "Instalando dependências")
    
    # Ativa o ambiente virtual e instala dependências
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python.exe"
    else:  # Linux/Mac
        python_cmd = "venv/bin/python"
    
    # Atualiza pip
    if not run_command(f"{python_cmd} -m pip install --upgrade pip", "Atualizando pip"):
        return False
    
    # Instala dependências
    if not run_command(f"{python_cmd} -m pip install -r requirements.txt", "Instalando dependências"):
        return False
    
    return True

def create_env_file():
    """Cria o arquivo .env se não existir"""
    print_step(4, "Configurando arquivo .env")
    
    if os.path.exists(".env"):
        print("⚠️  Arquivo .env já existe. Pulando criação...")
        return True
    
    # Cria arquivo .env com configurações padrão
    env_content = """# Configurações do Banco de Dados
MYSQL_USER=root
MYSQL_PASSWORD=osOvMtonkwxcbEphriXeJGPKdOxSfAzl
MYSQL_HOST=ballast.proxy.rlwy.net
MYSQL_PORT=56724
MYSQL_DATABASE=railway

# Configuração JWT
SECRET_KEY=chave_secreta_muito_longa_e_segura_para_jwt_tokens_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# URL base
BASE_URL=http://localhost:8000

# Ambiente
ENVIRONMENT=development
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com configurações padrão!")
        print("   ⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def test_installation():
    """Testa a instalação"""
    print_step(5, "Testando instalação")
    
    # Testa se consegue importar as dependências principais
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        print("✅ Dependências principais importadas com sucesso!")
    except ImportError as e:
        print(f"❌ Erro ao importar dependências: {e}")
        return False
    
    # Testa conexão com banco de dados
    if os.path.exists("test_db_connection.py"):
        python_cmd = "venv\\Scripts\\python.exe" if os.name == 'nt' else "venv/bin/python"
        if run_command(f"{python_cmd} test_db_connection.py", "Testando conexão com banco de dados"):
            print("✅ Conexão com banco de dados funcionando!")
        else:
            print("⚠️  Problema na conexão com banco de dados. Verifique as configurações no .env")
    
    return True

def print_next_steps():
    """Imprime os próximos passos"""
    print_step(6, "Instalação Concluída!")
    
    print("""
🎉 Instalação concluída com sucesso!

📋 Próximos passos:

1. Configure o arquivo .env com suas configurações:
   - Edite o arquivo .env na pasta backend/
   - Configure as credenciais do banco de dados
   - Gere uma chave secreta segura

2. Ative o ambiente virtual:
   # Windows
   venv\\Scripts\\activate
   
   # Linux/Mac
   source venv/bin/activate

3. Inicie o servidor:
   python start_server.py --reload

4. Acesse a aplicação:
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

📚 Para mais informações, consulte o arquivo INSTALACAO.md

🔧 Se encontrar problemas:
   - Verifique se todas as dependências foram instaladas
   - Confirme se o arquivo .env está configurado corretamente
   - Teste a conexão com o banco de dados
""")

def main():
    """Função principal"""
    print("🚀 Instalador do Sensorium UFRPE Backend")
    print("=" * 50)
    
    # Verifica se está no diretório correto
    if not os.path.exists("requirements.txt"):
        print("❌ Execute este script na pasta backend/ do projeto!")
        return False
    
    # Executa as etapas de instalação
    steps = [
        check_python_version,
        create_venv,
        install_dependencies,
        create_env_file,
        test_installation
    ]
    
    for step in steps:
        if not step():
            print("\n❌ Instalação falhou! Verifique os erros acima.")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
