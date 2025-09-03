# 📚 Documentação - Sistema Sensorium UFRPE

Esta pasta contém toda a documentação do projeto organizada de forma estruturada para facilitar a navegação e manutenção.

## 📁 Estrutura da Documentação

```
docs/
├── 📄 README.md                    # Este arquivo - visão geral da documentação
├── 📄 DOCUMENTATION_SUMMARY.md     # Índice completo de toda a documentação
├── 📁 guides/                      # Guias de uso e desenvolvimento
│   ├── QUICK_START.md             # Guia de início rápido
│   ├── DOCKER_GUIDE.md            # Guia completo do Docker
│   └── DEVELOPER_GUIDE.md         # Guia do desenvolvedor
├── 📁 examples/                    # Exemplos e templates
│   └── env.example                # Exemplo de configuração
├── 📁 backend/                     # Documentação específica do backend
├── 📁 arquitetura/                 # Documentação de arquitetura
├── 📁 migracao/                    # Documentação de migração
├── 📁 referencias/                 # Arquivos de referência
└── 📁 utilitarios/                 # Utilitários e scripts
```

## 🎯 Como Usar Esta Documentação

### Para Novos Participantes
1. **Comece com**: [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) - Índice completo
2. **Escolha seu método**: [guides/QUICK_START.md](guides/QUICK_START.md) - Docker ou Local
3. **Siga o guia específico**: [guides/DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) ou [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md)

### Para Desenvolvedores
1. **Leia**: [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md) - Informações técnicas
2. **Configure**: [examples/env.example](examples/env.example) - Configuração
3. **Desenvolva**: [../backend/README.md](../backend/README.md) - Documentação do backend

### Para Usuários de Docker
1. **Siga**: [guides/DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) - Guia completo
2. **Troubleshoot**: Seção de solução de problemas no mesmo guia

## 📋 Documentos Principais

### 🚀 Guias de Uso
- **[QUICK_START.md](guides/QUICK_START.md)** - Escolha entre Docker ou Local
- **[DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md)** - Instruções detalhadas para Docker
- **[DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md)** - Informações técnicas para desenvolvedores

### 📖 Documentação Técnica
- **[Backend README](../backend/README.md)** - Documentação técnica do backend
- **[API Docs](http://localhost:8001/docs)** - Documentação interativa da API

### 🔧 Exemplos e Configuração
- **[env.example](examples/env.example)** - Exemplo de configuração do ambiente

## 🔍 Encontrando Informações Específicas

### Problemas de Instalação
- **Docker**: [guides/DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) → Seção "Solução de Problemas"
- **Local**: [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md) → Seção "Troubleshooting"

### Configuração do Banco de Dados
- **Geral**: [guides/QUICK_START.md](guides/QUICK_START.md) → Seção "Configuração do MySQL"
- **Docker**: [guides/DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) → Seção "Configuração do Banco de Dados"
- **Local**: [../backend/README.md](../backend/README.md) → Seção "Configuração do Banco de Dados MySQL"

### Desenvolvimento
- **Arquitetura**: [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md) → Seção "Arquitetura do Sistema"
- **Padrões**: [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md) → Seção "Padrões de Desenvolvimento"
- **Testes**: [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md) → Seção "Testes"

### Deploy
- **Docker**: [guides/DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) → Seção "Deploy"
- **Local**: [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md) → Seção "Deploy"

## 📝 Manutenção da Documentação

### Quando Atualizar
- **README.md**: Sempre que houver mudanças significativas no projeto
- **guides/QUICK_START.md**: Quando houver mudanças nos processos de instalação
- **guides/DOCKER_GUIDE.md**: Quando houver mudanças na configuração do Docker
- **guides/DEVELOPER_GUIDE.md**: Quando houver mudanças na arquitetura ou padrões
- **../backend/README.md**: Quando houver mudanças no backend
- **examples/env.example**: Quando houver novas variáveis de ambiente

### Padrões de Documentação
- Use emojis para facilitar a navegação
- Mantenha seções consistentes entre documentos
- Inclua exemplos práticos
- Atualize links entre documentos
- Mantenha informações de contato atualizadas

## 🆘 Suporte

### Para Dúvidas sobre Documentação
1. **Verifique o [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)** para encontrar o documento correto
2. **Consulte a seção específica** no documento
3. **Abra uma issue** no repositório se encontrar informações desatualizadas
4. **Entre em contato** com a equipe para suporte específico

### Para Melhorias na Documentação
1. **Identifique** o documento que precisa de melhoria
2. **Abra uma issue** descrevendo a melhoria necessária
3. **Faça um Pull Request** com as melhorias
4. **Aguarde a revisão** e merge

---

**Última atualização**: Setembro 2025  
**Versão da documentação**: 1.0  
**Mantenedor**: Equipe Sensorium UFRPE