from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, create_tables
from schemas import *
from services import RCSService
import logging
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar rotas de autenticação
try:
    from auth_routes import router as auth_router
    from client_routes import router as client_router
    AUTH_ENABLED = True
except ImportError as e:
    logger.warning(f"Rotas de autenticação não encontradas: {e}")
    AUTH_ENABLED = False

# Cria tabelas do banco
create_tables()

# Inicializa FastAPI
app = FastAPI(
    title="RCS Gateway API with Authentication",
    description="Gateway para integração com API RCS da Eugen com sistema de autenticação",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas de autenticação se disponíveis
if AUTH_ENABLED:
    app.include_router(auth_router, prefix="/api", tags=["auth"])
    app.include_router(client_router, prefix="/api", tags=["client"])
    logger.info("Sistema de autenticação ativado")
else:
    logger.warning("Sistema de autenticação desativado - rotas não encontradas")

@app.get("/")
async def root():
    """Endpoint de health check"""
    return {
        "message": "RCS Gateway API está funcionando",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check detalhado"""
    return {
        "status": "healthy",
        "database": "connected",
        "api": "ready"
    }

# Endpoints RCS Basic
@app.post("/api/rcs/basic", response_model=List[MessageResponse])
async def send_basic_message(
    request: RCSBasicRequest,
    db: Session = Depends(get_db)
):
    """
    Envia mensagem RCS Basic
    
    - **campaign_name**: Nome da campanha (opcional)
    - **account**: ID da conta
    - **messages**: Lista de destinatários com números e variáveis
    - **content**: Conteúdo da mensagem (text, image, video, pdf, suggestion, richCard, carousel)
    - **callback**: URL para receber status de entrega (opcional)
    - **fallback**: Configuração de fallback SMS (opcional)
    """
    try:
        service = RCSService(db)
        responses = await service.send_basic_message(request)
        return responses
    except Exception as e:
        logger.error(f"Erro ao processar mensagem basic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint flexível que aceita qualquer formato
@app.post("/api/send", response_model=List[MessageResponse])
async def send_flexible_message(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint flexível que aceita diferentes formatos de requisição
    
    Formatos suportados:
    - Simples: {"phone": "11999999999", "message": "Texto"}
    - WhatsApp-like: {"number": "11999999999", "text": "Texto"}
    - Template: {"to": "11999999999", "template": "welcome", "variables": {...}}
    - RCS padrão: formato completo
    """
    try:
        # Importar o mapper
        from client_mapper import client_mapper
        
        # Obter dados da requisição
        request_data = await request.json()
        logger.info(f"Requisição flexível recebida: {request_data}")
        
        # Mapear para formato RCS padrão
        mapped_data = client_mapper.map_to_rcs_format(request_data)
        logger.info(f"Dados mapeados: {mapped_data}")
        
        # Converter para RCSBasicRequest
        rcs_request = RCSBasicRequest(**mapped_data)
        
        # Processar mensagem
        service = RCSService(db)
        responses = await service.send_basic_message(rcs_request)
        return responses
        
    except ValueError as e:
        logger.error(f"Erro de mapeamento: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Formato não suportado: {str(e)}")
    except Exception as e:
        logger.error(f"Erro ao processar mensagem flexível: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint específico para formato simples
@app.post("/api/send/simple")
async def send_simple_message(
    phone: str,
    message: str,
    campaign: str = "API_Simple",
    variables: dict = None,
    db: Session = Depends(get_db)
):
    """
    Endpoint super simples: apenas phone e message
    
    Exemplo: POST /api/send/simple?phone=11999999999&message=Olá
    """
    try:
        from client_mapper import client_mapper
        
        request_data = {
            "phone": phone,
            "message": message,
            "campaign": campaign,
            "variables": variables or {}
        }
        
        # Mapear para formato RCS
        mapped_data = client_mapper.map_to_rcs_format(request_data)
        rcs_request = RCSBasicRequest(**mapped_data)
        
        # Processar mensagem
        service = RCSService(db)
        responses = await service.send_basic_message(rcs_request)
        return responses
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem simples: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints RCS Single
@app.post("/api/rcs/single", response_model=List[MessageResponse])
async def send_single_message(
    request: RCSSingleRequest,
    db: Session = Depends(get_db)
):
    """
    Envia mensagem RCS Single
    
    Permite usar template_id ou content personalizado.
    """
    try:
        service = RCSService(db)
        responses = await service.send_single_message(request)
        return responses
    except Exception as e:
        logger.error(f"Erro ao processar mensagem single: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints RCS Conversacional (webhook)
@app.post("/api/rcs/webhook", response_model=List[MessageResponse])
async def send_webhook_message(
    request: RCSWebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Envia mensagem RCS Conversacional com webhook
    
    Requer webhook URL para receber respostas dos usuários.
    """
    try:
        service = RCSService(db)
        responses = await service.send_webhook_message(request)
        return responses
    except Exception as e:
        logger.error(f"Erro ao processar mensagem webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints RCS Conversacional (template)
@app.post("/api/rcs/template", response_model=List[MessageResponse])
async def send_template_message(
    request: RCSTemplateRequest,
    db: Session = Depends(get_db)
):
    """
    Envia mensagem RCS Conversacional com template
    
    Requer template_id e bot_id configurados na plataforma.
    """
    try:
        service = RCSService(db)
        responses = await service.send_template_message(request)
        return responses
    except Exception as e:
        logger.error(f"Erro ao processar mensagem template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para criar templates
@app.post("/api/rcs/templates")
async def create_template(
    request: CreateTemplateRequest,
    db: Session = Depends(get_db)
):
    """
    Cria template RCS na plataforma
    
    O template criado ficará disponível para uso posterior.
    """
    try:
        service = RCSService(db)
        response = await service.create_template(request)
        return response
    except Exception as e:
        logger.error(f"Erro ao criar template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para receber callbacks
@app.post("/api/rcs/callback")
async def receive_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Recebe callbacks da API RCS
    
    Este endpoint processa todos os tipos de eventos:
    - delivered: Mensagem entregue
    - read: Mensagem lida/visualizada
    - opened: Mensagem aberta
    - clicked: Botão clicado
    - replied: Usuário respondeu
    - failed: Falha na entrega
    """
    try:
        callback_data = await request.json()
        logger.info(f"Callback recebido: {callback_data}")
        
        # Processa diferentes formatos de callback
        event_type = callback_data.get("event", callback_data.get("type", "unknown"))
        phone_number = callback_data.get("phone", callback_data.get("number", callback_data.get("phone_number", "")))
        
        # Tenta extrair message_id se disponível
        message_id = callback_data.get("message_id", callback_data.get("id"))
        
        # Dados de interação (para clicks, replies)
        interaction_type = None
        interaction_value = None
        
        if event_type == "clicked" or "button" in callback_data:
            interaction_type = "button_click"
            interaction_value = callback_data.get("button_value", callback_data.get("value"))
        elif event_type == "replied" or "reply" in callback_data:
            interaction_type = "reply"
            interaction_value = callback_data.get("reply_text", callback_data.get("message"))
        
        # Timestamp do evento
        event_timestamp = None
        if callback_data.get("timestamp"):
            try:
                from datetime import datetime
                event_timestamp = datetime.fromisoformat(callback_data["timestamp"].replace("Z", "+00:00"))
            except:
                pass
        
        # Cria objeto de callback
        callback_obj = CallbackData(
            message_id=message_id,
            phone_number=phone_number,
            event_type=event_type,
            event_status=callback_data.get("status", "success"),
            interaction_type=interaction_type,
            interaction_value=interaction_value,
            event_timestamp=event_timestamp,
            user_agent=callback_data.get("user_agent"),
            device_info=callback_data.get("device_info"),
            raw_data=callback_data
        )
        
        # Processa callback
        service = RCSService(db)
        service.save_callback(callback_obj)
        
        logger.info(f"Callback processado: {event_type} para {phone_number}")
        
        return {
            "status": "callback_processed",
            "event_type": event_type,
            "phone_number": phone_number,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de consulta
@app.get("/api/messages/{message_id}")
async def get_message(message_id: int, db: Session = Depends(get_db)):
    """Consulta status detalhado de uma mensagem específica"""
    from models import RCSMessage
    
    message = db.query(RCSMessage).filter(RCSMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    return {
        "id": message.id,
        "status": message.status,
        "phone_number": message.phone_number,
        "campaign_name": message.campaign_name,
        "created_at": message.created_at,
        "sent_at": message.sent_at,
        "delivered_at": message.delivered_at,
        "read_at": message.read_at,
        "opened_at": message.opened_at,
        "last_interaction_at": message.last_interaction_at,
        "click_count": message.click_count,
        "reply_count": message.reply_count,
        "error_message": message.error_message
    }

@app.get("/api/messages/{message_id}/stats", response_model=MessageStats)
async def get_message_stats(message_id: int, db: Session = Depends(get_db)):
    """Retorna estatísticas detalhadas de uma mensagem"""
    service = RCSService(db)
    stats = service.get_message_stats(message_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    return stats

@app.get("/api/messages/{message_id}/events")
async def get_message_events(message_id: int, db: Session = Depends(get_db)):
    """Lista todos os eventos de uma mensagem"""
    from models import RCSCallback
    
    events = db.query(RCSCallback).filter(
        RCSCallback.message_id == message_id
    ).order_by(RCSCallback.received_at.desc()).all()
    
    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "event_status": event.event_status,
            "interaction_type": event.interaction_type,
            "interaction_value": event.interaction_value,
            "event_timestamp": event.event_timestamp,
            "received_at": event.received_at,
            "raw_data": event.callback_data
        }
        for event in events
    ]

@app.get("/api/campaigns/{campaign_name}/summary", response_model=EventSummary)
async def get_campaign_summary(campaign_name: str, db: Session = Depends(get_db)):
    """Retorna resumo de eventos para uma campanha"""
    service = RCSService(db)
    return service.get_campaign_summary(campaign_name=campaign_name)

@app.get("/api/accounts/{account}/summary", response_model=EventSummary)
async def get_account_summary(account: str, db: Session = Depends(get_db)):
    """Retorna resumo de eventos para uma conta"""
    service = RCSService(db)
    return service.get_campaign_summary(account=account)

@app.get("/api/events")
async def list_events(
    event_type: str = None,
    phone_number: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista eventos com filtros opcionais"""
    from models import RCSCallback
    
    query = db.query(RCSCallback)
    
    if event_type:
        query = query.filter(RCSCallback.event_type == event_type)
    if phone_number:
        query = query.filter(RCSCallback.phone_number == phone_number)
    
    events = query.order_by(RCSCallback.received_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": event.id,
            "message_id": event.message_id,
            "phone_number": event.phone_number,
            "event_type": event.event_type,
            "interaction_type": event.interaction_type,
            "interaction_value": event.interaction_value,
            "event_timestamp": event.event_timestamp,
            "received_at": event.received_at
        }
        for event in events
    ]

@app.get("/api/messages")
async def list_messages(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Lista mensagens com filtros opcionais"""
    from models import RCSMessage
    
    query = db.query(RCSMessage)
    
    if status:
        query = query.filter(RCSMessage.status == status)
    
    messages = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": msg.id,
            "status": msg.status,
            "phone_number": msg.phone_number,
            "campaign_name": msg.campaign_name,
            "created_at": msg.created_at,
            "sent_at": msg.sent_at
        }
        for msg in messages
    ]

@app.get("/api/platform/templates")
async def get_platform_templates(db: Session = Depends(get_db)):
    """
    Busca templates disponíveis na plataforma Eugen
    
    Retorna lista de templates criados na plataforma.
    """
    try:
        service = RCSService(db)
        templates = await service.rcs_client.get_templates()
        return templates
    except Exception as e:
        logger.error(f"Erro ao buscar templates da plataforma: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/platform/templates/{template_id}")
async def get_platform_template(template_id: str, db: Session = Depends(get_db)):
    """
    Busca um template específico na plataforma Eugen
    
    Retorna detalhes do template incluindo variáveis disponíveis.
    """
    try:
        service = RCSService(db)
        template = await service.rcs_client.get_template_by_id(template_id)
        return template
    except Exception as e:
        logger.error(f"Erro ao buscar template {template_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/templates")
async def list_templates(db: Session = Depends(get_db)):
    """Lista templates criados"""
    from models import RCSTemplate
    
    templates = db.query(RCSTemplate).all()
    
    return [
        {
            "id": tmpl.id,
            "template_id": tmpl.template_id,
            "name": tmpl.name,
            "content_type": tmpl.content_type,
            "account": tmpl.account,
            "created_at": tmpl.created_at
        }
        for tmpl in templates
    ]

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("GATEWAY_HOST", "0.0.0.0")
    port = int(os.getenv("GATEWAY_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
