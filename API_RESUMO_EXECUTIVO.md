# RCS Gateway API - Resumo Executivo para Validação

## 📋 Informações Gerais

**Nome:** RCS Gateway API with Authentication  
**Versão:** 2.0.0  
**Protocolo:** OpenAPI 3.1.0  
**Base URL:** `http://localhost:8000` (desenvolvimento)  
**Documentação Interativa:** `/docs`  

## 🎯 Objetivo

Gateway em Python para integração com a API RCS da Eugen com sistema completo de autenticação JWT e multi-tenancy, permitindo que múltiplos clientes utilizem a plataforma de forma isolada e segura.

## 🏗️ Arquitetura

### **Multi-tenancy**
- Isolamento completo entre clientes
- Cada cliente possui suas próprias mensagens, templates e usuários
- Autenticação via API Key por cliente

### **Dois Níveis de Acesso**
1. **Administradores**: Gerenciam clientes, usuários e API Keys via JWT
2. **Clientes**: Enviam mensagens e consultam dados via API Key

## 📡 Endpoints Principais

### **Para Clientes (Uso Principal)**

#### 1. **Envio de Mensagens** - `POST /api/client/send-message`
**Função:** Endpoint unificado para envio de mensagens RCS
- Suporte a mensagens básicas e rich content
- Uso de templates ou conteúdo personalizado
- Substituição automática de variáveis
- Callback configurável

**Autenticação:** Header `X-API-Key`

**Exemplo:**
```json
{
  "client_code": "CLI_ABC123",
  "message_type": "basic",
  "phone_numbers": ["5511999999999"],
  "content": {
    "text": {
      "message": "Olá {{nome}}! Seu pedido está pronto."
    }
  },
  "variables": {
    "nome": "João Silva"
  }
}
```

#### 2. **Consulta de Mensagens** - `GET /api/client/messages`
**Função:** Consultar histórico de mensagens enviadas
- Filtros por data, status, número
- Paginação de resultados
- Apenas mensagens do próprio cliente

**Parâmetros:**
- `client_code` (obrigatório)
- `start_date`, `end_date` (opcional)
- `status`, `phone_number` (opcional)
- `limit`, `offset` (paginação)

#### 3. **Consulta Individual** - `GET /api/client/messages/{client_message_id}`
**Função:** Detalhes de mensagem específica

#### 4. **Estatísticas** - `GET /api/client/stats`
**Função:** Relatórios de uso e performance do cliente

### **Para Administradores**

#### 1. **Autenticação** - `POST /api/auth/login`
**Função:** Login JWT para administradores

#### 2. **Gerenciamento de Clientes**
- `POST /api/admin/clients` - Criar cliente
- `GET /api/admin/clients` - Listar clientes
- `GET /api/admin/clients/{id}` - Obter cliente
- `PUT /api/admin/clients/{id}` - Atualizar cliente

#### 3. **Gerenciamento de Usuários**
- `POST /api/admin/users` - Criar usuário
- `GET /api/admin/users` - Listar usuários
- `GET /api/admin/users/{id}` - Obter usuário
- `PUT /api/admin/users/{id}` - Atualizar usuário

#### 4. **Gerenciamento de API Keys**
- `POST /api/admin/api-keys` - Criar API Key
- `GET /api/admin/api-keys` - Listar API Keys
- `DELETE /api/admin/api-keys/{id}` - Desativar API Key

#### 5. **Templates**
- `GET /api/client/templates` - Listar templates
- `POST /api/client/templates` - Criar template

### **Endpoints de Sistema**

#### 1. **Health Check** - `GET /health`
**Função:** Verificar status da aplicação

#### 2. **Informações da API** - `GET /api/info`
**Função:** Detalhes técnicos da API

#### 3. **Documentação** - `GET /docs`
**Função:** Interface Swagger interativa

### **Endpoints Legacy (Compatibilidade)**

Mantidos para compatibilidade com versões anteriores:
- `POST /api/rcs/basic` - Mensagem básica (deprecated)
- `POST /api/rcs/single` - Mensagem rica (deprecated)
- `GET /api/messages` - Listar mensagens (deprecated)
- `POST /api/rcs/callback` - Callback RCS (ainda usado)

## 📱 Tipos de Mensagem Suportados

### **1. Basic Messages**
- Texto simples até 160 caracteres
- Substituição de variáveis
- Se a mensagem for prrenchida sera feito o Fallback SMS automático

