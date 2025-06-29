# PIEC3

Este projeto é referente à disciplina de Projeto Interdisciplinar em Engenharia da Computação 1.  
Equipe composta por: Cauã Venceslau, Gabriel Alves, João Victor Bione, Luís Felipe, Pedro Ivo Novaes, Pedro Marques, Vinícius Rodrigues.

O objetivo desse projeto é organizar o abastecimento de cisternas em zonas rurais.

## Pré-requisitos

- Python 3.8 ou superior
- MySQL 8.0 ou superior
- Wampserver 3.3.5


## Instalação de Dependências

Antes de rodar o projeto, você precisa instalar as dependências listadas no arquivo `requirements.txt`. Para isso, execute o seguinte comando:

```bash
pip install -r requirements.txt


## Dependências

O projeto utiliza as seguintes bibliotecas:

blinker==1.8.2: Usado para enviar sinais e eventos em Flask.
click==8.1.7: Biblioteca para criar interfaces de linha de comando.
colorama==0.4.6: Facilita o uso de cores no terminal.
Flask==3.0.3: O framework web principal que você está usando.
Flask-SQLAlchemy==3.1.1: Extensão Flask para suporte ao SQLAlchemy.
greenlet==3.0.3: Biblioteca que permite a implementação de corrotinas.
itsdangerous==2.2.0: Usado para assinar dados de forma segura em Flask.
Jinja2==3.1.4: Motor de templates usado pelo Flask para renderizar HTML.
MarkupSafe==2.1.5: Biblioteca para garantir que o texto renderizado em HTML seja seguro.
mysql-connector-python==9.0.0: Conector para conectar o Flask ao banco de dados MySQL.
SQLAlchemy==2.0.32: Biblioteca de ORM para trabalhar com bancos de dados relacionais.
typing_extensions==4.12.2: Fornece suporte para novos recursos de tipagem.
Werkzeug==3.0.4: Biblioteca que fornece utilitários WSGI e suporte para Flask.



## Configuração do Banco de Dados

Criar o Banco de Dados:
Acesse o MySQL com um cliente como MySQL Workbench ou pela linha de comando.

Execute o seguinte comando para criar o banco de dados:
CREATE DATABASE banco_de_dados;


## Configurar as Tabelas:

Após criar o banco de dados, você precisa configurar as tabelas necessárias. Utilize o arquivo de esquema SQL fornecido para criar as tabelas no banco de dados. Aqui está um exemplo de comando para criar uma tabela de usuários:

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    cpf VARCHAR(14) UNIQUE,
    email VARCHAR(100) UNIQUE,
    endereco VARCHAR(255),
    senha VARCHAR(255)
);

CREATE TABLE empresas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    senha VARCHAR(255)
);

CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cpf_usuario VARCHAR(14),
    descricao TEXT,
    data DATETIME,
    FOREIGN KEY (cpf_usuario) REFERENCES usuarios(cpf)
);

Alguns usuarios para teste: 

INSERT INTO usuarios (nome, cpf, email, endereco, senha) VALUES
('João Silva', '12345678900', 'joao.silva@example.com', 'Rua das Flores, 123', 'senha123'),
('Maria Oliveira', '23456789012', 'maria.oliveira@example.com', 'Avenida Brasil, 456', 'senha456'),
('Pedro Souza', '34567890123', 'pedro.souza@example.com', 'Praça da Sé, 789', 'senha789');

INSERT INTO empresas (email, nome, cnpj, senha) 
VALUES ('empresa2@example.com', 'Empresa Exemplo 2', '12345678000196', 'senha456');


## Configurar as Conexões:
Verifique se as credenciais de conexão no arquivo app.py estão corretas. O arquivo app.py contém a configuração do banco de dados na variável db_config:

python
Copiar código
db_config = {
  'user': 'root',
  'password': '',
  'host': 'localhost',
  'database': 'banco_de_dados'}


## Rodando o Sistema

Para iniciar o sistema, execute o seguinte comando no bash:
python app.py

O servidor Flask será iniciado e estará disponível em http://localhost:5000.


## Os arquivos HTML do projeto estão localizados na pasta templates. 

Abaixo estão os principais arquivos e suas funções:
- **index.html**: Página inicial do sistema, exibida ao acessar o site pela primeira vez.
- **login_usuario.html**: Formulário de login para usuários, onde eles podem inserir seu CPF e senha.
- **login_empresa.html**: Formulário de login para empresas, com campos para email e senha.
- **cadastro.html**: Página de cadastro para novos usuários, incluindo campos para nome, CPF, email, endereço e senha.
- **cadastro_empresa.html**: Página de cadastro para novas empresas, incluindo campos para nome, CNPJ, email, endereço e senha.
- **editar_usuario.html**: Página para editar o perfil do usuário, onde eles podem atualizar suas informações.
- **editar_empresa.html**: Página para editar o perfil da empresa, permitindo atualizar dados como nome, endereço e telefone.
- **perfil_empresa.html**: Exibe o perfil da empresa, com informações relevantes e opções de edição.
- **dashboard_usuario.html**: Dashboard do usuário, que exibe informações pessoais e opções para solicitar pedidos.
- **solicitar_pedido.html**: Página para solicitar um novo pedido.
- **aceitar_pedidos.html**: Página para aceitar pedidos pendentes.
- **404.html**: Página de erro 404, exibida quando uma página não é encontrada.
- **500.html**: Página de erro 500, exibida quando ocorre um erro interno do servidor.
