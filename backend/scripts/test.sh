#!/bin/bash
# Script de atalhos para testes
# Autor: Qwen Code

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${BLUE}🧪 Atalhos para Testes - Sensorium UFRPE${NC}"
    echo "========================================"
    echo
    echo "Uso: ./test.sh [comando]"
    echo
    echo "Comandos disponíveis:"
    echo "  all          🚀 Executar todos os testes"
    echo "  unit         🔍 Executar testes de unidade"
    echo "  integration  🔗 Executar testes de integração"
    echo "  coverage     📊 Executar testes com cobertura"
    echo "  clean        🧹 Limpar containers de teste"
    echo "  build        🚀 Build dos containers de teste"
    echo "  help         📖 Mostrar esta ajuda"
    echo
}

run_all_tests() {
    echo -e "${BLUE}🚀 Executando todos os testes...${NC}"
    echo
    echo -e "${YELLOW}🧪 Testes de Unidade:${NC}"
    docker-compose -f ../config/docker-compose.yml run --rm tests
    echo
    echo -e "${YELLOW}🔗 Testes de Integração:${NC}"
    docker-compose -f ../config/docker-compose.yml run --rm tests_integration
}

run_unit_tests() {
    echo -e "${BLUE}🔍 Executando testes de unidade...${NC}"
    docker-compose -f ../config/docker-compose.yml run --rm tests
}

run_integration_tests() {
    echo -e "${BLUE}🔗 Executando testes de integração...${NC}"
    docker-compose -f ../config/docker-compose.yml run --rm tests_integration
}

run_coverage_tests() {
    echo -e "${BLUE}📊 Executando testes com cobertura...${NC}"
    echo
    echo -e "${YELLOW}🧪 Cobertura - Testes de Unidade:${NC}"
    docker-compose -f ../config/docker-compose.yml run --rm tests pytest --cov=app --cov-report=term-missing
    echo
    echo -e "${YELLOW}🔗 Cobertura - Testes de Integração:${NC}"
    docker-compose -f ../config/docker-compose.yml run --rm tests_integration pytest --cov=app --cov-report=term-missing
}

clean_test_containers() {
    echo -e "${BLUE}🧹 Limpando containers de teste...${NC}"
    docker-compose -f ../config/docker-compose.yml down -v
    echo -e "${GREEN}✅ Containers limpos com sucesso!${NC}"
}

build_test_containers() {
    echo -e "${BLUE}🚀 Building containers de teste...${NC}"
    docker-compose -f ../config/docker-compose.yml build tests tests_integration backend_int
    echo -e "${GREEN}✅ Build concluído!${NC}"
}

# Verificar se está no diretório correto
if [ ! -f "../config/docker-compose.yml" ]; then
    echo -e "${RED}❌ Erro: Execute este script a partir do diretório backend/scripts/${NC}"
    echo "   cd backend/scripts/"
    echo "   ./test.sh"
    exit 1
fi

# Processar argumentos
case "$1" in
    all)
        run_all_tests
        ;;
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    coverage)
        run_coverage_tests
        ;;
    clean)
        clean_test_containers
        ;;
    build)
        build_test_containers
        ;;
    help|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconhecido: $1${NC}"
        echo "Use './test.sh help' para ver os comandos disponíveis."
        exit 1
        ;;
esac