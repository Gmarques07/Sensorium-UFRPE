@echo off
REM Script para execução rápida dos testes
REM Autor: Qwen Code

echo 🧪 Sistema de Testes - Sensorium UFRPE
echo =======================================

REM Verificar se está no diretório correto
if not exist "..\config\docker-compose.yml" (
    echo ❌ Erro: Execute este script a partir do diretório backend/scripts/
    echo    cd backend/scripts/
    echo    run_tests.bat
    exit /b 1
)

echo.
echo Escolha uma opção:
echo 1) 🧪 Executar todos os testes
echo 2) 🔍 Executar testes de unidade
echo 3) 🔗 Executar testes de integração
echo 4) 🧹 Limpar containers de teste
echo 5) 🚀 Build dos containers de teste
echo 0) 🚪 Sair
echo.

set /p choice="Opção: "

if "%choice%"=="1" (
    echo 🚀 Executando todos os testes...
    echo.
    echo 🧪 Testes de Unidade:
    docker-compose -f ..\config\docker-compose.yml run --rm tests
    echo.
    echo 🔗 Testes de Integração:
    docker-compose -f ..\config\docker-compose.yml run --rm tests_integration
) else if "%choice%"=="2" (
    echo 🔍 Executando testes de unidade...
    docker-compose -f ..\config\docker-compose.yml run --rm tests
) else if "%choice%"=="3" (
    echo 🔗 Executando testes de integração...
    docker-compose -f ..\config\docker-compose.yml run --rm tests_integration
) else if "%choice%"=="4" (
    echo 🧹 Limpando containers de teste...
    docker-compose -f ..\config\docker-compose.yml down -v
    echo ✅ Containers limpos com sucesso!
) else if "%choice%"=="5" (
    echo 🚀 Building containers de teste...
    docker-compose -f ..\config\docker-compose.yml build tests tests_integration backend_int
    echo ✅ Build concluído!
) else if "%choice%"=="0" (
    echo 👋 Até logo!
    exit /b 0
) else (
    echo ❌ Opção inválida!
)

pause