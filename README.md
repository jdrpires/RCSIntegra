# RCS Gateway API

Gateway em Python para integração com a API RCS da PontalTech. Este sistema recebe dados, armazena no banco de dados PostgreSQL e dispara mensagens para a API RCS.

## Funcionalidades

- ✅ **RCS Basic**: Mensagens simples com fallback SMS
- ✅ **RCS Single**: Mensagens com templates ou conteúdo personalizado
- ✅ **RCS Conversacional (Webhook)**: Mensagens interativas com webhook
- ✅ **RCS Conversacional (Template)**: Mensagens usando templates pré-criados
- ✅ **Criação de Templates**: Criação e armazenamento de templates
- ✅ **Callbacks**: Recebimento de status de entrega e respostas
- ✅ **Banco de Dados**: Armazenamento completo de mensagens e templates
- ✅ **Validação**: Validação de números de telefone e conteúdo
- ✅ **Logs**: Sistema completo de logging
- ✅ **API REST**: Interface completa com FastAPI

## Tipos de Conteúdo Suportados

- **Text**: Mensagens de texto (até 5.000 caracteres)
- **Image**: Imagens ou GIFs via HTTPS (máx. 2MB)
- **Video**: Vídeos via HTTPS (máx. 50MB)
- **PDF**: Arquivos PDF hospedados
- **Suggestion**: Até 4 botões clicáveis
- **RichCard**: Cartão com mídia, texto e botões
- **Carousel**: Conjunto de cartões em carrossel

## Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd RCSIntegra
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o banco de dados PostgreSQL
```bash
# Instale PostgreSQL se necessário
brew install postgresql  # macOS
# ou
sudo apt-get install postgresql postgresql-contrib  # Ubuntu

# Crie o banco de dados
createdb rcs_gateway
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/rcs_gateway

# RCS API Configuration
RCS_API_BASE_URL=https://pointer-rcs-api-node.pontaltech.com.br
RCS_API_TOKEN=seu_token_bearer_aqui

# Gateway Configuration
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
DEBUG=True
```

### 5. Inicialize o banco de dados
```bash
python init_db.py
```

### 6. Execute o servidor
```bash
python main.py
```

O servidor estará disponível em `http://localhost:8000`

## Uso da API

### Documentação Interativa
Acesse `http://localhost:8000/docs` para ver a documentação interativa do Swagger.

### Endpoints Principais

#### 1. RCS Basic - Mensagem Simples
```bash
POST /api/rcs/basic
```

Exemplo:
```json
{
  "campaign_name": "Campanha Teste",
  "account": "sua_conta_id",
  "messages": [
    {
      "number": "5511999999999",
      "vars": {
        "nome": "João",
        "produto": "Smartphone"
      }
    }
  ],
  "content": {
    "text": {
      "message": "Olá {{nome}}, seu {{produto}} está disponível!"
    }
  },
  "callback": "https://seu-dominio.com/callback",
  "fallback": [
    {
      "channel": "SMS",
      "content": "Ola {{nome}}, seu {{produto}} esta disponivel!"
    }
  ]
}
```

#### 2. RCS Single - Rich Card
```bash
POST /api/rcs/single
```

Exemplo:
```json
{
  "account": "sua_conta_id",
  "messages": [
    {
      "number": "5511999999999"
    }
  ],
  "content": {
    "richCard": {
      "title": "Oferta Especial!",
      "description": "Aproveite 20% de desconto em todos os produtos.",
      "fileUrl": "https://exemplo.com/promocao.jpg",
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
}
```

#### 3. RCS Conversacional (Webhook)
```bash
POST /api/rcs/webhook
```

Exemplo:
```json
{
  "account": "sua_conta_id",
  "webhook": "https://seu-dominio.com/webhook-rcs",
  "messages": [
    {
      "number": "5511999999999"
    }
  ],
  "content": {
    "text": {
      "message": "Como posso ajudá-lo hoje?"
    }
  }
}
```

#### 4. Criar Template
```bash
POST /api/rcs/templates
```

Exemplo:
```json
{
  "name": "Template Boas Vindas",
  "account": "sua_conta_id",
  "content_type": "richCard",
  "template_data": {
    "title": "Bem-vindo {{nome}}!",
    "description": "Obrigado por se cadastrar!",
    "fileUrl": "https://exemplo.com/boas-vindas.jpg",
    "suggestions": [
      {
        "type": "openUrl",
        "title": "Explorar",
        "value": "https://loja.exemplo.com"
      }
    ]
  }
}
```

