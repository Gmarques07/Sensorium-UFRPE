# 🌊 Sistema Sensorium UFRPE

Plataforma web para gerenciamento e visualização de dados de sensores em tempo real, totalmente conteinerizada com Docker.

## 🚀 Primeiros Passos: Rodando o Projeto

Este guia é tudo que você precisa para ter o ambiente completo do Sensorium rodando na sua máquina.

### Pré-requisitos

*   [Docker](https://www.docker.com/products/docker-desktop/)
*   [Docker Compose](https://docs.docker.com/compose/install/) (geralmente já vem com o Docker Desktop)
*   [Git](https://git-scm.com/)

### Executando o Ambiente

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd Sensorium-UFRPE
    ```

2.  **Suba os contêineres com um único comando:**
    Na raiz do projeto, execute:
    ```bash
    docker-compose up --build
    ```
    *   O argumento `--build` é crucial na primeira vez para construir as imagens Docker do zero.

### O que Acontece ao Iniciar?

Ao executar o comando `up`, o Docker Compose irá orquestrar todo o setup para você:
1.  **Banco de Dados**: Inicia um contêiner com o banco de dados MySQL e o popula com as tabelas iniciais.
2.  **Testes de Validação**: O contêiner da aplicação é construído e **primeiro executa a suíte de testes completa**.
3.  **Inicialização do Servidor**:
    *   ✅ **Se todos os testes passarem**, o servidor web (API e Frontend) é iniciado.
    *   ❌ **Se algum teste falhar**, o processo é interrompido. Os logs no seu terminal indicarão o erro, prevenindo que a aplicação suba com problemas.

### Acessando o Sistema

Após a conclusão dos testes e o início do servidor, a aplicação estará disponível em:
*   **Aplicação Web**: [http://localhost:8001](http://localhost:8001)
*   **Documentação da API (Swagger)**: [http://localhost:8001/docs](http://localhost:8001/docs)

## Tecnologias

*   **Backend**: FastAPI, SQLAlchemy, Pydantic, JWT
*   **Frontend**: Jinja2, Bootstrap 5, Chart.js
*   **Banco de Dados**: MySQL
*   **Testes**: Pytest
*   **DevOps**: Docker & Docker Compose

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

