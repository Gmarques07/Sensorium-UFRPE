# Alteração de Cisterna para Local - Notas de Implementação

## Mudanças Realizadas

### 1. Estrutura de Código
- ✅ Renomeados arquivos:
  - `cisterna.py` → `local.py` em todos os diretórios relevantes
  - Atualizada estrutura de imports e referências

### 2. Modelos e Schemas
- ✅ Novo modelo `Local` definido com:
  - Tipos de ambiente (CISTERNA, AQUARIO, CASA)
  - Campos básicos (nome, descrição)
  - Relacionamentos com leituras
- ✅ Schemas atualizados para suportar diferentes tipos de local

### 3. API Endpoints
- ✅ Rotas atualizadas:
  - `/api/v1/cisterna` → `/api/v1/locais`
  - Novos endpoints para gerenciamento de locais
  - Documentação Swagger atualizada

### 4. Documentação
- ✅ API.md atualizado com novos endpoints
- ✅ Exemplos de uso atualizados
- ✅ Documentação do Swagger atualizada

## Pendências

### 1. Banco de Dados
- [ ] Criar migração para nova tabela `locais`
- [ ] Adicionar foreign keys nas tabelas existentes
- [ ] Migrar dados existentes
- [ ] Atualizar queries

### 2. Testes
- [ ] Atualizar testes existentes
- [ ] Adicionar testes para novas funcionalidades
- [ ] Testar diferentes tipos de local

### 3. Frontend
- [ ] Atualizar interfaces para suportar diferentes tipos de local
- [ ] Adicionar formulários de criação de local
- [ ] Atualizar visualizações existentes

## Próximos Passos Recomendados

1. Implementar as migrações do banco de dados
2. Atualizar a suite de testes
3. Adaptar o frontend para as mudanças
4. Realizar testes de integração

## Notas Importantes
- A estrutura do código está pronta para suportar diferentes tipos de local
- As mudanças no banco de dados serão feitas em uma fase posterior
- Manter compatibilidade com dados existentes durante a migração
- Documentar cada etapa da migração do banco de dados

## Impacto nas Funcionalidades Existentes
- Endpoints mantêm mesma lógica de negócio
- Apenas nomenclatura e estrutura foram alteradas
- Sem quebra de compatibilidade até migração do banco