### **2. Rich Content (Single)**
- **Rich Cards**: Imagem + texto + botões
- **Carousel**: Múltiplos cards deslizáveis
- **Imagens**: JPEG, PNG, GIF (até 2MB)
- **Vídeos**: MP4 (até 50MB)
- **PDFs**: Documentos hospedados

### **3. Botões Interativos**
- **openUrl**: Abrir link HTTPS
- **call**: Realizar chamada
- **reply**: Resposta automática

## 🔐 Segurança e Autenticação

### **Para Administradores**
- **JWT Bearer Token** no header `Authorization`
- Acesso completo ao sistema
- Gerenciamento de clientes e usuários

### **Para Clientes**
- **API Key** no header `X-API-Key`
- Acesso restrito aos próprios recursos
- Rate limiting configurável
- Scopes de permissão

### **Recursos de Segurança**
- Isolamento multi-tenant
- Validação rigorosa de dados
- Rate limiting por cliente
- Logs de auditoria
- Expiração de API Keys

## 📊 Modelos de Dados Principais

### **Client (Cliente)**
```json
{
  "id": "string",
  "client_code": "CLI_ABC123",
  "name": "Nome do Cliente",
  "email": "cliente@exemplo.com",
  "rcs_account": "15886",
  "is_active": true,
  "allowed_message_types": ["basic", "single"],
  "max_messages_per_day": "1000",
  "callback_url": "https://cliente.com/callback"
}
```

### **APIKey**
```json
{
  "id": "string",
  "client_id": "string",
  "api_key": "rcs_live_abc123...",
  "key_name": "Produção",
  "scopes": ["send_messages", "view_messages"],
  "requests_per_minute": "60",
  "requests_per_day": "1000",
  "is_active": true,
  "expires_at": "2025-12-31T23:59:59Z"
}
```

### **Message Response**
```json
{
  "id": "string",
  "client_message_id": "CLI_ABC123_a1b2c3d4",
  "phone_number": "5511999999999",
  "status": "delivered",
  "message_type": "basic",
  "campaign_name": "Promocao_Janeiro",
  "sent_at": "2025-01-15T10:30:00Z",
  "delivered_at": "2025-01-15T10:31:00Z",
  "created_at": "2025-01-15T10:30:00Z"
}
```

## 🚀 Fluxo de Integração Recomendado

### **1. Setup Inicial (Admin)**
1. Login como administrador
2. Criar cliente via `POST /api/admin/clients`
3. Criar usuário para o cliente via `POST /api/admin/users`
4. Gerar API Key via `POST /api/admin/api-keys`

### **2. Uso pelo Cliente**
1. Configurar API Key no header `X-API-Key`
2. Enviar mensagens via `POST /api/client/send-message`
3. Consultar status via `GET /api/client/messages`
4. Monitorar estatísticas via `GET /api/client/stats`

### **3. Callbacks**
- Configure `callback_url` no cliente
- Receba notificações de status automaticamente
- Processe respostas de usuários

## 📈 Recursos Avançados

### **Templates**
- Criação de templates reutilizáveis
- Substituição automática de variáveis
- Versionamento e controle de uso

### **Rate Limiting**
- Controle por minuto e por dia
- Configurável por cliente
- Resposta HTTP 429 quando excedido

### **Multi-tenancy**
- Isolamento completo de dados
- Configurações independentes por cliente
- Relatórios individualizados

### **Monitoramento**
- Health checks automáticos
- Logs detalhados de auditoria
- Métricas de performance

## 🔧 Configuração e Deploy

### **Variáveis de Ambiente**
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
RCS_API_TOKEN=token_eugen
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
DEBUG=False
```

### **Docker Support**
- Dockerfile incluído
- Docker Compose com PostgreSQL
- Configuração para produção

## 📞 Suporte e Contato

**Suporte Técnico:** suporte@exemplo.com  
**Documentação:** `/docs` (Swagger UI)  
**API Info:** `/api/info`  
**Health Check:** `/health`

---

## ✅ Checklist de Validação

- [ ] Autenticação JWT para admins funcional
- [ ] Autenticação API Key para clientes funcional
- [ ] Multi-tenancy com isolamento completo
- [ ] Envio de mensagens básicas
- [ ] Envio de rich content (cards, carousel)
- [ ] Sistema de templates
- [ ] Consulta de mensagens com filtros
- [ ] Callbacks da Eugen
- [ ] Rate limiting configurável
- [ ] Documentação Swagger completa
- [ ] Health checks e monitoramento
- [ ] Deploy via Docker

**Status:** ✅ **PRONTO PARA VALIDAÇÃO**
