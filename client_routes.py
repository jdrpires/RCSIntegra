"""
Rotas para o serviço de clientes RCS
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import get_db
from client_service import ClientRCSService
from auth_service import AuthService
from auth_models import Client
from auth_schemas import (
    ClientSendMessageRequest,
    ClientSendMessageResponse,
    ClientMessageQuery,
    ClientMessageResponse
)

router = APIRouter()


def get_client_service(db: Session = Depends(get_db)) -> ClientRCSService:
    """Dependency para obter o serviço de cliente"""
    return ClientRCSService(db)


def authenticate_client_request(
    x_api_key: str = Header(..., description="API Key do cliente"),
    client_service: ClientRCSService = Depends(get_client_service)
) -> Client:
    """Autentica requisição do cliente via API Key"""
    
    auth_service = AuthService(client_service.db)
    api_key = auth_service.authenticate_api_key(x_api_key)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou expirada"
        )
    
    # Verificar se a API Key tem permissão para enviar mensagens
    if "send_messages" not in api_key.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key não tem permissão para enviar mensagens"
        )
    
    # Buscar cliente
    client = client_service.db.query(Client).filter(
        Client.id == api_key.client_id,
        Client.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente não encontrado ou inativo"
        )
    
    return client


@router.post("/client/send-message", response_model=ClientSendMessageResponse)
async def send_message(
    request: ClientSendMessageRequest,
    client: Client = Depends(authenticate_client_request),
    client_service: ClientRCSService = Depends(get_client_service)
):
    """
    Endpoint principal para clientes enviarem mensagens RCS
    
    Este endpoint permite que clientes autenticados enviem mensagens RCS
    especificando o tipo (basic ou single) e opcionalmente um template.
    
    **Parâmetros:**
    - **client_code**: Código do cliente (deve corresponder ao cliente autenticado)
    - **user_code**: Código do usuário (opcional)
    - **message_type**: Tipo da mensagem ("basic" ou "single")
    - **template_id**: ID do template da plataforma (opcional)
    - **phone_numbers**: Lista de números de telefone
    - **variables**: Variáveis para substituição no template
    - **content**: Conteúdo personalizado (se não usar template)
    - **callback_url**: URL de callback (opcional, usa padrão do cliente)
    - **campaign_name**: Nome da campanha (opcional)
    
    **Exemplo de uso:**
    ```json
    {
        "client_code": "CLI_ABC123",
        "user_code": "user001",
        "message_type": "basic",
        "template_id": "template_001",
        "phone_numbers": ["5511999999999"],
        "variables": {
            "nome": "João",
            "produto": "Smartphone"
        },
        "callback_url": "https://meusite.com/callback",
        "campaign_name": "Promocao_Janeiro"
    }
    ```
    """
    
    # Verificar se o client_code corresponde ao cliente autenticado
    if request.client_code != client.client_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client code não corresponde ao cliente autenticado"
        )
    
    return await client_service.send_message(request)


@router.get("/client/messages", response_model=List[ClientMessageResponse])
def get_messages(
    client_code: str,
    start_date: str = None,
    end_date: str = None,
    status: str = None,
    phone_number: str = None,
    limit: int = 100,
    offset: int = 0,
    client: Client = Depends(authenticate_client_request),
    client_service: ClientRCSService = Depends(get_client_service)
):
    """
    Consultar mensagens enviadas pelo cliente
    
    Este endpoint permite que clientes consultem suas mensagens enviadas
    com filtros opcionais por data, status, número de telefone, etc.
    
    **Parâmetros de consulta:**
    - **client_code**: Código do cliente
    - **start_date**: Data inicial (formato: YYYY-MM-DD)
    - **end_date**: Data final (formato: YYYY-MM-DD)
    - **status**: Status da mensagem (pending, sent, delivered, read, failed)
    - **phone_number**: Número de telefone específico
    - **limit**: Limite de resultados (padrão: 100)
    - **offset**: Offset para paginação (padrão: 0)
    
    **Exemplo de resposta:**
    ```json
    [
        {
            "id": "123",
            "client_message_id": "CLI_ABC123_a1b2c3d4",
            "phone_number": "5511999999999",
            "status": "delivered",
            "message_type": "basic",
            "campaign_name": "Promocao_Janeiro",
            "sent_at": "2025-01-15T10:30:00Z",
            "delivered_at": "2025-01-15T10:31:00Z",
            "created_at": "2025-01-15T10:30:00Z"
        }
    ]
    ```
    """
    
    # Verificar se o client_code corresponde ao cliente autenticado
    if client_code != client.client_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client code não corresponde ao cliente autenticado"
        )
    
    # Converter datas se fornecidas
    from datetime import datetime
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de start_date inválido. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_date_obj = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de end_date inválido. Use YYYY-MM-DD"
            )
    
    # Criar query
    query = ClientMessageQuery(
        client_code=client_code,
        start_date=start_date_obj,
        end_date=end_date_obj,
        status=status,
        phone_number=phone_number,
        limit=limit,
        offset=offset
    )
    
    return client_service.get_client_messages(query)


@router.get("/client/messages/{client_message_id}", response_model=ClientMessageResponse)
def get_message_by_id(
    client_message_id: str,
    client: Client = Depends(authenticate_client_request),
    client_service: ClientRCSService = Depends(get_client_service)
):
    """
    Consultar mensagem específica pelo ID do cliente
    
    **Parâmetros:**
    - **client_message_id**: ID único da mensagem gerado para o cliente
    """
    
    from models import RCSMessage
    
    message = client_service.db.query(RCSMessage).filter(
        RCSMessage.client_id == client.id,
        RCSMessage.client_message_id == client_message_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensagem não encontrada"
        )
    
    return ClientMessageResponse(
        id=str(message.id),
        client_message_id=message.client_message_id or "",
        phone_number=message.phone_number,
        status=message.status,
        message_type=message.content_type,
        campaign_name=message.campaign_name,
        sent_at=message.sent_at,
        delivered_at=message.delivered_at,
        read_at=message.read_at,
        error_message=message.error_message,
        created_at=message.created_at
    )


@router.get("/client/stats")
def get_client_stats(
    client: Client = Depends(authenticate_client_request),
    client_service: ClientRCSService = Depends(get_client_service)
):
    """
    Estatísticas do cliente
    
    Retorna estatísticas básicas das mensagens enviadas pelo cliente.
    """
    
    from models import RCSMessage
    from sqlalchemy import func
    
    # Contar mensagens por status
    stats = client_service.db.query(
        RCSMessage.status,
        func.count(RCSMessage.id).label('count')
    ).filter(
        RCSMessage.client_id == client.id
    ).group_by(RCSMessage.status).all()
    
    # Contar total de mensagens
    total_messages = client_service.db.query(RCSMessage).filter(
        RCSMessage.client_id == client.id
    ).count()
    
    # Contar mensagens hoje
    from datetime import datetime, date
    today = date.today()
    messages_today = client_service.db.query(RCSMessage).filter(
        RCSMessage.client_id == client.id,
        func.date(RCSMessage.created_at) == today
    ).count()
    
    return {
        "client_code": client.client_code,
        "client_name": client.name,
        "total_messages": total_messages,
        "messages_today": messages_today,
        "messages_by_status": {stat.status: stat.count for stat in stats},
        "allowed_message_types": client.allowed_message_types,
        "max_messages_per_day": client.max_messages_per_day
    }
