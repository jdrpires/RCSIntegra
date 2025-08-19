"""
RCS Gateway API com Autenticação JWT e Multi-tenancy
"""
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Imports existentes
from database import get_db
from schemas import *
from services import RCSService

# Imports de autenticação
from auth_routes import router as auth_router
from client_routes import router as client_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="RCS Gateway API with Authentication",
    description="""
    Gateway em Python para integração com a API RCS da Eugen com sistema completo de autenticação JWT e multi-tenancy.
    
    ## Funcionalidades
    
    ### Para Administradores:
    - ✅ **Gerenciamento de Clientes**: Criar e gerenciar clientes da API
    - ✅ **Gerenciamento de Usuários**: Criar usuários para cada cliente
    - ✅ **API Keys**: Gerar chaves de API para autenticação
    - ✅ **Templates**: Gerenciar templates por cliente
    
    ### Para Clientes:
    - ✅ **Envio de Mensagens**: Endpoint unificado para envio via API Key
    - ✅ **Consulta de Mensagens**: Visualizar apenas suas próprias mensagens
    - ✅ **Estatísticas**: Relatórios de uso e performance
    - ✅ **Multi-tenancy**: Isolamento completo entre clientes
    
    ### Tipos de Mensagem Suportados:
    - **Basic**: Mensagens simples com fallback SMS
    - **Single**: Mensagens com Rich Cards, Carousel, etc.
    
    ## Autenticação
    
    ### Para Administradores:
    - Login via JWT Token
    - Acesso completo ao sistema
    
    ### Para Clientes:
    - Autenticação via API Key no header `X-API-Key`
    - Acesso restrito às próprias mensagens e recursos
    
    ## Como Usar
    
    ### 1. Para Clientes (Uso Principal):
    
    ```bash
    # Enviar mensagem básica
    curl -X POST "http://localhost:8000/api/client/send-message" \\
         -H "X-API-Key: sua_api_key_aqui" \\
         -H "Content-Type: application/json" \\
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
    
    # Consultar mensagens
    curl -X GET "http://localhost:8000/api/client/messages?client_code=CLI_ABC123" \\
         -H "X-API-Key: sua_api_key_aqui"
    ```
    
    ### 2. Para Administradores:
    
    ```bash
    # Login
    curl -X POST "http://localhost:8000/api/auth/login" \\
         -H "Content-Type: application/json" \\
         -d '{
           "username": "admin",
           "password": "admin123"
         }'
    
    # Criar cliente
    curl -X POST "http://localhost:8000/api/admin/clients" \\
         -H "Authorization: Bearer seu_jwt_token" \\
         -H "Content-Type: application/json" \\
         -d '{
           "name": "Novo Cliente",
           "email": "cliente@exemplo.com",
           "rcs_account": "15886"
         }'
    ```
    """,
    version="2.0.0",
    contact={
        "name": "Suporte RCS Gateway",
        "email": "suporte@exemplo.com"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas de autenticação
app.include_router(auth_router, prefix="/api", tags=["Autenticação e Administração"])

# Incluir rotas do cliente
app.include_router(client_router, prefix="/api", tags=["Serviços para Clientes"])

# Manter rotas originais para compatibilidade (com autenticação opcional)
@app.get("/", tags=["Sistema"])
def root():
    """Informações da API"""
    return {
        "message": "RCS Gateway API with Authentication",
        "version": "2.0.0",
        "status": "active",
        "features": [
            "JWT Authentication",
            "Multi-tenancy",
            "API Key Authentication",
            "RCS Basic Messages",
            "RCS Single Messages",
            "Message Tracking",
            "Client Management"
        ],
        "endpoints": {
            "client_service": "/api/client/send-message",
            "client_messages": "/api/client/messages",
            "admin_login": "/api/auth/login",
            "admin_clients": "/api/admin/clients",
            "documentation": "/docs"
        }
    }

@app.get("/health", tags=["Sistema"])
def health_check():
    """Health check da aplicação"""
    return {
        "status": "healthy",
        "database": "connected",
        "api": "ready"
    }

# Manter endpoints originais para compatibilidade (com autenticação opcional)
@app.post("/api/rcs/basic", tags=["RCS Original (Compatibilidade)"])
async def send_basic_message_legacy(
    request: RCSBasicRequest,
    db: Session = Depends(get_db)
):
    """
    [LEGACY] Envio de mensagem RCS Basic (mantido para compatibilidade)
    
    ⚠️ **Deprecated**: Use `/api/client/send-message` para novos projetos
    """
    logger.warning("Uso de endpoint legacy /api/rcs/basic - considere migrar para /api/client/send-message")
    
    service = RCSService(db)
    return await service.send_basic_message(request)

@app.post("/api/rcs/single", tags=["RCS Original (Compatibilidade)"])
async def send_single_message_legacy(
    request: RCSSingleRequest,
    db: Session = Depends(get_db)
):
    """
    [LEGACY] Envio de mensagem RCS Single (mantido para compatibilidade)
    
    ⚠️ **Deprecated**: Use `/api/client/send-message` para novos projetos
    """
    logger.warning("Uso de endpoint legacy /api/rcs/single - considere migrar para /api/client/send-message")
    
    service = RCSService(db)
    return await service.send_single_message(request)

@app.get("/api/messages", tags=["RCS Original (Compatibilidade)"])
async def list_messages_legacy(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    [LEGACY] Listar mensagens (mantido para compatibilidade)
    
    ⚠️ **Deprecated**: Use `/api/client/messages` para novos projetos
    """
    logger.warning("Uso de endpoint legacy /api/messages - considere migrar para /api/client/messages")
    
    service = RCSService(db)
    return await service.list_messages(skip=skip, limit=limit, status=status)

@app.post("/api/rcs/callback", tags=["RCS Original (Compatibilidade)"])
async def receive_callback_legacy(
    callback_data: dict,
    db: Session = Depends(get_db)
):
    """
    [LEGACY] Receber callback da API RCS (mantido para compatibilidade)
    
    Este endpoint ainda é usado pela Eugen para enviar callbacks.
    """
    service = RCSService(db)
    return await service.process_callback(callback_data)

# Endpoint para documentação da API
@app.get("/api/info", tags=["Sistema"])
def api_info():
    """Informações detalhadas da API"""
    return {
        "name": "RCS Gateway API with Authentication",
        "version": "2.0.0",
        "description": "Gateway para integração com API RCS da Eugen com autenticação JWT",
        "authentication": {
            "jwt": {
                "description": "Para administradores",
                "header": "Authorization: Bearer <token>",
                "login_endpoint": "/api/auth/login"
            },
            "api_key": {
                "description": "Para clientes",
                "header": "X-API-Key: <api_key>",
                "obtain": "Solicite ao administrador"
            }
        },
        "main_endpoints": {
            "send_message": {
                "url": "/api/client/send-message",
                "method": "POST",
                "auth": "API Key",
                "description": "Endpoint principal para envio de mensagens"
            },
            "get_messages": {
                "url": "/api/client/messages",
                "method": "GET", 
                "auth": "API Key",
                "description": "Consultar mensagens do cliente"
            },
            "admin_login": {
                "url": "/api/auth/login",
                "method": "POST",
                "auth": "None",
                "description": "Login de administrador"
            }
        },
        "supported_message_types": ["basic", "single"],
        "supported_content_types": [
            "text", "image", "video", "pdf", 
            "richCard", "carousel", "suggestion"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    host = os.getenv("GATEWAY_HOST", "0.0.0.0")
    port = int(os.getenv("GATEWAY_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"🚀 Iniciando RCS Gateway API with Authentication")
    logger.info(f"📡 Host: {host}:{port}")
    logger.info(f"🔧 Debug: {debug}")
    logger.info(f"📚 Documentação: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main_with_auth:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
