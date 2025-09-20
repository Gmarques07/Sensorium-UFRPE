#!/bin/bash

# Script para execução fácil dos testes em ambientes Linux/macOS
# Usa docker-compose.dev.yml para um ambiente totalmente containerizado

COMPOSE_FILE="docker-compose.dev.yml"

# Verificar se o arquivo docker-compose.dev.yml existe
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Erro: O arquivo $COMPOSE_FILE não foi encontrado na raiz do projeto."
    echo "Certifique-se de estar no diretório raiz do projeto e que o arquivo existe."
    exit 1
fi

show_menu() {
    echo ""
    echo "======================================="
    echo "Sistema de Testes - Sensorium UFRPE (Dockerizado)"
    echo "======================================="
    echo ""
    echo "Escolha uma opcao:"
    echo "1) Executar todos os testes"
    echo "2) Executar testes de unidade"
    echo "3) Executar testes de integracao"
    echo "4) Executar testes com cobertura"
    echo "5) Executar testes especificos"
    echo "6) Limpar containers de teste"
    echo "7) Build dos containers de teste"
    echo "0) Sair"
    echo ""
}

run_all_tests() {
    echo "Executando todos os testes..."
    echo ""
    echo "Cobertura - Testes de Unidade:"
    docker-compose -f "$COMPOSE_FILE" run --rm tests pytest --cov=backend/app --cov-report=term-missing --ignore=backend/tests/integration
    echo ""
    echo "Cobertura - Testes de Integracao:"
    docker-compose -f "$COMPOSE_FILE" run --rm tests_integration pytest --cov=backend/app --cov-report=term-missing
}

run_unit_tests() {
    echo "Executando testes de unidade..."
    docker-compose -f "$COMPOSE_FILE" run --rm tests
}

run_integration_tests() {
    echo "Executando testes de integracao..."
    docker-compose -f "$COMPOSE_FILE" run --rm tests_integration
}

run_coverage_tests() {
    echo "Executando testes com cobertura..."
    echo ""
    echo "Cobertura - Testes de Unidade:"
    docker-compose -f "$COMPOSE_FILE" run --rm tests pytest --cov=backend/app --cov-report=term-missing --ignore=backend/tests/integration
    echo ""
    echo "Cobertura - Testes de Integracao:"
    docker-compose -f "$COMPOSE_FILE" run --rm tests_integration pytest --cov=backend/app --cov-report=term-missing
}

run_specific_tests() {
    echo "Executar testes especificos"
    echo "Exemplos:"
    echo "  - backend/tests/test_auth.py"
    echo "  - backend/tests/integration/test_usuarios_integration.py"
    echo "  - backend/tests/ -k login"
    echo ""
    read -p "Comando pytest: " test_cmd
    
    if [[ "$test_cmd" == *integration* ]]; then
        echo "Executando testes de integracao especificos..."
        docker-compose -f "$COMPOSE_FILE" run --rm tests_integration pytest $test_cmd
    else
        echo "Executando testes de unidade especificos..."
        docker-compose -f "$COMPOSE_FILE" run --rm tests pytest $test_cmd
    fi
}

clean_test_containers() {
    echo "Limpando containers de teste..."
    docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
    echo "Containers limpos com sucesso!"
}

build_test_containers() {
    echo "Building containers de teste..."
    docker-compose -f "$COMPOSE_FILE" build tests tests_integration backend_int
    echo "Build concluido!"
}

# Loop principal
while true; do
    show_menu
    read -p "Opcao: " choice
    
    case $choice in
        1) run_all_tests ;;
        2) run_unit_tests ;;
        3) run_integration_tests ;;
        4) run_coverage_tests ;;
        5) run_specific_tests ;;
        6) clean_test_containers ;;
        7) build_test_containers ;;
        0) 
            echo "Ate logo!"
            break
            ;;
        *)
            echo "Opcao invalida!"
            ;;
    esac
    
    # Pausa para o usuário ver o resultado antes de mostrar o menu novamente
    if [ "$choice" -ne 0 ]; then
        echo ""
        read -n 1 -s -r -p "Pressione qualquer tecla para continuar..."
        echo ""
    fi
done