#### 5. Consultar Status de Mensagem
```bash
GET /api/messages/{message_id}
```

#### 6. Listar Mensagens
```bash
GET /api/messages?status=sent&skip=0&limit=100
```

#### 7. Receber Callbacks
```bash
POST /api/rcs/callback
```

Este endpoint recebe automaticamente os callbacks da API RCS.

## Estrutura do Banco de Dados

### Tabela: rcs_messages
Armazena todas as mensagens enviadas com status e metadados.

### Tabela: rcs_templates
Armazena templates criados via API.

### Tabela: rcs_callbacks
Armazena callbacks recebidos (status de entrega, respostas).

## Exemplos de Uso

Execute o arquivo `examples.py` para ver exemplos práticos:

```bash
python examples.py
```

## Tipos de Botões Suportados

- **openUrl**: Abre um link HTTPS
- **call**: Realiza chamada telefônica
- **reply**: Envia resposta automática

## Validações Automáticas

- **Números de telefone**: Formatação automática com código do país
- **Conteúdo fallback**: Remove acentos e limita a 160 caracteres
- **URLs**: Validação de URLs HTTPS para mídias
- **Limites de caracteres**: Validação conforme especificação da API

## Logs e Monitoramento

O sistema gera logs detalhados para:
- Requisições recebidas
- Chamadas para API RCS
- Erros e exceções
- Status de mensagens
- Callbacks recebidos

## Tratamento de Erros

- **Validação de dados**: Retorna erros 400 com detalhes
- **Falhas na API**: Armazena erro no banco e retorna status
- **Timeout**: Configuração de timeout para requisições
- **Retry**: Implementação de retry pode ser adicionada

## Segurança

- **Bearer Token**: Autenticação via token da PontalTech
- **CORS**: Configuração de CORS para APIs web
- **Validação**: Validação rigorosa de todos os dados de entrada
- **Logs**: Não exposição de dados sensíveis nos logs

## Testes

O projeto inclui uma suíte completa de testes automatizados e manuais.

### Testes Automatizados

#### Instalação das dependências de teste
```bash
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

#### Executar todos os testes
```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar com relatório de cobertura
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

# Executar testes específicos
python -m pytest tests/test_rcs_basic.py -v
python -m pytest tests/test_rcs_single.py -v
python -m pytest tests/test_templates.py -v
```

#### Script automatizado
```bash
# Executar script que roda todos os testes e gera relatórios
python run_tests.py
```

### Estrutura dos Testes

- **`tests/test_rcs_basic.py`** - Testes para mensagens RCS Basic
- **`tests/test_rcs_single.py`** - Testes para mensagens RCS Single (Rich Cards, Carousel, etc.)
- **`tests/test_rcs_webhook.py`** - Testes para mensagens conversacionais e callbacks
- **`tests/test_templates.py`** - Testes para criação e uso de templates
- **`tests/test_validations.py`** - Testes para validações (telefone, URLs, conteúdo)

### Testes Manuais

Para testes manuais com a API real:

```bash
# Configure seu token no .env primeiro
python test_examples_manual.py
```

Este script testa:
- ✅ Envio de mensagens básicas
- ✅ Rich Cards com botões
- ✅ Carousels com múltiplos cards
- ✅ Mensagens conversacionais
- ✅ Criação e uso de templates
- ✅ Listagem de mensagens e templates

### Teste de Todos os Templates

Para testar todos os templates existentes enviando para um número específico:

```bash
# Teste completo com interface interativa
python test_all_templates.py

# Teste direto e rápido para número específico (11998637834)
python send_all_templates_to_number.py

