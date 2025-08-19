# 📮 Postman - Guia dos Endpoints Flexíveis

## 🎯 Sim! Você pode usar o mesmo Postman + MUITO MAIS!

### ✅ **O que mudou:**
- **Novos endpoints flexíveis** que aceitam qualquer formato
- **Mapeamento automático** para o formato RCS
- **Compatibilidade total** com collections antigas
- **Mais facilidade** para testar

## 📁 Collections Disponíveis

### 🆕 **Nova Collection (Recomendada)**
- **Arquivo**: `RCS_Gateway_Flexible.postman_collection.json`
- **Environment**: `RCS_Gateway_Flexible.postman_environment.json`
- **Recursos**: Endpoints flexíveis + originais

### 📚 **Collections Antigas (Ainda Funcionam)**
- `RCS_Gateway_API.postman_collection.json`
- `RCS_Gateway_Client_API.postman_collection.json`
- `RCS_Gateway_Production_Complete.postman_collection.json`

## 🚀 Como Importar

### 1. Importar Nova Collection
```
1. Abra o Postman
2. Clique em "Import"
3. Selecione: RCS_Gateway_Flexible.postman_collection.json
4. Importe também: RCS_Gateway_Flexible.postman_environment.json
5. Selecione o environment "RCS Gateway - Flexible"
```

### 2. Configurar Variáveis
```
base_url: http://localhost:8000
api_key: jHID31pmJFi97TjO6rQVhKJGNqLdWXYZ8aBcEfGhIjKlMnOpQrStUvWxYz
test_phone: 11999999999
account_id: 2992
```

## 📱 Endpoints Flexíveis

### 🔥 **1. Super Simples (Query Params)**
```
POST /api/send/simple?phone=11999999999&message=Ola
Headers: X-API-Key: {{api_key}}
```
**Mais fácil impossível!**

### 📝 **2. Formato Simples (JSON)**
```json
POST /api/send
{
  "phone": "11999999999",
  "message": "Olá! Teste simples."
}
```

### 💬 **3. Formato WhatsApp-like**
```json
POST /api/send
{
  "number": "5511999999999",
  "text": "Mensagem WhatsApp style! 📱",
  "type": "text"
}
```

### 🎨 **4. Formato com Template**
```json
POST /api/send
{
  "to": "11999999999",
  "template": "welcome",
  "variables": {
    "name": "João",
    "product": "Smartphone"
  }
}
```

### 🤖 **5. Formato Telegram-like**
```json
POST /api/send
{
  "chat_id": "5511999999999",
  "text": "Mensagem Telegram style! 🚀"
}
```

## 🔄 Compatibilidade Total

### ✅ **Endpoints Originais Funcionam Igual**
- `/api/rcs/basic` - RCS Basic
- `/api/rcs/single` - RCS Single
- `/api/rcs/webhook` - RCS Webhook
- `/api/rcs/template` - RCS Template

### 🎯 **Vantagens dos Novos Endpoints**
- **Mais simples** de usar
- **Qualquer formato** aceito
- **Mapeamento automático**
- **Menos campos obrigatórios**

## 🧪 Testes Recomendados

### 1️⃣ **Teste Básico**
```
Endpoint: Super Simples
Resultado: Status 200 (sucesso)
```

### 2️⃣ **Teste de Autenticação**
```
Endpoint: Sem API Key
Resultado: Status 401 (erro esperado)
```

### 3️⃣ **Teste de Compatibilidade**
```
Endpoint: RCS Basic Original
Resultado: Status 200 (compatibilidade mantida)
```

## 📊 Respostas Esperadas

### ✅ **Sucesso (Status 200)**
```json
[
  {
    "id": 123,
    "status": "sent",
    "message": "Mensagem enviada com sucesso",
    "created_at": "2025-08-13T17:52:43Z"
  }
]
```

### ❌ **Erro de Autenticação (Status 401)**
```json
{
  "detail": "API Key inválida ou expirada"
}
```

### ⚠️ **Erro de Conta (Status 200 mas failed)**
```json
[
  {
    "id": 124,
    "status": "failed",
    "message": "Erro na API RCS: account does not exists",
    "created_at": "2025-08-13T17:52:43Z"
  }
]
```

## 🎯 Fluxo de Teste Recomendado

### 1. **Health Check**
```
GET /health
Deve retornar: {"status": "healthy"}
```

### 2. **Teste Super Simples**
```
POST /api/send/simple?phone=11999999999&message=Teste
Deve retornar: Status 200
```

### 3. **Teste Formato JSON**
```
POST /api/send
{"phone": "11999999999", "message": "Teste JSON"}
Deve retornar: Status 200
```

### 4. **Verificar Mensagem**
```
GET /api/messages
Deve listar as mensagens enviadas
```

## 💡 Dicas Importantes

### 🔑 **API Key**
- **Sempre obrigatória** no header `X-API-Key`
- **Mesma API Key** para todos os endpoints
- **Não mudou nada** na autenticação

### 📱 **Números de Telefone**
- **Aceita qualquer formato**: 11999999999, 5511999999999
- **Normalização automática** para formato brasileiro
- **Código do país** adicionado automaticamente

### 🎨 **Formatos**
- **Qualquer formato** é aceito no `/api/send`
- **Mapeamento automático** para RCS
- **Compatibilidade total** mantida

## 🚀 Próximos Passos

1. **Importe a nova collection**
2. **Teste os endpoints flexíveis**
3. **Use o formato que preferir**
4. **Mantenha as collections antigas** (ainda funcionam)

## 🎉 Resumo

**Antes**: Só formato RCS complexo
**Agora**: Qualquer formato + RCS original

**Você pode usar:**
- ✅ Collections antigas (funcionam igual)
- ✅ Nova collection (mais flexível)
- ✅ Qualquer formato de requisição
- ✅ Mapeamento automático

**O Postman ficou ainda mais poderoso!** 🚀
