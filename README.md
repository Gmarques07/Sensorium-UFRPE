# Sistema de Gerenciamento de Cisternas

Este é um sistema web para gerenciamento de cisternas, monitoramento de níveis de água e qualidade (pH). O projeto está estruturado em duas partes:

1. Frontend: Interface web desenvolvida em Flask (temporariamente)
2. Backend: API RESTful moderna desenvolvida em FastAPI

O sistema permite que usuários monitorem suas cisternas em tempo real, com uma interface web amigável e uma API robusta para integrações.

## Funcionalidades Principais

### Para Usuários
- Cadastro e login de usuários
- Solicitação de pedidos de água
- Monitoramento do status dos pedidos
- Visualização de níveis de água e pH da cisterna
- Upload e análise de imagens para detecção de rachaduras
- Recebimento de comunicados e notificações

### Para Empresas
- Cadastro e login de empresas
- Gerenciamento de pedidos recebidos
- Monitoramento de cisternas
- Análise de imagens para detecção de rachaduras
- Envio de comunicados aos usuários
- Dashboard com informações relevantes

### Para Administradores
- Painel administrativo completo
- Gerenciamento de usuários e empresas
- Monitoramento de pedidos
- Configurações do sistema
- Sistema de notificações

## Tecnologias Utilizadas

- Python 3.x
Frontend:
- Flask (Framework Web)
- Jinja2 (Templates)
- Bootstrap (UI)

Backend:
- FastAPI (Framework Web moderno e assíncrono)
- Pydantic (Validação de dados)
- SQLAlchemy (ORM)
- JWT (Autenticação)
- MySQL (Banco de Dados)
- OpenCV (Processamento de Imagens)
- HTML/CSS/JavaScript (Frontend)
- Bootstrap (Framework CSS)

## Requisitos

- Python 3.x
- MySQL Server
- Bibliotecas Python (listadas em requirements.txt)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente do banco de dados em `app.py`:
```python
db_config = {
    'user': 'seu_usuario',
    'password': 'sua_senha',
    'host': 'seu_host',
    'port': porta,
    'database': 'nome_do_banco'
}
```

4. Execute as migrações do banco de dados (os scripts estão na pasta database/schemas)

5. Inicie o servidor:
```bash
python app.py
```

## Estrutura do Projeto

```
Projeto/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   ├── img/
│   │   ├── js/
│   │   └── uploads/
│   ├── templates/
│   └── utils/
├── database/
│   ├── migrations/
│   └── schemas/
├── docs/
├── static/
├── templates/
├── tests/
├── app.py
└── requirements.txt
```

## Funcionalidades de Segurança

- Autenticação de usuários e empresas
- Senhas criptografadas
- Controle de acesso baseado em perfis
- Validação de dados de entrada
- Proteção contra uploads maliciosos
- Sessões seguras

## Processamento de Imagens

O sistema utiliza OpenCV para:
- Detecção automática de rachaduras
- Análise de objetos nas imagens
- Processamento e armazenamento seguro de uploads

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença [INSERIR_LICENÇA]. Veja o arquivo `LICENSE` para mais detalhes.

## Suporte

Para suporte, envie um email para [INSERIR_EMAIL] ou abra uma issue no repositório.
