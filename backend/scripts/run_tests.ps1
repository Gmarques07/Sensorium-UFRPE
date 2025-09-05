# Script para execução fácil dos testes no Windows
# Autor: Qwen Code

Write-Host "🧪 Sistema de Testes - Sensorium UFRPE" -ForegroundColor Blue
Write-Host "======================================="

# Verificar se está no diretório correto
if (-not (Test-Path "../config/docker-compose.yml")) {
    Write-Host "❌ Erro: Execute este script a partir do diretório backend/scripts/" -ForegroundColor Red
    Write-Host "   cd backend/scripts/" -ForegroundColor Yellow
    Write-Host "   .\run_tests.ps1" -ForegroundColor Yellow
    exit 1
}

function Show-Menu {
    Write-Host ""
    Write-Host "Escolha uma opção:" -ForegroundColor Yellow
    Write-Host "1) 🧪 Executar todos os testes"
    Write-Host "2) 🔍 Executar testes de unidade"
    Write-Host "3) 🔗 Executar testes de integração"
    Write-Host "4) 📊 Executar testes com cobertura"
    Write-Host "5) 🎯 Executar testes específicos"
    Write-Host "6) 🧹 Limpar containers de teste"
    Write-Host "7) 🚀 Build dos containers de teste"
    Write-Host "0) 🚪 Sair"
    Write-Host ""
}

function Run-All-Tests {
    Write-Host "🚀 Executando todos os testes..." -ForegroundColor Blue
    Write-Host ""
    Write-Host "🧪 Testes de Unidade:" -ForegroundColor Yellow
    docker-compose -f ../config/docker-compose.yml run --rm tests
    Write-Host ""
    Write-Host "🔗 Testes de Integração:" -ForegroundColor Yellow
    docker-compose -f ../config/docker-compose.yml run --rm tests_integration
}

function Run-Unit-Tests {
    Write-Host "🔍 Executando testes de unidade..." -ForegroundColor Blue
    docker-compose -f ../config/docker-compose.yml run --rm tests
}

function Run-Integration-Tests {
    Write-Host "🔗 Executando testes de integração..." -ForegroundColor Blue
    docker-compose -f ../config/docker-compose.yml run --rm tests_integration
}

function Run-Coverage-Tests {
    Write-Host "📊 Executando testes com cobertura..." -ForegroundColor Blue
    Write-Host ""
    Write-Host "🧪 Cobertura - Testes de Unidade:" -ForegroundColor Yellow
    docker-compose -f ../config/docker-compose.yml run --rm tests pytest --cov=app --cov-report=term-missing
    Write-Host ""
    Write-Host "🔗 Cobertura - Testes de Integração:" -ForegroundColor Yellow
    docker-compose -f ../config/docker-compose.yml run --rm tests_integration pytest --cov=app --cov-report=term-missing
}

function Run-Specific-Tests {
    Write-Host "🎯 Executar testes específicos" -ForegroundColor Blue
    Write-Host "Exemplos:"
    Write-Host "  - tests/test_auth.py"
    Write-Host "  - tests/integration/test_usuarios_integration.py"
    Write-Host "  - tests/ -k login"
    Write-Host ""
    
    $test_cmd = Read-Host "Comando pytest"
    
    if ($test_cmd -like "*integration*") {
        Write-Host "🔗 Executando testes de integração específicos..." -ForegroundColor Yellow
        docker-compose -f ../config/docker-compose.yml run --rm tests_integration pytest $test_cmd
    } else {
        Write-Host "🧪 Executando testes de unidade específicos..." -ForegroundColor Yellow
        docker-compose -f ../config/docker-compose.yml run --rm tests pytest $test_cmd
    }
}

function Clean-Test-Containers {
    Write-Host "🧹 Limpando containers de teste..." -ForegroundColor Blue
    docker-compose -f ../config/docker-compose.yml down -v
    Write-Host "✅ Containers limpos com sucesso!" -ForegroundColor Green
}

function Build-Test-Containers {
    Write-Host "🚀 Building containers de teste..." -ForegroundColor Blue
    docker-compose -f ../config/docker-compose.yml build tests tests_integration backend_int
    Write-Host "✅ Build concluído!" -ForegroundColor Green
}

do {
    Show-Menu
    $choice = Read-Host "Opção"
    
    switch ($choice) {
        1 { Run-All-Tests }
        2 { Run-Unit-Tests }
        3 { Run-Integration-Tests }
        4 { Run-Coverage-Tests }
        5 { Run-Specific-Tests }
        6 { Clean-Test-Containers }
        7 { Build-Test-Containers }
        0 { 
            Write-Host "👋 Até logo!" -ForegroundColor Green
            exit 0
        }
        default { 
            Write-Host "❌ Opção inválida!" -ForegroundColor Red
        }
    }
} while ($true)