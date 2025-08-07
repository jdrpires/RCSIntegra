# 📮 RCS Gateway - Collection do Postman

Collection completa para testar o RCS Gateway em produção no servidor `api-plataform.com:8000`.

## 🚀 Como Usar

### 1. **Importar Collection**
```bash
# Arquivo principal (mais completo)
RCS_Gateway_Production_Complete.postman_collection.json

# Arquivo básico (versão simplificada)
RCS_Gateway_Production.postman_collection.json
```

### 2. **Configurar Variáveis**
As variáveis já estão pré-configuradas, mas você pode ajustar:

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `base_url` | `http://api-plataform.com:8000` | URL base da API |
| `account_id` | `15885` | ID da conta RCS |
| `test_phone` | `5516982089942` | Número para testes |

### 3. **Ordem de Execução Recomendada**

#### 🏥 **Passo 1: Health Check**
1. **API Health Check** - Verifica se a API está funcionando
2. **API Documentation** - Testa acesso à documentação

#### 📱 **Passo 2: Envio de Mensagens**
1. **RCS Basic - Texto Simples** - Mensagem básica com fallback SMS
2. **RCS Single - Rich Card** - Cartão rico com botões
3. **RCS Webhook - Conversacional** - Mensagem com webhook ativo

#### 📋 **Passo 3: Templates**
1. **Criar Template - Rich Card** - Cria um template de exemplo
2. **Listar Todos os Templates** - Lista templates existentes
3. **Usar Template Criado** - Envia mensagem usando template

#### 📊 **Passo 4: Consultas**
1. **Listar Mensagens Recentes** - Últimas 10 mensagens
2. **Consultar Mensagem Específica** - Detalhes de uma mensagem
3. **Filtrar Mensagens por Status** - Mensagens por status

#### 🔄 **Passo 5: Callbacks**
1. **Simular Callback de Entrega** - Simula callback de status
2. **Simular Resposta do Usuário** - Simula resposta do usuário

## 🧪 Testes Automatizados

Cada requisição inclui testes automatizados que verificam:

### ✅ **Testes Básicos**
- Status code 200
- Tempo de resposta < 2000ms
- Estrutura da resposta

### ✅ **Testes Específicos**
- **Health Check**: Verifica se API está "healthy"
- **Mensagens**: Valida ID e status da mensagem
- **Templates**: Confirma criação e estrutura
- **Consultas**: Valida estrutura dos dados

### ✅ **Variáveis Dinâmicas**
- IDs de mensagens são salvos automaticamente
- Template IDs são reutilizados entre requisições
- Logs detalhados no console do Postman

## 📊 Interpretando Resultados

### **Status das Mensagens**
- `sent` - Mensagem enviada com sucesso
- `failed` - Falha no envio (geralmente IP não liberado)
- `delivered` - Mensagem entregue ao dispositivo
- `read` - Mensagem lida pelo usuário

### **Códigos de Erro Comuns**
- `403 Forbidden` - IP não liberado na PontalTech
- `400 Bad Request` - Dados inválidos na requisição
- `500 Internal Server Error` - Erro interno do servidor

## 🔧 Troubleshooting

### **Problema: Mensagens com status "failed"**
```json
{
  "status": "failed",
  "message": "IP address is not allowed: 195.26.251.151"
}
```
**Solução**: Solicitar liberação do IP para `apoio.ca@pontaltech.com.br`

### **Problema: Template não encontrado**
```json
{
  "error": "Template not found"
}
```
**Solução**: Execute "Criar Template" antes de "Usar Template"

### **Problema: Timeout na requisição**
**Solução**: Verificar se o servidor está rodando:
```bash
curl http://api-plataform.com:8000/
```

## 📈 Monitoramento

### **Logs em Tempo Real**
```bash
# Ver logs da aplicação
docker-compose logs -f rcs_gateway

# Ver logs do Nginx (se usando)
sudo tail -f /var/log/nginx/access.log
```

### **Verificar Status do Sistema**
```bash
# Status dos containers
docker-compose ps

# Teste rápido da API
curl -s http://api-plataform.com:8000/ | jq .
```

## 🎯 Cenários de Teste

### **Teste Completo de Funcionalidade**
1. Execute todos os requests na ordem recomendada
2. Verifique se todos os testes passaram
3. Confirme que as mensagens foram criadas no banco

### **Teste de Performance**
1. Execute "Listar Mensagens Recentes" várias vezes
2. Verifique tempo de resposta consistente
3. Monitore uso de recursos do servidor

### **Teste de Integração**
1. Crie um template
2. Use o template para enviar mensagem
3. Consulte o status da mensagem
4. Simule callback de entrega

## 📧 URLs Importantes

- **🌐 API**: http://api-plataform.com:8000
- **📚 Documentação**: http://api-plataform.com:8000/docs
- **🔗 Callback**: http://api-plataform.com:8000/api/rcs/callback
- **❤️ Health**: http://api-plataform.com:8000/

## 🆘 Suporte

Para problemas com a collection:
1. Verifique se o servidor está rodando
2. Confirme as variáveis de ambiente
3. Execute os testes na ordem recomendada
4. Consulte os logs para detalhes de erros

**Sistema funcionando perfeitamente! 🎉**
