# Plano de Refatoração do Sistema - Sensorium

## 1. Visão Geral da Nova Direção

### 1.1 Transformação do Projeto
- **De**: Sistema de Gerenciamento de Cisternas
- **Para**: **Sensorium** - Plataforma de Monitoramento e Gerenciamento de Sensores IoT

### 1.2 Objetivos da Refatoração
- Melhorar a tipagem e segurança do código
- Criar uma arquitetura mais modular e sustentável
- Facilitar a manutenção e evolução do sistema
- Melhorar a testabilidade do código
- Implementar melhores práticas de desenvolvimento
- **NOVO**: Generalizar o sistema para suportar múltiplos tipos de ativos e sensores
- **NOVO**: Preparar a base para integração com IoT e análise de dados em tempo real

## 2. Estrutura Proposta

### 2.1 Organização de Diretórios
```
sensorium/
├── app/
│   ├── __init__.py
│   ├── models/           # Classes de modelo para ativos, sensores, métricas
│   ├── repositories/     # Camada de acesso a dados
│   ├── services/         # Lógica de negócios e processamento de dados
│   ├── controllers/      # Rotas e controladores
│   ├── schemas/          # Schemas de validação
│   ├── utils/            # Utilitários
│   └── iot/              # NOVO: Módulos específicos para IoT
│       ├── sensor_manager.py
│       ├── data_processor.py
│       └── real_time_handler.py
├── tests/
│   ├── unit/
│   └── integration/
├── config/               # Configurações
├── docs/                # Documentação
└── frontend/            # NOVO: Frontend React separado
    ├── src/
    ├── public/
    └── package.json
```

### 2.2 Camadas da Aplicação

#### 2.2.1 Models - Representação das Entidades
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class TipoAtivo(Enum):
    CISTERNA = "cisterna"
    TANQUE_COMBUSTIVEL = "tanque_combustivel"
    SILO_GRAS = "silo_graos"
    MAQUINA_INDUSTRIAL = "maquina_industrial"
    SENSOR_AMBIENTAL = "sensor_ambiental"
    EQUIPAMENTO_MEDICO = "equipamento_medico"

class TipoMetrica(Enum):
    NIVEL = "nivel"
    TEMPERATURA = "temperatura"
    UMIDADE = "umidade"
    PH = "ph"
    PRESSAO = "pressao"
    CONSUMO_ENERGIA = "consumo_energia"
    HORAS_USO = "horas_uso"

@dataclass
class Ativo:
    id: int
    nome: str
    tipo: TipoAtivo
    descricao: str
    localizacao: str
    proprietario_id: int
    proprietario_tipo: str  # 'usuario' ou 'empresa'
    configuracoes: Dict[str, Any]
    ativo: bool
    data_criacao: datetime
    data_atualizacao: datetime

@dataclass
class Sensor:
    id: int
    ativo_id: int
    nome: str
    tipo: TipoMetrica
    unidade: str
    frequencia_leitura: int  # em segundos
    limites: Dict[str, float]  # min, max, alerta
    ativo: bool
    ultima_leitura: Optional[datetime]

@dataclass
class LeituraSensor:
    id: int
    sensor_id: int
    valor: float
    timestamp: datetime
    qualidade_dado: float  # 0-1, confiabilidade da leitura
    metadados: Dict[str, Any]

@dataclass
class SolicitacaoServico:
    id: int
    ativo_id: int
    solicitante_id: int
    solicitante_tipo: str
    prestador_id: int
    tipo_servico: str
    descricao: str
    prioridade: str
    status: str
    data_solicitacao: datetime
    data_agendada: Optional[datetime]
    data_conclusao: Optional[datetime]
```

#### 2.2.2 Repositories - Acesso ao Banco de Dados
```python
from typing import Optional, List
from .models import Ativo, Sensor, LeituraSensor, SolicitacaoServico

class AtivoRepository:
    def find_by_id(self, id: int) -> Optional[Ativo]
    def find_by_proprietario(self, proprietario_id: int, proprietario_tipo: str) -> List[Ativo]
    def find_by_tipo(self, tipo: TipoAtivo) -> List[Ativo]
    def save(self, ativo: Ativo) -> Ativo
    def update(self, ativo: Ativo) -> Ativo
    def delete(self, id: int) -> bool

class SensorRepository:
    def find_by_ativo(self, ativo_id: int) -> List[Sensor]
    def find_by_tipo(self, tipo: TipoMetrica) -> List[Sensor]
    def save(self, sensor: Sensor) -> Sensor
    def update(self, sensor: Sensor) -> Sensor
    def delete(self, id: int) -> bool

class LeituraSensorRepository:
    def find_by_sensor(self, sensor_id: int, limit: int = 100) -> List[LeituraSensor]
    def find_by_ativo(self, ativo_id: int, limit: int = 100) -> List[LeituraSensor]
    def find_by_periodo(self, sensor_id: int, inicio: datetime, fim: datetime) -> List[LeituraSensor]
    def save(self, leitura: LeituraSensor) -> LeituraSensor
    def get_ultima_leitura(self, sensor_id: int) -> Optional[LeituraSensor]
