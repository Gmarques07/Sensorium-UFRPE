# Guia de Tarefas - Migração Flask para FastAPI

## 1. Preparação Inicial ✅
- [x] Criar nova estrutura de diretórios
- [x] Configurar ambiente FastAPI básico
- [x] Criar arquivo requirements.txt
- [x] Configurar conexão com banco de dados

## 2. Migração dos Modelos✅
- [x] Migrar modelo Usuario
  - [x] Criar schema Pydantic
  - [x] Atualizar modelo SQLAlchemy
  - [x] Implementar métodos CRUD

- [x] Migrar modelos de Cisterna
  - [x] Criar schemas para PhNivel
  - [x] Criar schemas para NivelAgua
  - [x] Implementar métodos CRUD

- [x] Migrar modelos de Notificações
  - [x] Criar schemas
  - [x] Atualizar modelo SQLAlchemy
  - [x] Implementar métodos CRUD

## 3. Migração das Rotas✅

### 3.1 Autenticação (/api/v1/auth) ✅
- [x] Implementar login
  - [x] Adicionar JWT
  - [x] Implementar OAuth2
- [x] Implementar registro
- [x] Implementar logout (stateless - JWT)
- [x] Implementar recuperação de senha

### 3.2 Usuários (/api/v1/usuarios) ✅
- [x] GET /perfil
- [x] PUT /editar-perfil
- [x] DELETE /excluir-conta
- [x] POST /validar-senha (adicional)

### 3.3 Cisterna (/api/v1/cisterna)✅
- [x] GET /dados-atuais
- [x] GET /historico
- [x] GET /nivel-agua
- [x] POST /registrar-leitura

### 3.4 Admin (/api/v1/admin) ✅
- [x] Implementar autenticação admin (via get_current_admin dependency)
- [x] GET /dashboard (com estatísticas completas)
- [x] GET /usuarios (lista e gerenciamento)
- [x] GET /notificacoes (implementado anteriormente)
- [x] GET /configuracoes (CRUD completo)

### 3.5 Notificações (/api/v1/notificacoes) ✅
- [x] GET /listar
- [x] POST /marcar-como-lida
- [x] GET /nao-lidas
- [x] GET /admin (listar notificações admin)
- [x] POST /admin/criar (criar notificação admin)
- [x] POST /admin/{id}/marcar-como-lida

## 4. Testes ✅
- [x] Configurar ambiente de testes
- [x] Testes unitários
  - [x] Modelos
  - [x] Rotas
  - [x] Autenticação
- [x] Testes de integração

## 5. Documentação
- [ ] Documentar todas as rotas no Swagger
- [ ] Criar exemplos de uso
- [ ] Documentar processo de instalação
- [ ] Documentar configurações necessárias

## 6. Deploy
- [ ] Configurar variáveis de ambiente
- [ ] Preparar docker-compose
- [ ] Configurar CI/CD
- [ ] Fazer backup do banco de dados

## O que acontece com o app.py?

O arquivo `app.py` atual será gradualmente descontinuado. O processo será:

1. **Manter dois sistemas temporariamente**
   - Manter `app.py` funcionando durante a migração
   - Criar novos endpoints no FastAPI paralelamente
   - Testar cada funcionalidade migrada

2. **Processo de migração**
   ```
   /app.py (Flask)              →    /app/** (FastAPI)
   /login_usuario              →    /api/v1/auth/login
   /cadastro                   →    /api/v1/auth/signup
   /dashboard_usuario/<cpf>    →    /api/v1/usuarios/dashboard
   /informacoes_cisterna       →    /api/v1/cisterna/dados
   ```

3. **Após a migração completa**
   - Mover `app.py` para `app.py.old`
   - Atualizar documentação
   - Remover dependências do Flask
   - Atualizar scripts de deploy

## Ordem Sugerida de Migração

1. **Primeira Fase**
   - Autenticação básica
   - Rotas de usuário essenciais
   - Endpoints da cisterna

2. **Segunda Fase**
   - Sistema de notificações
   - Dashboard do usuário
   - Funcionalidades administrativas

3. **Terceira Fase**
   - Funcionalidades avançadas
   - Otimizações
   - Testes e documentação

## Validação de Cada Etapa

Para cada funcionalidade migrada:
1. Implementar no FastAPI
2. Testar em paralelo com Flask
3. Documentar mudanças
4. Atualizar clientes da API
5. Remover código antigo

## Dicas de Migração

1. **Modelos**
   - Use Pydantic para validação
   - Mantenha compatibilidade com banco atual
   - Adicione novos campos gradualmente

2. **Rotas**
   - Migre uma rota por vez
   - Mantenha URLs consistentes
   - Documente todas as mudanças

3. **Autenticação**
   - Implemente JWT desde o início
   - Mantenha tokens compatíveis
   - Planeje transição de sessões

4. **Testes**
   - Teste cada endpoint migrado
   - Compare respostas com Flask
   - Valide formatos de dados