# Teste automatizado (com mocks)
python -m pytest tests/test_send_all_templates.py -v
```

**Funcionalidades dos testes de templates:**
- 🔍 Busca automaticamente todos os templates
- 🧠 Gera variáveis inteligentemente baseadas no conteúdo
- 📱 Envia para número específico (11998637834)
- 📊 Relatório detalhado de sucessos/falhas
- ⏱️ Controle de tempo entre envios
- 🛡️ Validação de conexão e erros

### Cobertura de Testes

Os testes cobrem:

- **Endpoints da API**: Todos os endpoints principais
- **Validações**: Números de telefone, URLs, limites de caracteres
- **Substituição de variáveis**: Templates e mensagens dinâmicas
- **Tipos de conteúdo**: Texto, imagem, vídeo, PDF, Rich Cards, Carousel
- **Fallback SMS**: Sanitização e limites de caracteres
- **Callbacks**: Recebimento de status e respostas
- **Banco de dados**: Armazenamento e consulta de dados
- **Tratamento de erros**: Cenários de falha da API

### Executar Testes no Docker

```bash
# Subir ambiente de teste
docker-compose --env-file .env.docker.local up -d

# Executar testes dentro do container
docker-compose exec rcs_gateway python -m pytest tests/ -v

# Ou executar testes manuais
docker-compose exec rcs_gateway python test_examples_manual.py
```

## Desenvolvimento

### Estrutura do Projeto
```
RCSIntegra/
├── main.py              # Aplicação FastAPI principal
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Schemas Pydantic
├── database.py          # Configuração do banco
├── rcs_client.py        # Cliente da API RCS
├── services.py          # Lógica de negócio
├── init_db.py          # Inicialização do banco
├── examples.py          # Exemplos de uso
├── requirements.txt     # Dependências
├── .env.example        # Exemplo de configuração
└── README.md           # Documentação
```

### Executar em Desenvolvimento
```bash
# Com reload automático
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Executar em Produção
```bash
# Com Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Deploy

### Docker Compose (Recomendado)

O projeto inclui configuração completa para Docker Compose com PostgreSQL e a aplicação.

#### 1. Configurar variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.docker .env.docker.local

# Edite com seu token da API RCS
nano .env.docker.local
```

Conteúdo do `.env.docker.local`:
```env
# RCS API Configuration
RCS_API_TOKEN=seu_token_bearer_real_aqui
```

#### 2. Subir os serviços
```bash
# Subir todos os serviços (PostgreSQL + RCS Gateway)
docker-compose --env-file .env.docker.local up -d

# Ou para ver os logs em tempo real
docker-compose --env-file .env.docker.local up
```

#### 3. Verificar se os serviços estão rodando
```bash
# Ver status dos containers
docker-compose ps

# Ver logs da aplicação
docker-compose logs rcs_gateway

# Ver logs do PostgreSQL
docker-compose logs postgres
```

#### 4. Acessar a aplicação
- API: `http://localhost:8000`
- Documentação: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

#### 5. Comandos úteis
```bash
# Parar os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados do banco)
docker-compose down -v

# Rebuild da aplicação após mudanças no código
docker-compose build rcs_gateway
docker-compose up -d rcs_gateway

# Executar comandos dentro do container
docker-compose exec rcs_gateway python init_db.py
docker-compose exec postgres psql -U rcsintegra -d rcsintegra
```

### Docker Manual (Alternativo)

Se preferir usar Docker sem Compose:

```bash
# 1. Criar rede
docker network create rcs_network

# 2. Subir PostgreSQL
docker run -d \
  --name rcs_postgres \
  --network rcs_network \
  -e POSTGRES_USER=rcsintegra \
  -e POSTGRES_PASSWORD=Rc\$1nT3gR@2025! \
  -e POSTGRES_DB=rcsintegra \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# 3. Build da aplicação
docker build -t rcs_gateway .

# 4. Subir aplicação
docker run -d \
  --name rcs_gateway \
  --network rcs_network \
  -e DATABASE_URL=postgresql://rcsintegra:Rc\$1nT3gR@2025!@rcs_postgres:5432/rcsintegra \
  -e RCS_API_TOKEN=seu_token_aqui \
  -p 8000:8000 \
  rcs_gateway
```

### Variáveis de Ambiente para Produção
```env
DATABASE_URL=postgresql://rcsintegra:Rc$1nT3gR@2025!@postgres:5432/rcsintegra
RCS_API_TOKEN=seu_token_producao
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
DEBUG=False
```

## Suporte

Para dúvidas sobre a API RCS da PontalTech, entre em contato:
- Email: apoio.ca@pontaltech.com.br

Para questões sobre este gateway, abra uma issue no repositório.

## Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.