```

#### 2.2.3 Services - Lógica de Negócios
```python
class AtivoService:
    def __init__(self, repository: AtivoRepository):
        self.repository = repository

    def criar_ativo(self, dados_ativo: dict) -> Ativo
    def atualizar_ativo(self, ativo_id: int, dados_ativo: dict) -> Ativo
    def desativar_ativo(self, ativo_id: int) -> bool
    def buscar_ativos_por_proprietario(self, proprietario_id: int, proprietario_tipo: str) -> List[Ativo]

class SensorService:
    def __init__(self, repository: SensorRepository, leitura_repository: LeituraSensorRepository):
        self.repository = repository
        self.leitura_repository = leitura_repository

    def criar_sensor(self, dados_sensor: dict) -> Sensor
    def processar_leitura(self, sensor_id: int, valor: float, timestamp: datetime) -> LeituraSensor
    def verificar_alertas(self, sensor_id: int, valor: float) -> List[str]
    def gerar_relatorio(self, sensor_id: int, periodo: tuple) -> Dict[str, Any]

class IoTService:
    def __init__(self, sensor_service: SensorService):
        self.sensor_service = sensor_service

    def receber_dados_sensor(self, dados_iot: dict) -> bool
    def processar_stream_tempo_real(self, dados_stream: List[dict]) -> List[LeituraSensor]
    def configurar_webhook(self, sensor_id: int, url: str) -> bool
```

#### 2.2.4 Controllers - Rotas e Endpoints
```python
from flask import Blueprint, request, jsonify
from .services import AtivoService, SensorService, IoTService

# API para Ativos
ativos_bp = Blueprint('ativos', __name__)

@ativos_bp.route('/ativos', methods=['POST'])
@login_required
def criar_ativo():
    # Implementação

@ativos_bp.route('/ativos/<int:ativo_id>/sensores', methods=['GET'])
@login_required
def listar_sensores_ativo(ativo_id):
    # Implementação

# API para Sensores e Dados IoT
iot_bp = Blueprint('iot', __name__)

@iot_bp.route('/sensores/<int:sensor_id>/dados', methods=['POST'])
def receber_dados_sensor(sensor_id):
    # Endpoint para receber dados de sensores IoT

@iot_bp.route('/ativos/<int:ativo_id>/dashboard', methods=['GET'])
@login_required
def dashboard_ativo(ativo_id):
    # Dashboard em tempo real para um ativo específico
```

## 3. Melhorias de Tipagem

### 3.1 Tipos Personalizados para IoT
```python
from typing import TypeVar, Generic, NewType, Union

# IDs específicos
AtivoId = NewType('AtivoId', int)
SensorId = NewType('SensorId', int)
LeituraId = NewType('LeituraId', int)

# Tipos de dados de sensores
ValorSensor = Union[float, int, str]
QualidadeDado = NewType('QualidadeDado', float)  # 0.0 a 1.0

# Configurações de sensores
ConfiguracaoSensor = Dict[str, Union[str, int, float, bool]]
LimitesSensor = Dict[str, float]  # min, max, alerta

# Metadados de leituras
MetadadosLeitura = Dict[str, Union[str, int, float, bool]]
```

### 3.2 Validação com Pydantic para IoT
```python
from pydantic import BaseModel, Field, validator
from typing import Dict, Any

class LeituraSensorCreate(BaseModel):
    sensor_id: int = Field(..., gt=0)
    valor: float = Field(..., description="Valor lido pelo sensor")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    qualidade_dado: float = Field(..., ge=0.0, le=1.0)
    metadados: Dict[str, Any] = Field(default_factory=dict)

class ConfiguracaoSensorCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: TipoMetrica
    unidade: str = Field(..., min_length=1, max_length=20)
    frequencia_leitura: int = Field(..., gt=0, description="Frequência em segundos")
    limites: LimitesSensor = Field(..., description="Limites min, max, alerta")
```

## 4. Segurança e Boas Práticas

### 4.1 Autenticação e Autorização para IoT
```python
from functools import wraps
from flask import current_app

def require_iot_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar se o usuário tem acesso ao ativo/sensor
        # Verificar permissões específicas para IoT
        pass
    return decorated_function

