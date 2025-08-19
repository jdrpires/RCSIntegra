"""
Serviço principal para clientes enviarem mensagens RCS
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from auth_service import AuthService
from auth_models import Client, User, ClientTemplate
from auth_schemas import (
    ClientSendMessageRequest, 
    ClientSendMessageResponse,
    ClientMessageQuery,
    ClientMessageResponse
)
from services import RCSService
from models import RCSMessage, RCSTemplate
from schemas import RCSBasicRequest, RCSSingleRequest


class ClientRCSService:
    """Serviço para clientes enviarem mensagens RCS"""
    
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(db)
        self.rcs_service = RCSService(db)
    
    async def send_message(self, request: ClientSendMessageRequest) -> ClientSendMessageResponse:
        """
        Serviço principal para envio de mensagens pelos clientes
        """
        try:
            # 1. Validar cliente
            client = self.auth_service.get_client_by_code(request.client_code)
            if not client:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
            
            # 2. Validar tipo de mensagem permitido
            if request.message_type not in client.allowed_message_types:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Tipo de mensagem '{request.message_type}' não permitido para este cliente"
                )
            
            # 3. Validar usuário (se fornecido)
            user = None
            if request.user_code:
                user = self.db.query(User).filter(
                    User.username == request.user_code,
                    User.client_id == client.id,
                    User.is_active == True
                ).first()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Usuário não encontrado"
                    )
            
            # 4. Preparar conteúdo da mensagem
            content = self._prepare_message_content(
                client=client,
                message_type=request.message_type,
                template_id=request.template_id,
                custom_content=request.content,
                variables=request.variables
            )
            
            # 5. Gerar ID único para o cliente
            client_message_id = f"{client.client_code}_{uuid.uuid4().hex[:8]}"
            
            # 6. Preparar dados para envio
            if request.message_type == "basic":
                rcs_request = self._prepare_basic_request(
                    client=client,
                    phone_numbers=request.phone_numbers,
                    content=content,
                    variables=request.variables,
                    callback_url=request.callback_url or client.callback_url,
                    campaign_name=request.campaign_name or f"Campaign_{client_message_id}"
                )
                
                # Enviar via RCS Basic
                response = await self.rcs_service.send_basic_message(rcs_request)
                
            elif request.message_type == "single":
                rcs_request = self._prepare_single_request(
                    client=client,
                    phone_numbers=request.phone_numbers,
                    content=content,
                    variables=request.variables,
                    callback_url=request.callback_url or client.callback_url
                )
                
                # Enviar via RCS Single
                response = await self.rcs_service.send_single_message(rcs_request)
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de mensagem '{request.message_type}' não suportado"
                )
            
            # 7. Atualizar mensagens com referência ao cliente
            self._update_messages_with_client_info(
                response=response,
                client=client,
                client_message_id=client_message_id
            )
            
            # 8. Registrar log
            success = len([r for r in response if r.status == "sent"]) > 0
            first_message_id = response[0].id if response and len(response) > 0 else None
            
            self.auth_service.log_message_request(
                client_id=client.id,
                user_id=user.id if user else None,
                rcs_message_id=str(first_message_id) if first_message_id else "",
                endpoint_used=f"/api/client/send-{request.message_type}",
                request_data=request.dict(),
                success=success,
                error_message=None if success else "Falha no envio"
            )
            
            # 9. Preparar resposta
            sent_count = len([r for r in response if r.status == "sent"])
            failed_count = len([r for r in response if r.status == "failed"])
            
            return ClientSendMessageResponse(
                success=success,
                message_id=str(first_message_id) if first_message_id else "",
                client_message_id=client_message_id,
                status="sent" if success else "failed",
                message="Mensagem enviada com sucesso" if success else "Falha no envio",
                sent_count=sent_count,
                failed_count=failed_count,
                details={"responses": [r.dict() for r in response]}
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}"
            )
    
    def _prepare_message_content(self, client: Client, message_type: str, 
                               template_id: Optional[str], custom_content: Optional[Dict],
                               variables: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara o conteúdo da mensagem"""
        
        # Se foi fornecido um template_id, buscar template da plataforma
        if template_id:
            platform_template = self.db.query(RCSTemplate).filter(
                RCSTemplate.template_id == template_id,
                RCSTemplate.account == client.rcs_account
            ).first()
            
            if not platform_template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template não encontrado"
                )
            
            # Usar dados do template da plataforma
            content = platform_template.template_data.copy()
            
            # Substituir variáveis se fornecidas
            if variables:
                content = self._replace_variables(content, variables)
            
            return content
        
        # Se foi fornecido conteúdo customizado
        elif custom_content:
            # Substituir variáveis se fornecidas
            if variables:
                return self._replace_variables(custom_content, variables)
            return custom_content
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário fornecer template_id ou content"
            )
    
    def _replace_variables(self, content: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Substitui variáveis no conteúdo"""
        import json
        
        # Converter para string, substituir variáveis e converter de volta
        content_str = json.dumps(content)
        
        for key, value in variables.items():
            content_str = content_str.replace(f"{{{{{key}}}}}", str(value))
        
        return json.loads(content_str)
    
    def _prepare_basic_request(self, client: Client, phone_numbers: List[str],
                             content: Dict[str, Any], variables: Dict[str, Any],
                             callback_url: Optional[str], campaign_name: str) -> RCSBasicRequest:
        """Prepara requisição RCS Basic"""
        
        messages = []
        for phone in phone_numbers:
            messages.append({
                "number": phone,
                "vars": variables
            })
        
        return RCSBasicRequest(
            campaign_name=campaign_name,
            account=client.rcs_account,
            messages=messages,
            content=content,
            callback=callback_url,
            fallback=[{
                "channel": "SMS",
                "content": self._prepare_sms_fallback(content)
            }] if content else None
        )
    
    def _prepare_single_request(self, client: Client, phone_numbers: List[str],
                              content: Dict[str, Any], variables: Dict[str, Any],
                              callback_url: Optional[str]) -> RCSSingleRequest:
        """Prepara requisição RCS Single"""
        
        messages = []
        for phone in phone_numbers:
            messages.append({
                "number": phone,
                "vars": variables
            })
        
        return RCSSingleRequest(
            account=client.rcs_account,
            messages=messages,
            content=content,
            callback=callback_url
        )
    
    def _prepare_sms_fallback(self, content: Dict[str, Any]) -> str:
        """Prepara conteúdo de fallback SMS"""
        # Extrair texto do conteúdo RCS para SMS
        if "text" in content and "message" in content["text"]:
            return content["text"]["message"][:160]  # Limite SMS
        elif "richCard" in content:
            rich_card = content["richCard"]
            text = rich_card.get("title", "") + " " + rich_card.get("description", "")
            return text[:160]
        else:
            return "Mensagem RCS"
    
    def _update_messages_with_client_info(self, response: List, 
                                        client: Client, client_message_id: str):
        """Atualiza mensagens com informações do cliente"""
        
        # Atualizar mensagens com client_id
        for msg_response in response:
            if hasattr(msg_response, 'id') and msg_response.id:
                message = self.db.query(RCSMessage).filter(
                    RCSMessage.id == msg_response.id
                ).first()
                
                if message:
                    message.client_id = client.id
                    message.client_message_id = client_message_id
                    self.db.commit()
    
    def get_client_messages(self, query: ClientMessageQuery) -> List[ClientMessageResponse]:
        """Busca mensagens do cliente"""
        
        # Validar cliente
        client = self.auth_service.get_client_by_code(query.client_code)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Construir query
        db_query = self.db.query(RCSMessage).filter(RCSMessage.client_id == client.id)
        
        # Filtros opcionais
        if query.start_date:
            db_query = db_query.filter(RCSMessage.created_at >= query.start_date)
        
        if query.end_date:
            db_query = db_query.filter(RCSMessage.created_at <= query.end_date)
        
        if query.status:
            db_query = db_query.filter(RCSMessage.status == query.status)
        
        if query.phone_number:
            db_query = db_query.filter(RCSMessage.phone_number == query.phone_number)
        
        # Paginação
        messages = db_query.offset(query.offset).limit(query.limit).all()
        
        # Converter para resposta
        result = []
        for msg in messages:
            result.append(ClientMessageResponse(
                id=str(msg.id),
                client_message_id=msg.client_message_id or "",
                phone_number=msg.phone_number,
                status=msg.status,
                message_type=msg.content_type,
                campaign_name=msg.campaign_name,
                sent_at=msg.sent_at,
                delivered_at=msg.delivered_at,
                read_at=msg.read_at,
                error_message=msg.error_message,
                created_at=msg.created_at
            ))
        
        return result
