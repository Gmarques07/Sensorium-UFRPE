# Script para execução fácil dos testes no Windows
# Autor: Qwen Code

# Verificar se está no diretório correto
if (-not (Test-Path '../../docker-compose.yml')) {
    Write-Host 'Erro: Execute este script a partir do diretório backend/scripts/' -ForegroundColor Red
    Write-Host '   cd backend/scripts/' -ForegroundColor Yellow
    Write-Host '   .\run_tests.ps1' -ForegroundColor Yellow
    exit 1
}

function Show-Menu {
    Write-Host ''
    Write-Host '=======================================' -ForegroundColor Blue
    Write-Host 'Sistema de Testes - Sensorium UFRPE' -ForegroundColor Blue
    Write-Host '=======================================' -ForegroundColor Blue
    Write-Host ''
    Write-Host 'Escolha uma opcao:' -ForegroundColor Yellow
    Write-Host '1) Executar todos os testes'
    Write-Host '2) Executar testes de unidade'
    Write-Host '3) Executar testes de integracao'
    Write-Host '4) Executar testes com cobertura'
    Write-Host '5) Executar testes especificos'
    Write-Host '6) Limpar containers de teste'
    Write-Host '7) Build dos containers de teste'
    Write-Host '0) Sair'
    Write-Host ''
}

function Run-All-Tests {
    Write-Host 'Executando todos os testes...' -ForegroundColor Blue
    Write-Host ''
    Write-Host 'Testes de Unidade:' -ForegroundColor Yellow
    docker-compose run --rm tests
    Write-Host ''
    Write-Host 'Testes de Integracao:' -ForegroundColor Yellow
    docker-compose run --rm tests_integration
}

function Run-Unit-Tests {
    Write-Host 'Executando testes de unidade...' -ForegroundColor Blue
    docker-compose run --rm tests
}

function Run-Integration-Tests {
    Write-Host 'Executando testes de integracao...' -ForegroundColor Blue
    docker-compose run --rm tests_integration
}

function Run-Coverage-Tests {
    Write-Host 'Executando testes com cobertura...' -ForegroundColor Blue
    Write-Host ''
    Write-Host 'Cobertura - Testes de Unidade:' -ForegroundColor Yellow
    docker-compose run --rm tests pytest --cov=app --cov-report=term-missing
    Write-Host ''
    Write-Host 'Cobertura - Testes de Integracao:' -ForegroundColor Yellow
    docker-compose run --rm tests_integration pytest --cov=app --cov-report=term-missing
}

function Run-Specific-Tests {
    Write-Host 'Executar testes especificos' -ForegroundColor Blue
    Write-Host 'Exemplos:'
    Write-Host '  - tests/test_auth.py'
    Write-Host '  - tests/integration/test_usuarios_integration.py'
    Write-Host '  - tests/ -k login'
    Write-Host ''
    
    $test_cmd = Read-Host 'Comando pytest'
    
    if ($test_cmd -like '*integration*') {
        Write-Host 'Executando testes de integracao especificos...' -ForegroundColor Yellow
        docker-compose run --rm tests_integration pytest $test_cmd
    } else {
        Write-Host 'Executando testes de unidade especificos...' -ForegroundColor Yellow
        docker-compose run --rm tests pytest $test_cmd
    }
}

function Clean-Test-Containers {
    Write-Host 'Limpando containers de teste...' -ForegroundColor Blue
    docker-compose down -v --remove-orphans
    docker rm -f sensorium_mysql sensorium_backend sensorium_backend_int sensorium_tests sensorium_tests_integration 2>$null
    docker network prune -f 2>$null
    Write-Host 'Containers limpos com sucesso!' -ForegroundColor Green
}

function Build-Test-Containers {
    Write-Host 'Building containers de teste...' -ForegroundColor Blue
    docker-compose build tests tests_integration backend_int
    Write-Host 'Build concluido!' -ForegroundColor Green
}

# Loop principal
$continue = $true
while ($continue) {
    Show-Menu
    $choice = Read-Host 'Opcao'
    
    switch ($choice) {
        1 { Run-All-Tests }
        2 { Run-Unit-Tests }
        3 { Run-Integration-Tests }
        4 { Run-Coverage-Tests }
        5 { Run-Specific-Tests }
        6 { Clean-Test-Containers }
        7 { Build-Test-Containers }
        0 { 
            Write-Host 'Ate logo!' -ForegroundColor Green
            $continue = $false
        }
        default { 
            Write-Host 'Opcao invalida!' -ForegroundColor Red
        }
    }
    
    # Pausa para o usuário ver o resultado antes de mostrar o menu novamente
    if ($choice -ne 0) {
        Write-Host ''
        Write-Host 'Pressione qualquer tecla para continuar...' -ForegroundColor Gray
        $host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    }
}