# 🌊 Sistema Sensorium UFRPE

Plataforma web para gerenciamento e visualização de dados de sensores em tempo real, totalmente conteinerizada com Docker.

## ✨ Visão Geral do Ambiente

Este projeto está configurado para rodar em um ambiente Docker unificado, garantindo consistência e simplicidade no desenvolvimento e execução. O ambiente é composto por dois serviços principais orquestrados pelo Docker Compose:

1.  **`app`**: O contêiner da aplicação principal (backend FastAPI e frontend).
2.  **`mysql`**: O contêiner do banco de dados MySQL.

O fluxo de inicialização foi automatizado para garantir a qualidade do código:

1.  Ao iniciar, o contêiner da aplicação primeiro executa a suíte de testes completa (unidade, integração e cobertura).
2.  **Se todos os testes passarem**, o servidor web da aplicação é iniciado.
3.  **Se qualquer teste falhar**, o contêiner da aplicação irá parar, e os logs indicarão o erro, prevenindo que a aplicação suba com problemas.

##  teknolojileri

*   **Backend**: FastAPI, SQLAlchemy, Pydantic, JWT
*   **Frontend**: Jinja2, Bootstrap 5, Chart.js
*   **Banco de Dados**: MySQL
*   **Testes**: Pytest
*   **DevOps**: Docker & Docker Compose

## 🚀 Como Executar o Projeto

### Pré-requisitos

*   Docker
*   Docker Compose

### Passos para Iniciar

1.  **Clone o repositório** (se ainda não o fez):
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd Sensorium-UFRPE
    ```

2.  **Suba os contêineres**:
    Na raiz do projeto, execute o comando:
    ```bash
    docker-compose up --build
    ```
    *   O `--build` é importante na primeira vez ou se houver mudanças no `Dockerfile` ou `requirements.txt`.

3.  **Acesse o sistema**:
    Após os testes passarem e o servidor iniciar, a aplicação estará disponível em:
    *   **Aplicação Web**: [http://localhost:8001](http://localhost:8001)
    *   **Documentação da API (Swagger)**: [http://localhost:8001/docs](http://localhost:8001/docs)

## 🛠️ Comandos Úteis do Docker

*   **Ver logs em tempo real** (para acompanhar os testes e o servidor):
    ```bash
    docker-compose logs -f app
    ```

*   **Parar os serviços**:
    ```bash
    docker-compose down
    ```

*   **Parar e remover os volumes** (para limpar o banco de dados e começar do zero):
    ```bash
    docker-compose down -v
    ```

## 🗃️ Banco de Dados

*   O serviço do MySQL roda em um contêiner separado e armazena seus dados em um volume Docker (`mysql_data`) para persistência.
*   Para se conectar ao banco de dados a partir da sua máquina (usando MySQL Workbench, por exemplo), use as seguintes credenciais:
    *   **Host**: `localhost`
    *   **Porta**: `3306`
    *   **Usuário**: `root`
    *   **Senha**: `rootpassword`

