from sqlalchemy.orm import Session
from models import RCSMessage, RCSTemplate, RCSCallback
from schemas import *
from rcs_client import RCSAPIClient
from typing import Dict, Any, List
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class RCSService:
    def __init__(self, db: Session):
        self.db = db
        self.rcs_client = RCSAPIClient()
    
    def _determine_content_type(self, content: MessageContent) -> str:
        """Determina o tipo de conteúdo da mensagem"""
        if content.text:
            return "text"
        elif content.image:
            return "image"
        elif content.video:
            return "video"
        elif content.pdf:
            return "pdf"
        elif content.suggestion:
            return "suggestion"
        elif content.richCard:
            return "richCard"
        elif content.carousel:
            return "carousel"
        else:
            raise ValueError("Tipo de conteúdo não especificado")
    
    def _prepare_content_data(self, content: MessageContent) -> Dict[str, Any]:
        """Prepara dados do conteúdo para armazenamento"""
        content_dict = content.dict(exclude_none=True)
        return content_dict
    
    async def send_basic_message(self, request: RCSBasicRequest) -> List[MessageResponse]:
        """Processa e envia mensagem RCS Basic"""
        responses = []
        
        for message in request.messages:
            # Valida número de telefone
            phone_number = self.rcs_client.validate_phone_number(message.number)
            
            # Determina tipo de conteúdo
            content_type = self._determine_content_type(request.content)
            
            # Cria registro no banco
            db_message = RCSMessage(
                campaign_name=request.campaign_name,
                account=request.account,
                phone_number=phone_number,
                content_type=content_type,
                content_data=self._prepare_content_data(request.content),
                variables=message.vars,
                callback_url=request.callback,
                fallback_enabled=bool(request.fallback),
                fallback_channel=request.fallback[0].channel if request.fallback else None,
                fallback_content=request.fallback[0].content if request.fallback else None,
                status="pending"
            )
            
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            
            try:
                # Prepara dados para API
                api_data = {
                    "account": request.account,
                    "messages": [{"number": phone_number, "vars": message.vars}],
                    "content": request.content.dict(exclude_none=True)
                }
                
                # Adiciona campos opcionais apenas se fornecidos
                if request.campaign_name:
                    api_data["campaign_name"] = request.campaign_name
                if request.callback:
                    api_data["callback"] = request.callback
                if request.fallback:
                    api_data["fallback"] = [fb.dict() for fb in request.fallback]
                
                # Remove campos None
                # api_data = {k: v for k, v in api_data.items() if v is not None}
                
                # Envia para API
                api_response = await self.rcs_client.send_basic_message(api_data)
                
                # Atualiza status
                db_message.status = "sent"
                db_message.api_response = api_response
                db_message.sent_at = datetime.utcnow()
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="sent",
                    message="Mensagem enviada com sucesso",
                    created_at=db_message.created_at
                ))
                
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem {db_message.id}: {str(e)}")
                db_message.status = "failed"
                db_message.error_message = str(e)
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="failed",
                    message=f"Erro ao enviar mensagem: {str(e)}",
                    created_at=db_message.created_at
                ))
            
            self.db.commit()
        
        return responses
    
    async def send_single_message(self, request: RCSSingleRequest) -> List[MessageResponse]:
        """Processa e envia mensagem RCS Single"""
        responses = []
        
        for message in request.messages:
            phone_number = self.rcs_client.validate_phone_number(message.number)
            
            # Se usar template_id, define content_type como "template"
            if request.template_id:
                content_type = "template"
                content_data = {"template_id": request.template_id}
            elif request.content:
                content_type = self._determine_content_type(request.content)
                content_data = self._prepare_content_data(request.content)
            else:
                raise ValueError("É necessário fornecer 'content' ou 'template_id'")
            
            db_message = RCSMessage(
                campaign_name=request.campaign_name,
                account=request.account,
                phone_number=phone_number,
                template_id=request.template_id,
                content_type=content_type,
                content_data=content_data,
                variables=message.vars,
                callback_url=request.callback,
                fallback_enabled=bool(request.fallback),
                fallback_channel=request.fallback[0].channel if request.fallback else None,
                fallback_content=request.fallback[0].content if request.fallback else None,
                status="pending"
            )
            
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            
            try:
                api_data = {
                    "account": request.account,
                    "messages": [{"number": phone_number, "vars": message.vars}]
                }
                
                # Adiciona campos opcionais
                if request.campaign_name:
                    api_data["campaign_name"] = request.campaign_name
                if request.template_id:
                    api_data["template_id"] = request.template_id
                if request.content:
                    api_data["content"] = request.content.dict(exclude_none=True)
                if request.callback:
                    api_data["callback"] = request.callback
                if request.fallback:
                    api_data["fallback"] = [fb.dict() for fb in request.fallback]
                
                # api_data = {k: v for k, v in api_data.items() if v is not None}
                
                api_response = await self.rcs_client.send_single_message(api_data)
                
                db_message.status = "sent"
                db_message.api_response = api_response
                db_message.sent_at = datetime.utcnow()
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="sent",
                    message="Mensagem enviada com sucesso",
                    created_at=db_message.created_at
                ))
                
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem {db_message.id}: {str(e)}")
                db_message.status = "failed"
                db_message.error_message = str(e)
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="failed",
                    message=f"Erro ao enviar mensagem: {str(e)}",
                    created_at=db_message.created_at
                ))
            
            self.db.commit()
        
        return responses
    
    async def send_webhook_message(self, request: RCSWebhookRequest) -> List[MessageResponse]:
        """Processa e envia mensagem RCS Conversacional (webhook)"""
        responses = []
        
        for message in request.messages:
            phone_number = self.rcs_client.validate_phone_number(message.number)
            
            # Define content_type baseado no que foi fornecido
            if request.template_id:
                content_type = "template"
                content_data = {"template_id": request.template_id}
            elif request.content:
                content_type = self._determine_content_type(request.content)
                content_data = self._prepare_content_data(request.content)
            else:
                raise ValueError("É necessário fornecer 'content' ou 'template_id'")
            
            db_message = RCSMessage(
                campaign_name=request.campaign_name,
                account=request.account,
                phone_number=phone_number,
                template_id=request.template_id,
                webhook=request.webhook,
                content_type=content_type,
                content_data=content_data,
                variables=message.vars,
                callback_url=request.callback,
                fallback_enabled=bool(request.fallback),
                fallback_channel=request.fallback[0].channel if request.fallback else None,
                fallback_content=request.fallback[0].content if request.fallback else None,
                status="pending"
            )
            
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            
            try:
                api_data = {
                    "account": request.account,
                    "webhook": request.webhook,
                    "messages": [{"number": phone_number, "vars": message.vars}]
                }
                
                # Adiciona campos opcionais
                if request.campaign_name:
                    api_data["campaign_name"] = request.campaign_name
                if request.template_id:
                    api_data["template_id"] = request.template_id
                if request.content:
                    api_data["content"] = request.content.dict(exclude_none=True)
                if request.callback:
                    api_data["callback"] = request.callback
                if request.fallback:
                    api_data["fallback"] = [fb.dict() for fb in request.fallback]
                
                # api_data = {k: v for k, v in api_data.items() if v is not None}
                
                api_response = await self.rcs_client.send_webhook_message(api_data)
                
                db_message.status = "sent"
                db_message.api_response = api_response
                db_message.sent_at = datetime.utcnow()
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="sent",
                    message="Mensagem enviada com sucesso",
                    created_at=db_message.created_at
                ))
                
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem {db_message.id}: {str(e)}")
                db_message.status = "failed"
                db_message.error_message = str(e)
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="failed",
                    message=f"Erro ao enviar mensagem: {str(e)}",
                    created_at=db_message.created_at
                ))
            
            self.db.commit()
        
        return responses
    
    async def send_template_message(self, request: RCSTemplateRequest) -> List[MessageResponse]:
        """Processa e envia mensagem RCS Conversacional (template)"""
        responses = []
        
        for message in request.messages:
            phone_number = self.rcs_client.validate_phone_number(message.number)
            
            # Define content_type baseado no que foi fornecido
            if request.template_id:
                content_type = "template"
                content_data = {"template_id": request.template_id, "bot_id": request.bot_id}
            elif request.content:
                content_type = self._determine_content_type(request.content)
                content_data = self._prepare_content_data(request.content)
            else:
                raise ValueError("É necessário fornecer 'content' ou 'template_id'")
            
            db_message = RCSMessage(
                campaign_name=request.campaign_name,
                account=request.account,
                phone_number=phone_number,
                template_id=request.template_id,
                webhook=request.webhook,
                bot_id=request.bot_id,
                content_type=content_type,
                content_data=content_data,
                variables=message.vars,
                callback_url=request.callback,
                fallback_enabled=bool(request.fallback),
                fallback_channel=request.fallback[0].channel if request.fallback else None,
                fallback_content=request.fallback[0].content if request.fallback else None,
                status="pending"
            )
            
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            
            try:
                api_data = {
                    "account": request.account,
                    "webhook": request.webhook,
                    "messages": [{"number": phone_number, "vars": message.vars}],
                    "template_id": request.template_id,
                    "bot_id": request.bot_id
                }
                
                # Adiciona campos opcionais
                if request.campaign_name:
                    api_data["campaign_name"] = request.campaign_name
                if request.content:
                    api_data["content"] = request.content.dict(exclude_none=True)
                if request.callback:
                    api_data["callback"] = request.callback
                if request.fallback:
                    api_data["fallback"] = [fb.dict() for fb in request.fallback]
                
                # api_data = {k: v for k, v in api_data.items() if v is not None}
                
                api_response = await self.rcs_client.send_template_message(api_data)
                
                db_message.status = "sent"
                db_message.api_response = api_response
                db_message.sent_at = datetime.utcnow()
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="sent",
                    message="Mensagem enviada com sucesso",
                    created_at=db_message.created_at
                ))
                
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem {db_message.id}: {str(e)}")
                db_message.status = "failed"
                db_message.error_message = str(e)
                
                responses.append(MessageResponse(
                    id=db_message.id,
                    status="failed",
                    message=f"Erro ao enviar mensagem: {str(e)}",
                    created_at=db_message.created_at
                ))
            
            self.db.commit()
        
        return responses
    
    async def create_template(self, request: CreateTemplateRequest) -> Dict[str, Any]:
        """Cria template RCS"""
        try:
            api_response = await self.rcs_client.create_template(request.dict())
            
            # Salva template no banco
            db_template = RCSTemplate(
                template_id=api_response.get("template_id", ""),
                name=request.name,
                content_type=request.content_type,
                template_data=request.template_data,
                account=request.account
            )
            
            self.db.add(db_template)
            self.db.commit()
            
            return api_response
            
        except Exception as e:
            logger.error(f"Erro ao criar template: {str(e)}")
            raise e
    
    def save_callback(self, callback_data: CallbackData) -> None:
        """Salva dados de callback e atualiza status da mensagem"""
        
        # Salva o callback
        db_callback = RCSCallback(
            message_id=callback_data.message_id,
            phone_number=callback_data.phone_number,
            event_type=callback_data.event_type,
            event_status=callback_data.event_status,
            callback_data=callback_data.raw_data,
            interaction_type=callback_data.interaction_type,
            interaction_value=callback_data.interaction_value,
            event_timestamp=callback_data.event_timestamp,
            user_agent=callback_data.user_agent,
            device_info=callback_data.device_info
        )
        
        self.db.add(db_callback)
        
        # Atualiza a mensagem correspondente
        if callback_data.message_id:
            message = self.db.query(RCSMessage).filter(
                RCSMessage.id == callback_data.message_id
            ).first()
        else:
            # Tenta encontrar por número de telefone e timestamp recente
            message = self.db.query(RCSMessage).filter(
                RCSMessage.phone_number == callback_data.phone_number
            ).order_by(RCSMessage.created_at.desc()).first()
        
        if message:
            self._update_message_from_callback(message, callback_data)
        
        self.db.commit()
    
    def _update_message_from_callback(self, message: RCSMessage, callback: CallbackData):
        """Atualiza status da mensagem baseado no callback"""
        now = datetime.utcnow()
        
        # Atualiza status principal
        if callback.event_type == "delivered":
            message.status = "delivered"
            message.delivered_at = callback.event_timestamp or now
            
        elif callback.event_type == "read":
            message.status = "read"
            message.read_at = callback.event_timestamp or now
            
        elif callback.event_type == "opened":
            message.opened_at = callback.event_timestamp or now
            
        elif callback.event_type == "clicked":
            message.click_count += 1
            message.last_interaction_at = callback.event_timestamp or now
            
        elif callback.event_type == "replied":
            message.reply_count += 1
            message.last_interaction_at = callback.event_timestamp or now
            
        elif callback.event_type == "failed":
            message.status = "failed"
            message.error_message = callback.raw_data.get("error_message", "Falha na entrega")
        
        message.updated_at = now
    
    def get_message_stats(self, message_id: int) -> Optional[MessageStats]:
        """Retorna estatísticas detalhadas de uma mensagem"""
        message = self.db.query(RCSMessage).filter(RCSMessage.id == message_id).first()
        
        if not message:
            return None
        
        return MessageStats(
            id=message.id,
            phone_number=message.phone_number,
            status=message.status,
            created_at=message.created_at,
            sent_at=message.sent_at,
            delivered_at=message.delivered_at,
            read_at=message.read_at,
            opened_at=message.opened_at,
            last_interaction_at=message.last_interaction_at,
            click_count=message.click_count,
            reply_count=message.reply_count
        )
    
    def get_campaign_summary(self, campaign_name: str = None, account: str = None) -> EventSummary:
        """Retorna resumo de eventos para uma campanha ou conta"""
        query = self.db.query(RCSMessage)
        
        if campaign_name:
            query = query.filter(RCSMessage.campaign_name == campaign_name)
        if account:
            query = query.filter(RCSMessage.account == account)
        
        messages = query.all()
        
        total_sent = len([m for m in messages if m.status != "pending"])
        total_delivered = len([m for m in messages if m.delivered_at is not None])
        total_read = len([m for m in messages if m.read_at is not None])
        total_opened = len([m for m in messages if m.opened_at is not None])
        total_clicked = sum(m.click_count for m in messages)
        total_replied = sum(m.reply_count for m in messages)
        
        # Calcula taxas
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
        read_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0
        engagement_rate = ((total_clicked + total_replied) / total_delivered * 100) if total_delivered > 0 else 0
        
        return EventSummary(
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_read=total_read,
            total_opened=total_opened,
            total_clicked=total_clicked,
            total_replied=total_replied,
            delivery_rate=round(delivery_rate, 2),
            read_rate=round(read_rate, 2),
            engagement_rate=round(engagement_rate, 2)
        )
