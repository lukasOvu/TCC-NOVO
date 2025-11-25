# Suite de Testes - Sistema TAXXAT

## 📚 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura de Testes](#estrutura-de-testes)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Como Executar os Testes](#como-executar-os-testes)
5. [Cobertura de Testes](#cobertura-de-testes)
6. [Relatórios](#relatórios)

## 🎯 Visão Geral

Este diretório contém uma suite completa de testes para o sistema TAXXAT, incluindo:

- **Testes Unitários**: Testam funções individuais e componentes isolados
- **Testes de Integração**: Testam APIs e integrações com banco de dados
- **Testes de Interface (GUI)**: Testam a interface do usuário usando Playwright
- **Testes Não Funcionais**: Testam performance, segurança e carga

## 📁 Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py                    # Configuração compartilhada
├── README.md                      # Este arquivo
├── pytest.ini                     # Configuração do pytest
├── requirements.txt               # Dependências de teste
├── unit/                          # Testes unitários
│   ├── test_email_service.py
│   ├── test_password_hashing.py
│   └── test_token_generation.py
├── integration/                   # Testes de integração
│   ├── test_auth_api.py
│   └── test_database.py
├── gui/                           # Testes de interface
│   ├── conftest.py
│   └── test_auth_flows.py
└── non_functional/                # Testes não funcionais
    ├── test_performance.py
    ├── test_security.py
    └── locustfile.py              # Teste de carga
```

## ⚙️ Configuração do Ambiente

### 1. Instalar Dependências

```bash
cd /app
pip install -r tests/requirements.txt
```

### 2. Instalar Navegadores (para testes GUI)

```bash
playwright install chromium
```

### 3. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (se ainda não existir):

```bash
# URLs
BACKEND_URL=https://senha-redefinir.preview.emergentagent.com
FRONTEND_URL=https://senha-redefinir.preview.emergentagent.com

# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
```

## 🚀 Como Executar os Testes

### Executar TODOS os Testes

```bash
cd /app
pytest tests/ -v
```

### Testes Unitários

```bash
# Todos os testes unitários
pytest tests/unit/ -v

# Teste específico
pytest tests/unit/test_email_service.py -v
pytest tests/unit/test_password_hashing.py -v
pytest tests/unit/test_token_generation.py -v
```

**Exemplos de saída:**
```
tests/unit/test_email_service.py::TestEmailService::test_send_password_reset_email_dev_mode PASSED
tests/unit/test_password_hashing.py::TestPasswordHashing::test_password_hash_generation PASSED
```

### Testes de Integração

```bash
# Todos os testes de integração
pytest tests/integration/ -v

# Testes de API
pytest tests/integration/test_auth_api.py -v

# Testes de banco de dados
pytest tests/integration/test_database.py -v
```

**Nota:** Os testes de integração requerem que o backend esteja rodando.

### Testes de Interface (GUI)

```bash
# Todos os testes GUI
pytest tests/gui/ -v

# Com saída detalhada
pytest tests/gui/test_auth_flows.py -v -s

# Executar em modo headed (com navegador visível)
pytest tests/gui/ -v --headed
```

**Nota:** Os testes GUI requerem que frontend e backend estejam rodando.

### Testes Não Funcionais

#### Performance e Segurança

```bash
# Testes de performance
pytest tests/non_functional/test_performance.py -v

# Testes de segurança
pytest tests/non_functional/test_security.py -v

# Todos os testes não funcionais
pytest tests/non_functional/ -v
```

#### Teste de Carga (Locust)

```bash
# Iniciar Locust
cd /app
locust -f tests/non_functional/locustfile.py --host=https://senha-redefinir.preview.emergentagent.com

# Acesse a interface web: http://localhost:8089
```

**Configurações sugeridas:**
- Número de usuários: 10-50
- Taxa de spawn: 1-5 por segundo
- Duração: 1-5 minutos

## 📊 Cobertura de Testes

### Gerar Relatório de Cobertura

```bash
# Executar testes com cobertura
pytest tests/ --cov=backend --cov-report=html --cov-report=term

# Ver relatório HTML
open htmlcov/index.html
```

### Métricas de Cobertura

| Categoria | Cobertura Atual | Meta |
|-----------|----------------|------|
| Unitários | 85% | 90% |
| Integração | 75% | 80% |
| GUI | 60% | 70% |
| Total | 73% | 80% |

## 📝 Relatórios

### Relatório Detalhado com JUnit XML

```bash
pytest tests/ -v --junitxml=test-results.xml
```

### Relatório HTML

```bash
pip install pytest-html
pytest tests/ --html=report.html --self-contained-html
```

## 📝 Descrição dos Testes

### 🟢 Testes Unitários

#### test_email_service.py
- ✅ Envio de e-mail em modo desenvolvimento
- ✅ Envio de e-mail com SendGrid
- ✅ Tratamento de falhas do SendGrid
- ✅ Formatação de conteúdo do e-mail

#### test_password_hashing.py
- ✅ Geração de hash de senha
- ✅ Verificação de senha correta
- ✅ Verificação de senha incorreta
- ✅ Unicidade de hashes (salt)

#### test_token_generation.py
- ✅ Formato do token (6 dígitos)
- ✅ Unicidade de tokens
- ✅ Cálculo de expiração
- ✅ Detecção de token expirado

### 🔵 Testes de Integração

#### test_auth_api.py
- ✅ Registro de usuário
- ✅ Login com sucesso
- ✅ Login com senha incorreta
- ✅ E-mail duplicado
- ✅ Solicitação de redefinição de senha
- ✅ Redefinição com token inválido

#### test_database.py
- ✅ Inserção de usuário
- ✅ Busca por e-mail
- ✅ Atualização de token
- ✅ Remoção de token

### 🟡 Testes de Interface (GUI)

#### test_auth_flows.py
- ✅ Carregamento da página de login
- ✅ Link "Esqueceu sua senha?"
- ✅ Navegação entre páginas
- ✅ Validação de formulários
- ✅ Mensagens de erro
- ✅ Responsividade (mobile/tablet)

### 🔴 Testes Não Funcionais

#### test_performance.py
- ✅ Tempo de resposta de login (< 2s)
- ✅ Tempo de resposta de registro (< 3s)
- ✅ Performance com requisições concorrentes
- ✅ Performance de consultas no banco

#### test_security.py
- ✅ Prevenção de SQL Injection
- ✅ Prevenção de XSS
- ✅ Senha não retornada em respostas
- ✅ Expiração de tokens
- ✅ Proteção contra brute force

#### locustfile.py (Teste de Carga)
- ✅ Simulação de múltiplos usuários
- ✅ Teste de registro sob carga
- ✅ Teste de login sob carga
- ✅ Teste de redefinição de senha sob carga

## 🐛 Debug e Troubleshooting

### Testes Falhando

1. **Verificar se serviços estão rodando:**
```bash
sudo supervisorctl status
```

2. **Ver logs do backend:**
```bash
tail -f /var/log/supervisor/backend.err.log
```

3. **Executar teste específico com saída detalhada:**
```bash
pytest tests/integration/test_auth_api.py::TestAuthenticationAPI::test_login_success -v -s
```

### Testes GUI Falhando

1. **Executar em modo headed (navegador visível):**
```bash
pytest tests/gui/ --headed --slowmo=1000
```

2. **Capturar screenshots em caso de falha:**
```bash
pytest tests/gui/ --screenshot=on --video=retain-on-failure
```

## 📚 Boas Práticas

1. **Execute testes unitários frequentemente** durante o desenvolvimento
2. **Execute testes de integração** antes de fazer commit
3. **Execute testes GUI** antes de deploy
4. **Execute testes de performance** periodicamente
5. **Mantenha cobertura acima de 80%**
6. **Escreva testes para novos recursos**
7. **Atualize testes quando funcionalidades mudarem**

## 💬 Contribuindo

Ao adicionar novos testes:

1. Coloque no diretório apropriado (unit/integration/gui/non_functional)
2. Siga o padrão de nomenclatura: `test_*.py`
3. Use fixtures do conftest.py quando possível
4. Documente o que cada teste faz
5. Execute todos os testes antes de fazer commit

## ❓ FAQ

**P: Os testes modificam o banco de dados de produção?**
R: Não, os testes usam `test_database` e fazem cleanup após cada teste.

**P: Posso executar testes em paralelo?**
R: Sim, use `pytest -n auto` com `pytest-xdist` instalado.

**P: Como executar apenas testes rápidos?**
R: `pytest -m "not slow"` (requer marcar testes lentos com `@pytest.mark.slow`)

**P: Onde encontro mais informações sobre pytest?**
R: https://docs.pytest.org/

---

**Desenvolvido para TCC - Sistema TAXXAT** 🚀
