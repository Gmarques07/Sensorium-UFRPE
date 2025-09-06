#!/bin/bash
# Script para execução fácil dos testes

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Sistema de Testes - Sensorium UFRPE${NC}"
echo "======================================="

# Verificar se está no diretório correto
if [ ! -f "../../docker-compose.yml" ]; then
    echo -e "${RED}Erro: Execute este script a partir do diretório backend/scripts/${NC}"
    echo "   cd backend/scripts/"
    echo "   ./run_tests.sh"
    exit 1
fi

while true; do
    echo
    echo -e "${YELLOW}Escolha uma opcao:${NC}"
    echo "1) Executar todos os testes"
    echo "2) Executar testes de unidade"
    echo "3) Executar testes de integracao"
    echo "4) Executar testes com cobertura"
    echo "5) Executar testes especificos"
    echo "6) Limpar containers de teste"
    echo "7) Build dos containers de teste"
    echo "0) Sair"
    echo
    read -p "Opcao: " choice

    case $choice in
        1)
            echo -e "${BLUE}Executando todos os testes...${NC}"
            echo
            echo -e "${YELLOW}Testes de Unidade:${NC}"
            docker-compose run --rm tests
            echo
            echo -e "${YELLOW}Testes de Integracao:${NC}"
            docker-compose run --rm tests_integration
            ;;
        2)
            echo -e "${BLUE}Executando testes de unidade...${NC}"
            docker-compose run --rm tests
            ;;
        3)
            echo -e "${BLUE}Executando testes de integracao...${NC}"
            docker-compose run --rm tests_integration
            ;;
        4)
            echo -e "${BLUE}Executando testes com cobertura...${NC}"
            echo
            echo -e "${YELLOW}Cobertura - Testes de Unidade:${NC}"
            docker-compose run --rm tests pytest --cov=app --cov-report=term-missing
            echo
            echo -e "${YELLOW}Cobertura - Testes de Integracao:${NC}"
            docker-compose run --rm tests_integration pytest --cov=app --cov-report=term-missing
            ;;
        5)
            echo -e "${BLUE}Executar testes especificos${NC}"
            echo "Exemplos:"
            echo "  - tests/test_auth.py"
            echo "  - tests/integration/test_usuarios_integration.py"
            echo "  - tests/ -k login"
            echo
            read -p "Comando pytest: " test_cmd
            if [[ $test_cmd == *"integration"* ]]; then
                echo -e "${YELLOW}Executando testes de integracao especificos...${NC}"
                docker-compose run --rm tests_integration pytest $test_cmd
            else
                echo -e "${YELLOW}Executando testes de unidade especificos...${NC}"
                docker-compose run --rm tests pytest $test_cmd
            fi
            ;;
        6)
            echo -e "${BLUE}Limpando containers de teste...${NC}"
            docker-compose down -v --remove-orphans
            docker rm -f sensorium_mysql sensorium_backend sensorium_backend_int sensorium_tests sensorium_tests_integration 2>/dev/null || true
            docker network prune -f 2>/dev/null || true
            echo -e "${GREEN}Containers limpos com sucesso!${NC}"
            ;;
        7)
            echo -e "${BLUE}Building containers de teste...${NC}"
            docker-compose build tests tests_integration backend_int
            echo -e "${GREEN}Build concluido!${NC}"
            ;;
        0)
            echo -e "${GREEN}Ate logo!${NC}"
            break
            ;;
        *)
            echo -e "${RED}Opcao invalida!${NC}"
            ;;
    esac
done