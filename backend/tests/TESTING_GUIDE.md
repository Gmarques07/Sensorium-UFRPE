# Guia de Testes do Projeto Sensorium UFRPE

Este guia explica como os testes são estruturados, executados e como garantem a qualidade do código no projeto Sensorium UFRPE.

## 1. Tipos de Testes

O projeto utiliza três tipos principais de testes:

### 1.1. Testes de Unidade (Unit Tests)

*   **Objetivo:** Testar componentes individuais do código (funções, classes, módulos) de forma isolada.
*   **Ambiente:** São executados em um ambiente totalmente isolado, utilizando um banco de dados SQLite em memória. Isso garante que os testes de unidade sejam rápidos, independentes e não afetem o banco de dados real.
*   **Localização:** `backend/tests/` (excluindo a subpasta `integration/`).
*   **Configuração:** Definidos em `backend/tests/conftest.py`.

### 1.2. Testes de Integração (Integration Tests)

*   **Objetivo:** Testar a interação entre diferentes componentes do sistema, incluindo a comunicação com o banco de dados e as APIs.
*   **Ambiente:** São executados contra a aplicação FastAPI rodando em um contêiner Docker, que por sua vez se conecta ao seu banco de dados MySQL local (WAMP).
*   **Localização:** `backend/tests/integration/`.
*   **Configuração:** Definidos em `backend/tests/integration/conftest.py`.

### 1.3. Testes com Cobertura de Código

*   **Objetivo:** Medir a porcentagem do seu código-fonte que é executada pelos seus testes. Ajuda a identificar áreas do código que não estão sendo testadas.
*   **Execução:** A opção 4 do script `run_tests.ps1` executa os testes de unidade e integração, e adicionalmente gera um relatório de cobertura de código. O comando `docker-compose run` para os serviços `tests` e `tests_integration` é estendido com flags `--cov=backend/app --cov-report=term-missing`.
*   **Relatório:** O resultado é exibido diretamente no terminal, mostrando para cada arquivo:
    *   `Stmts` (Declarações): Número total de linhas de código executáveis.
    *   `Miss` (Faltantes): Número de linhas que não foram executadas pelos testes.
    *   `Cover` (Cobertura): Porcentagem de código coberto pelos testes.
    *   `Missing` (Linhas Faltantes): Números das linhas específicas que não foram testadas.
*   **Importância:** Uma alta cobertura de código indica que grande parte do seu código está sendo exercitada pelos testes, reduzindo a chance de bugs em áreas não testadas. No entanto, alta cobertura não garante que o código está correto, apenas que ele foi executado.

## 2. Como Executar os Testes

Todos os testes são executados via `docker-compose`, utilizando o script auxiliar `backend/scripts/run_tests.ps1`.

Para executar os testes, navegue até o diretório raiz do projeto (`Sensorium-UFRPE/`) no PowerShell e execute:

```powershell
backend/scripts/run_tests.ps1
```

Você terá as seguintes opções:

*   **Opção 1: Executar todos os testes:** Roda tanto os testes de unidade quanto os de integração.
*   **Opção 2: Executar testes de unidade:** Roda apenas os testes de unidade.
*   **Opção 3: Executar testes de integração:** Roda apenas os testes de integração.
*   **Opção 4: Executar testes com cobertura:** Roda todos os testes e gera um relatório de cobertura de código.

**Importante:** Para os testes de integração funcionarem, seu servidor WAMP (com o MySQL) deve estar rodando.

## 3. Conexões e Banco de Dados

### 3.1. Testes de Unidade

*   **Conexão:** Conectam-se a um banco de dados SQLite em memória.
*   **Detalhes:**
    *   O arquivo `backend/tests/conftest.py` (linha 16) define `SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"`.
    *   A fixture `db()` (linha 24) garante que, para cada teste de unidade, um novo banco de dados em memória seja criado e as tabelas sejam populadas, e depois descartado. Isso assegura isolamento total entre os testes.

### 3.2. Testes de Integração

*   **Conexão:** Conectam-se ao seu banco de dados MySQL local (WAMP).
*   **Detalhes:**
    *   O serviço `backend_int` no `docker-compose.yml` (linha ~30) é configurado para usar `MYSQL_HOST: host.docker.internal`, que permite ao contêiner se comunicar com o MySQL rodando na sua máquina hospedeira.
    *   As credenciais de conexão (usuário, senha, banco de dados) são definidas nas variáveis de ambiente do serviço `backend_int` no `docker-compose.yml`.

## 4. Limpeza de Dados de Teste (Testes de Integração)

Para evitar que os dados criados pelos testes de integração poluam seu banco de dados local, uma rotina de limpeza automática foi implementada:

*   **Mecanismo:** Uma fixture `auto_cleanup_db()` (definida em `backend/tests/integration/conftest.py`, linha 12) é executada automaticamente após cada teste de integração.
*   **Funcionamento:** Esta fixture identifica e remove os dados de teste (como usuários criados com `@example.com` e seus dados relacionados em outras tabelas) do seu banco de dados. A ordem de exclusão é cuidadosamente gerenciada para respeitar as chaves estrangeiras.
*   **Código para verificar:**
    *   `backend/tests/integration/conftest.py`: Veja a implementação da fixture `auto_cleanup_db`.
    *   `backend/app/models/usuario.py`: Define o modelo `Usuario`.
    *   `backend/app/models/notificacao.py`: Define o modelo `Notificacao`.
    *   `backend/app/models/usuario_sensor.py`: Define o modelo `UsuarioSensor`.

## 5. Estrutura de Pastas Relevantes

*   `backend/tests/`: Contém todos os testes do backend.
    *   `backend/tests/conftest.py`: Fixtures e configurações para testes de unidade.
    *   `backend/tests/integration/`: Testes de integração.
        *   `backend/tests/integration/conftest.py`: Fixtures e configurações específicas para testes de integração (incluindo a limpeza de dados).
*   `docker-compose.yml`: Define os serviços Docker para execução da aplicação e dos testes.
*   `pytest.ini`: Configurações gerais do Pytest, incluindo o registro de marcadores.
*   `backend/scripts/run_tests.ps1`: Script PowerShell para facilitar a execução dos testes.

Este guia deve fornecer uma compreensão clara de como o sistema de testes funciona e onde encontrar as informações relevantes no código.