def require_sensor_ownership(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar se o usuário é proprietário do sensor
        pass
    return decorated_function
```

### 4.2 Injeção de Dependência para IoT
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    db = providers.Singleton(Database, config.db_url)
    
    # Repositories
    ativo_repository = providers.Factory(AtivoRepository, db=db)
    sensor_repository = providers.Factory(SensorRepository, db=db)
    leitura_repository = providers.Factory(LeituraSensorRepository, db=db)
    
    # Services
    ativo_service = providers.Factory(AtivoService, repository=ativo_repository)
    sensor_service = providers.Factory(SensorService, 
                                     repository=sensor_repository,
                                     leitura_repository=leitura_repository)
    iot_service = providers.Factory(IoTService, sensor_service=sensor_service)
```

## 5. Funcionalidades IoT Específicas

### 5.1 Gerenciamento de Sensores
- Cadastro e configuração de diferentes tipos de sensores
- Definição de limites e alertas personalizados
- Calibração e validação de sensores
- Histórico de manutenção e calibração

### 5.2 Coleta de Dados em Tempo Real
- Endpoints para receber dados de sensores IoT
- Processamento de streams de dados
- Validação de qualidade dos dados
- Armazenamento eficiente de séries temporais

### 5.3 Dashboard e Visualização
- Gráficos em tempo real para diferentes tipos de métricas
- Alertas e notificações baseadas em limites
- Relatórios históricos e análises
- Comparação entre diferentes ativos/sensores

### 5.4 Integração com Sistemas Externos
- Webhooks para notificações
- APIs para integração com outros sistemas
- Exportação de dados em diferentes formatos
- Integração com plataformas de IoT existentes

## 6. Migração do Sistema Atual

### 6.1 Fase 1: Preparação da Base
1. Criar nova branch: `feature/sensorium-refactor`
2. Implementar novos modelos de dados
3. Criar camada de repositórios
4. Migrar funcionalidades existentes para nova arquitetura

### 6.2 Fase 2: Generalização de Conceitos
1. **Cisternas → Ativos**: Migrar tabela de cisternas para tabela de ativos
2. **Níveis de Água → Métricas**: Generalizar tabelas de níveis para métricas de sensores
3. **Pedidos → Solicitações de Serviço**: Expandir sistema de pedidos para diferentes tipos de serviços
4. **Análise de Imagens → Detecção de Anomalias**: Generalizar análise de rachaduras para diferentes tipos de problemas

### 6.3 Fase 3: Implementação IoT
1. Sistema de gerenciamento de sensores
2. Coleta e processamento de dados em tempo real
3. Dashboard interativo
4. Sistema de alertas e notificações

### 6.4 Fase 4: Frontend Moderno
1. Migração para React + TypeScript
2. Implementação de WebSockets para tempo real
3. Componentes de visualização de dados
4. Interface responsiva e moderna

## 7. Tecnologias e Ferramentas Recomendadas

### 7.1 Backend
- **FastAPI** (alternativa ao Flask para APIs mais robustas)
- **SQLAlchemy** (ORM mais robusto)
- **Celery** (para processamento assíncrono de dados IoT)
- **Redis** (cache e filas de mensagens)
- **InfluxDB** (banco de dados para séries temporais, opcional)

### 7.2 Frontend
- **React** + **TypeScript**
- **Tailwind CSS** para estilização
- **Chart.js** ou **D3.js** para visualizações
- **Socket.io** para comunicação em tempo real
- **React Query** para gerenciamento de estado do servidor

### 7.3 IoT e Tempo Real
- **WebSockets** para comunicação bidirecional
- **MQTT** para protocolo de mensagens IoT
- **Apache Kafka** (para sistemas de alta escala)
- **Grafana** (para dashboards avançados, opcional)

## 8. Considerações de Escalabilidade

### 8.1 Banco de Dados
- Particionamento de tabelas de leituras por data
- Índices otimizados para consultas de séries temporais
- Considerar banco de dados específico para IoT (InfluxDB, TimescaleDB)

### 8.2 Processamento de Dados
- Processamento em lotes para dados históricos
- Processamento em tempo real para alertas críticos
- Cache inteligente para dados frequentemente acessados

### 8.3 Infraestrutura
- Load balancing para múltiplas instâncias
- Containerização com Docker
- Orquestração com Kubernetes (para alta escala)

## 9. Próximos Passos

### 9.1 Imediato (1-2 semanas)
1. Definir esquema final do banco de dados
2. Implementar novos modelos de dados
3. Criar estrutura de repositórios básica

### 9.2 Curto Prazo (1-2 meses)
1. Migrar funcionalidades existentes
2. Implementar sistema básico de sensores
3. Criar APIs RESTful para novos recursos

### 9.3 Médio Prazo (3-6 meses)
1. Sistema completo de IoT
2. Dashboard em tempo real
3. Frontend moderno com React

### 9.4 Longo Prazo (6+ meses)
1. Análise preditiva com IA/ML
2. Integração com plataformas IoT externas
3. Expansão para diferentes verticais de mercado

## 10. Benefícios Esperados

### 10.1 Técnicos
- Código mais modular e sustentável
- Melhor testabilidade e manutenibilidade
- Arquitetura preparada para escalabilidade
- Base sólida para futuras expansões

### 10.2 de Negócio
- Plataforma mais versátil e atrativa
- Potencial de expansão para diferentes mercados
- Diferencial competitivo com funcionalidades IoT
- Base para monetização através de diferentes tipos de clientes

### 10.3 de Aprendizado
- Experiência com tecnologias modernas
- Conhecimento em IoT e sistemas em tempo real
- Práticas de desenvolvimento escalável
- Preparação para projetos mais complexos

---

**Nota**: Este plano mantém a base sólida de refatoração existente, mas expande significativamente o escopo para criar uma plataforma IoT robusta e escalável. A abordagem híbrida permite evoluir gradualmente, validando cada etapa antes de prosseguir para a próxima. 