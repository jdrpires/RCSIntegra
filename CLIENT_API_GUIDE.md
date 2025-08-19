# 📱 RCS Gateway - Guia da API para Clientes

Este guia explica como usar a API RCS Gateway para enviar mensagens RCS através da sua aplicação.

## 🚀 Início Rápido

### 1. Importar Collection no Postman

1. Abra o Postman
2. Clique em **Import**
3. Selecione o arquivo `RCS_Gateway_Client_API.postman_collection.json`
4. A collection será importada com todos os exemplos

### 2. Configurar Variáveis

Após importar, configure as seguintes variáveis na collection:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `BASE_URL` | URL do servidor da API | `https://api.exemplo.com` |
| `API_KEY` | Sua chave de API | `jHID31pmJFi97TjO6rQVAzeC6WkZba6TII_Hn1q6nHY` |
| `CLIENT_CODE` | Seu código de cliente | `CLI_7FB141C8` |

**Como configurar:**
1. Clique com botão direito na collection
2. Selecione **Edit**
3. Vá na aba **Variables**
4. Preencha os valores na coluna **Current Value**

## 🔐 Autenticação

Todas as requisições devem incluir o header:
```
X-API-Key: sua_api_key_aqui
```

## 📤 Enviando Mensagens

### Mensagem Básica (Texto)

```bash
curl -X POST "https://api.exemplo.com/api/client/send-message" \
  -H "X-API-Key: sua_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "client_code": "CLI_ABC123",
    "message_type": "basic",
    "phone_numbers": ["5511999999999"],
    "content": {
      "text": {
        "message": "Olá! Esta é uma mensagem de teste."
      }
    }
  }'
```

### Rich Card com Botões

```bash
curl -X POST "https://api.exemplo.com/api/client/send-message" \
  -H "X-API-Key: sua_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "client_code": "CLI_ABC123",
    "message_type": "single",
    "phone_numbers": ["5511999999999"],
    "content": {
      "richCard": {
        "title": "Oferta Especial!",
        "description": "50% de desconto em todos os produtos",
        "fileUrl": "https://exemplo.com/imagem.jpg",
        "suggestions": [
          {
            "type": "openUrl",
            "title": "Ver Produtos",
            "value": "https://loja.exemplo.com"
          },
          {
            "type": "call",
            "title": "Ligar",
            "value": "1140001234"
          }
        ]
      }
    }
  }'
```

### Usando Templates

```bash
curl -X POST "https://api.exemplo.com/api/client/send-message" \
  -H "X-API-Key: sua_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "client_code": "CLI_ABC123",
    "message_type": "basic",
    "template_id": "template_001",
    "phone_numbers": ["5511999999999"],
    "variables": {
      "nome": "João",
      "produto": "Smartphone"
    }
  }'
```

## 📋 Consultando Mensagens

### Listar Mensagens

```bash
curl -X GET "https://api.exemplo.com/api/client/messages?client_code=CLI_ABC123" \
  -H "X-API-Key: sua_api_key"
```

### Filtrar por Status

```bash
curl -X GET "https://api.exemplo.com/api/client/messages?client_code=CLI_ABC123&status=delivered" \
  -H "X-API-Key: sua_api_key"
```

### Filtrar por Data

```bash
curl -X GET "https://api.exemplo.com/api/client/messages?client_code=CLI_ABC123&start_date=2025-01-01&end_date=2025-01-31" \
  -H "X-API-Key: sua_api_key"
```

## 📊 Estatísticas

```bash
curl -X GET "https://api.exemplo.com/api/client/stats" \
  -H "X-API-Key: sua_api_key"
```

## 📱 Tipos de Conteúdo Suportados

### 1. Texto Simples
```json
{
  "text": {
    "message": "Sua mensagem aqui"
  }
}
```

### 2. Rich Card
```json
{
  "richCard": {
    "title": "Título do Card",
    "description": "Descrição detalhada",
    "fileUrl": "https://exemplo.com/imagem.jpg",
    "suggestions": [
      {
        "type": "openUrl",
        "title": "Abrir Link",
        "value": "https://exemplo.com"
      }
    ]
  }
}
```

### 3. Tipos de Botões

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `openUrl` | Abre uma URL | `{"type": "openUrl", "title": "Ver Site", "value": "https://exemplo.com"}` |
| `call` | Faz chamada | `{"type": "call", "title": "Ligar", "value": "1140001234"}` |
| `reply` | Resposta automática | `{"type": "reply", "title": "Sim", "value": "Confirmo"}` |

## 🔄 Status das Mensagens

| Status | Descrição |
|--------|-----------|
| `pending` | Aguardando envio |
| `sent` | Enviada com sucesso |
| `delivered` | Entregue ao destinatário |
| `read` | Lida pelo destinatário |
| `failed` | Falha no envio |

## ⚠️ Limites e Restrições

### Limites Técnicos
- **Texto**: Máximo 5.000 caracteres
- **Imagens**: Máximo 2MB, formato JPEG/PNG
- **Vídeos**: Máximo 50MB, formato MP4
- **Botões**: Máximo 4 por Rich Card
- **Números por requisição**: Recomendado máximo 100

### Limites da Conta
- **Mensagens por dia**: Conforme seu plano contratado
- **Requisições por minuto**: Conforme configuração da API Key
- **Tipos de mensagem**: Conforme permissões da conta

## 🐛 Tratamento de Erros

### Códigos de Erro Comuns

| Código | Descrição | Solução |
|--------|-----------|---------|
| `401` | API Key inválida | Verifique sua API Key |
| `403` | Sem permissão | Contate o administrador |
| `404` | Recurso não encontrado | Verifique IDs e códigos |
| `429` | Muitas requisições | Aguarde e tente novamente |
| `500` | Erro interno | Contate o suporte |

### Exemplo de Resposta de Erro
```json
{
  "detail": "API Key inválida ou expirada"
}
```

## 📞 Suporte

### Informações de Contato
- **Email**: suporte@exemplo.com
- **Telefone**: (11) 4000-1234
- **Horário**: Segunda a Sexta, 9h às 18h

### Antes de Entrar em Contato
1. Verifique se sua API Key está correta
2. Confirme se o `client_code` está correto
3. Teste com a collection do Postman
4. Verifique os logs de erro

### Informações Úteis para Suporte
- Seu `client_code`
- Timestamp do erro
- Mensagem de erro completa
- Exemplo da requisição que falhou

## 🔄 Changelog

### Versão 2.0.0 (Janeiro 2025)
- ✅ Sistema de autenticação via API Key
- ✅ Multi-tenancy (isolamento entre clientes)
- ✅ Endpoint unificado para envio de mensagens
- ✅ Consulta de mensagens por cliente
- ✅ Estatísticas de uso
- ✅ Suporte a templates

### Versão 1.0.0 (Julho 2024)
- ✅ Envio de mensagens RCS Basic e Single
- ✅ Suporte a Rich Cards e Carousel
- ✅ Sistema de callbacks
- ✅ Fallback SMS automático

## 📚 Recursos Adicionais

- [Documentação Completa da API](http://localhost:8000/docs)
- [Especificação RCS](https://www.gsma.com/futurenetworks/rcs/)
- [Melhores Práticas para RCS](https://developers.google.com/business-communications/rcs-business-messaging/guides/learn/best-practices)

---

**💡 Dica**: Mantenha sua API Key segura e nunca a compartilhe em repositórios públicos ou logs de aplicação.
