# 📮 Guia da Collection Postman - Autenticação RCS Gateway

## 📥 Como Importar

### 1. Importar Collection
1. Abra o Postman
2. Clique em **Import**
3. Selecione o arquivo: `RCS_Gateway_Authentication.postman_collection.json`
4. Clique em **Import**

### 2. Importar Environment
1. No Postman, vá em **Environments**
2. Clique em **Import**
3. Selecione o arquivo: `RCS_Gateway_Authentication.postman_environment.json`
4. Clique em **Import**
5. **Ative o environment** selecionando-o no dropdown

## 🧪 Testes Disponíveis

### 🔍 **1. Health Check**
- **Método:** GET
- **URL:** `/health`
- **Objetivo:** Verificar se a API está funcionando

### 🔐 **2. Testes de Login**

#### Login Admin
- **Credenciais:** admin / Admin123!
- **Auto-salva:** Token e client_code nas variáveis

#### Login Demo  
- **Credenciais:** demo / Demo123!
- **Auto-salva:** Token e client_code nas variáveis

#### Login Teste
- **Credenciais:** teste / Teste123!
- **Auto-salva:** Token e client_code nas variáveis

#### Login com Credenciais Inválidas
- **Objetivo:** Testar rejeição de credenciais incorretas
- **Esperado:** Status 401

### 👤 **3. Informações do Usuário**

#### Get User Info (Admin/Demo/Teste)
- **Usa:** Token salvo automaticamente
- **Retorna:** Dados do usuário logado

#### Access Without Token
- **Objetivo:** Testar proteção de endpoints
- **Esperado:** Status 401/403

### 🛠️ **4. Administração (Admin apenas)**

#### List Clients
- **Lista:** Todos os clientes cadastrados
- **Requer:** Token de admin

#### List Users
- **Lista:** Todos os usuários cadastrados
- **Requer:** Token de admin

#### List API Keys
- **Lista:** Todas as API Keys ativas
- **Requer:** Token de admin

#### Create New Client
- **Cria:** Novo cliente de teste
- **Dados:** Cliente Teste Postman

#### Create New User
- **Cria:** Novo usuário para cliente
- **Nota:** Precisa ajustar client_id manualmente

### 🚫 **5. Testes de Segurança**

#### Test Invalid Token
- **Objetivo:** Testar rejeição de tokens inválidos
- **Esperado:** Status 401

## 🔄 Ordem de Execução Recomendada

1. **Health Check** - Verificar se API está rodando
2. **Login Admin** - Fazer login e salvar token
3. **Get User Info (Admin)** - Testar token salvo
4. **List Clients** - Testar endpoint protegido
5. **Login Invalid Credentials** - Testar segurança
6. **Access Without Token** - Testar proteção
7. **Test Invalid Token** - Testar validação de token

## 🎯 Testes Automatizados

A collection inclui **testes automatizados** que verificam:

- ✅ Status codes corretos
- ✅ Presença de tokens nos responses
- ✅ Estrutura dos dados retornados
- ✅ Rejeição de credenciais inválidas
- ✅ Proteção de endpoints

### Como Ver Resultados
1. Execute uma requisição
2. Vá na aba **Test Results**
3. Veja os testes que passaram/falharam

## 🔧 Variáveis Automáticas

A collection salva automaticamente:

| Variável | Descrição |
|----------|-----------|
| `admin_token` | Token JWT do usuário admin |
| `demo_token` | Token JWT do usuário demo |
| `teste_token` | Token JWT do usuário teste |
| `admin_client_code` | Código do cliente admin |
| `demo_client_code` | Código do cliente demo |
| `teste_client_code` | Código do cliente teste |

## 🚀 Executar Todos os Testes

### Via Collection Runner
1. Clique nos **3 pontos** da collection
2. Selecione **Run collection**
3. Escolha o environment **RCS Gateway Authentication**
4. Clique em **Run RCS Gateway - Authentication Tests**

### Resultado Esperado
- ✅ 10+ testes passando
- ⚠️ Alguns podem falhar se API estiver offline

## 🔍 Troubleshooting

### API não responde
- Verifique se Docker está rodando: `docker-compose ps`
- Verifique se API está na porta 8000: `curl http://localhost:8000/health`

### Tokens expiram
- Execute novamente os requests de login
- Tokens têm validade de 24 horas

### Environment não ativo
- Certifique-se de selecionar o environment no dropdown
- Variáveis devem aparecer como `{{admin_token}}`

## 📊 Credenciais de Teste

| Usuário | Password | Permissões | Cliente |
|---------|----------|------------|---------|
| admin | Admin123! | Completas | CLI_2EDF5B7E |
| demo | Demo123! | Médias | CLI_57BC2C59 |
| teste | Teste123! | Básicas | CLI_5D67211A |

## 🎉 Próximos Passos

Após validar a autenticação, você pode:

1. **Testar endpoints de mensagens RCS**
2. **Criar collections para cada tipo de mensagem**
3. **Implementar testes de integração**
4. **Configurar CI/CD com Newman**

---

**✅ Collection pronta para uso! Importe e comece a testar!**