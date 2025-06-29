# Plano de Refatoração do Sistema

## 1. Objetivos
- Melhorar a tipagem e segurança do código
- Criar uma arquitetura mais modular e sustentável
- Facilitar a manutenção e evolução do sistema
- Melhorar a testabilidade do código
- Implementar melhores práticas de desenvolvimento

## 2. Estrutura Proposta

### 2.1 Organização de Diretórios
```
projeto/
├── app/
│   ├── __init__.py
│   ├── models/           # Classes de modelo
│   ├── repositories/     # Camada de acesso a dados
│   ├── services/         # Lógica de negócios
│   ├── controllers/      # Rotas e controladores
│   ├── schemas/          # Schemas de validação
│   └── utils/            # Utilitários
├── tests/
│   ├── unit/
│   └── integration/
├── config/               # Configurações
└── docs/                # Documentação
```

### 2.2 Camadas da Aplicação
1. **Models**: Representação das entidades
   ```python
   from dataclasses import dataclass
   from datetime import datetime
   from typing import Optional

   @dataclass
   class Pedido:
       id: int
       cpf_usuario: str
       descricao: str
       quantidade: int
       data: datetime
       status: str
       cnpj_empresa: str
   ```

2. **Repositories**: Acesso ao banco de dados
   ```python
   from typing import Optional, List
   from .models import Pedido

   class PedidoRepository:
       def find_by_id(self, id: int) -> Optional[Pedido]
       def save(self, pedido: Pedido) -> Pedido
       def update(self, pedido: Pedido) -> Pedido
       def delete(self, id: int) -> bool
       def find_by_usuario(self, cpf: str) -> List[Pedido]
   ```

3. **Services**: Lógica de negócios
   ```python
   class PedidoService:
       def __init__(self, repository: PedidoRepository):
           self.repository = repository

       def criar_pedido(self, dados_pedido: dict) -> Pedido
       def cancelar_pedido(self, pedido_id: int, cpf_usuario: str) -> bool
       def alterar_status(self, pedido_id: int, novo_status: str) -> Pedido
   ```

4. **Controllers**: Rotas e endpoints
   ```python
   from flask import Blueprint, request, jsonify
   from .services import PedidoService

   pedidos_bp = Blueprint('pedidos', __name__)

   @pedidos_bp.route('/pedidos', methods=['POST'])
   @login_required
   def criar_pedido():
       # Implementação
   ```

## 3. Melhorias de Tipagem

### 3.1 Tipos Personalizados
```python
from typing import TypeVar, Generic, NewType

UserId = NewType('UserId', int)
PedidoId = NewType('PedidoId', int)
CPF = NewType('CPF', str)
CNPJ = NewType('CNPJ', str)

T = TypeVar('T')
class Repository(Generic[T]):
    # Implementação base
```

### 3.2 Validação com Pydantic
```python
from pydantic import BaseModel, Field

class PedidoCreate(BaseModel):
    cpf_usuario: str = Field(..., regex=r'^\d{11}$')
    descricao: str = Field(..., min_length=1, max_length=500)
    quantidade: int = Field(..., gt=0)
    cnpj_empresa: str = Field(..., regex=r'^\d{14}$')
```

## 4. Segurança e Boas Práticas

### 4.1 Injeção de Dependência
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    db = providers.Singleton(Database, config.db_url)
    pedido_repository = providers.Factory(
        PedidoRepository,
        db=db
    )
```

### 4.2 Logging Estruturado
```python
import structlog

logger = structlog.get_logger()

class PedidoService:
    def criar_pedido(self, dados_pedido: dict) -> Pedido:
        logger.info(
            "criando_pedido",
            dados=dados_pedido,
            usuario=dados_pedido["cpf_usuario"]
        )
```

### 4.3 Tratamento de Erros
```python
class AppError(Exception):
    """Erro base da aplicação"""
    pass

class PedidoNaoEncontradoError(AppError):
    """Pedido não encontrado"""
    pass

class AcessoNegadoError(AppError):
    """Usuário não tem permissão"""
    pass
```

## 5. Testes

### 5.1 Testes Unitários
```python
import pytest
from unittest.mock import Mock

def test_criar_pedido():
    repository = Mock(PedidoRepository)
    service = PedidoService(repository)
    
    # Arrange
    dados_pedido = {...}
    
    # Act
    resultado = service.criar_pedido(dados_pedido)
    
    # Assert
    assert resultado.status == "pendente"
    repository.save.assert_called_once()
```

### 5.2 Testes de Integração
```python
def test_fluxo_pedido():
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.post("/pedidos", json={...})
    
    # Assert
    assert response.status_code == 201
    assert "id" in response.json()
```

## 6. Plano de Implementação

### Fase 1: Preparação
1. Criar nova branch: `feature/refatoracao`
2. Configurar ambiente de desenvolvimento
3. Instalar dependências necessárias
4. Criar estrutura de diretórios

### Fase 2: Implementação Base
1. Implementar models e schemas
2. Criar camada de repositório
3. Implementar serviços básicos
4. Configurar injeção de dependência

### Fase 3: Migração
1. Migrar rotas para novos controllers
2. Implementar novos serviços
3. Atualizar chamadas de banco de dados
4. Adicionar validações

### Fase 4: Testes e Documentação
1. Escrever testes unitários
2. Implementar testes de integração
3. Documentar APIs
4. Criar documentação técnica

### Fase 5: Revisão e Deploy
1. Code review
2. Testes de performance
3. Ajustes finais
4. Deploy em staging
5. Testes em produção
6. Deploy final

## 7. Considerações Finais

### Benefícios Esperados
- Código mais seguro e tipado
- Melhor manutenibilidade
- Facilidade para adicionar novas features
- Melhor testabilidade
- Documentação clara

### Riscos e Mitigações
- **Risco**: Tempo de migração
  - *Mitigação*: Implementação gradual
- **Risco**: Bugs durante migração
  - *Mitigação*: Testes extensivos
- **Risco**: Impacto em produção
  - *Mitigação*: Deploy gradual e monitoramento

### Próximos Passos
1. Aprovação do plano
2. Definição de timeline
3. Alocação de recursos
4. Início da implementação 