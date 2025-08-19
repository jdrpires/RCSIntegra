"""
Sistema de mapeamento automático para diferentes formatos de cliente
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import re

class ClientRequestMapper:
    """Mapeia diferentes formatos de requisição do cliente para o formato RCS padrão"""
    
    def __init__(self):
        # Configurações de mapeamento por cliente
        self.client_mappings = {
            "default": {
                "account_id": "2992",  # Conta padrão - PRECISA SER ATUALIZADA COM CONTA REAL
                "default_campaign": "API_Gateway"
            }
        }
        
        # TODO: Solicitar conta real da Eugen
        # Entre em contato com apoio.ca@eugen.com.br para obter o ID correto
    
    def detect_format(self, data: Dict[str, Any]) -> str:
        """Detecta o formato da requisição do cliente"""
        
        # Formato RCS padrão (já suportado)
        if all(key in data for key in ["account", "messages", "content"]):
            return "rcs_standard"
        
        # Formato simples (phone + message)
        if "phone" in data and "message" in data:
            return "simple"
        
        # Formato WhatsApp-like
        if "number" in data and "text" in data:
            return "whatsapp_like"
        
        # Formato com template
        if "to" in data and ("template" in data or "message" in data):
            return "template_based"
        
        # Formato Telegram-like
        if "chat_id" in data and "text" in data:
            return "telegram_like"
        
        # Formato com destinatário único
        if any(key in data for key in ["recipient", "destination", "target"]):
            return "single_recipient"
        
        return "unknown"
    
    def normalize_phone(self, phone: str) -> str:
        """Normaliza número de telefone para formato brasileiro"""
        # Remove caracteres não numéricos
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        
        # Adiciona código do país se necessário
        if len(clean_phone) == 11 and clean_phone.startswith('0'):
            return '55' + clean_phone[1:]
        elif len(clean_phone) == 10:
            return '55' + clean_phone
        elif len(clean_phone) == 11 and not clean_phone.startswith('55'):
            return '55' + clean_phone
        elif len(clean_phone) == 13 and clean_phone.startswith('55'):
            return clean_phone
        
        return clean_phone
    
    def map_to_rcs_format(self, data: Dict[str, Any], client_id: str = "default") -> Dict[str, Any]:
        """Mapeia qualquer formato para o formato RCS padrão"""
        
        format_type = self.detect_format(data)
        client_config = self.client_mappings.get(client_id, self.client_mappings["default"])
        
        # Se já está no formato RCS padrão, apenas ajusta a conta
        if format_type == "rcs_standard":
            if data.get("account") in ["test", "test_account", "cliente_account"]:
                data["account"] = client_config["account_id"]
            return data
        
        # Mapeamento para formato simples
        if format_type == "simple":
            return {
                "campaign_name": data.get("campaign", client_config["default_campaign"]),
                "account": client_config["account_id"],
                "messages": [
                    {
                        "number": self.normalize_phone(data["phone"]),
                        "vars": data.get("variables", data.get("vars", {}))
                    }
                ],
                "content": {
                    "text": {
                        "message": data["message"]
                    }
                },
                "callback": data.get("callback"),
                "fallback": [
                    {
                        "channel": "SMS",
                        "content": self._sanitize_sms(data["message"])
                    }
                ]
            }
        
        # Mapeamento para formato WhatsApp-like
        if format_type == "whatsapp_like":
            return {
                "campaign_name": data.get("campaign", client_config["default_campaign"]),
                "account": client_config["account_id"],
                "messages": [
                    {
                        "number": self.normalize_phone(data["number"]),
                        "vars": data.get("variables", data.get("vars", {}))
                    }
                ],
                "content": {
                    "text": {
                        "message": data["text"]
                    }
                },
                "callback": data.get("callback"),
                "fallback": [
                    {
                        "channel": "SMS",
                        "content": self._sanitize_sms(data["text"])
                    }
                ]
            }
        
        # Mapeamento para formato com template
        if format_type == "template_based":
            message = data.get("message", "Mensagem via template")
            if "template" in data:
                # Se tem template, pode buscar da base ou usar mensagem padrão
                message = f"Template: {data['template']}"
            
            return {
                "campaign_name": data.get("campaign", client_config["default_campaign"]),
                "account": client_config["account_id"],
                "messages": [
                    {
                        "number": self.normalize_phone(data["to"]),
                        "vars": data.get("variables", data.get("vars", {}))
                    }
                ],
                "content": {
                    "text": {
                        "message": message
                    }
                },
                "callback": data.get("callback"),
                "fallback": [
                    {
                        "channel": "SMS",
                        "content": self._sanitize_sms(message)
                    }
                ]
            }
        
        # Mapeamento para formato Telegram-like
        if format_type == "telegram_like":
            return {
                "campaign_name": data.get("campaign", client_config["default_campaign"]),
                "account": client_config["account_id"],
                "messages": [
                    {
                        "number": self.normalize_phone(data["chat_id"]),
                        "vars": data.get("variables", data.get("vars", {}))
                    }
                ],
                "content": {
                    "text": {
                        "message": data["text"]
                    }
                },
                "callback": data.get("callback"),
                "fallback": [
                    {
                        "channel": "SMS",
                        "content": self._sanitize_sms(data["text"])
                    }
                ]
            }
        
        # Mapeamento para formato com destinatário único
        if format_type == "single_recipient":
            recipient_field = None
            for field in ["recipient", "destination", "target"]:
                if field in data:
                    recipient_field = field
                    break
            
            message = data.get("message", data.get("text", "Mensagem"))
            
            return {
                "campaign_name": data.get("campaign", client_config["default_campaign"]),
                "account": client_config["account_id"],
                "messages": [
                    {
                        "number": self.normalize_phone(data[recipient_field]),
                        "vars": data.get("variables", data.get("vars", {}))
                    }
                ],
                "content": {
                    "text": {
                        "message": message
                    }
                },
                "callback": data.get("callback"),
                "fallback": [
                    {
                        "channel": "SMS",
                        "content": self._sanitize_sms(message)
                    }
                ]
            }
        
        # Se não conseguiu mapear, retorna erro
        raise ValueError(f"Formato não suportado: {format_type}")
    
    def _sanitize_sms(self, text: str) -> str:
        """Sanitiza texto para SMS (remove acentos, limita caracteres)"""
        import unicodedata
        
        # Remove acentos
        normalized = unicodedata.normalize('NFD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        
        # Limita a 160 caracteres
        return ascii_text[:160]
    
    def add_client_mapping(self, client_id: str, account_id: str, default_campaign: str = "API_Gateway"):
        """Adiciona mapeamento para um cliente específico"""
        self.client_mappings[client_id] = {
            "account_id": account_id,
            "default_campaign": default_campaign
        }

# Instância global do mapper
client_mapper = ClientRequestMapper()

# Schemas flexíveis para diferentes formatos
class FlexibleRequest(BaseModel):
    """Schema flexível que aceita qualquer formato"""
    
    class Config:
        extra = "allow"  # Permite campos extras
    
    def dict(self, **kwargs):
        """Retorna todos os campos, incluindo os extras"""
        return super().dict(**kwargs)

class SimpleMessageRequest(BaseModel):
    """Formato simples: phone + message"""
    phone: str
    message: str
    campaign: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    callback: Optional[str] = None

class WhatsAppLikeRequest(BaseModel):
    """Formato WhatsApp-like: number + text"""
    number: str
    text: str
    type: Optional[str] = "text"
    campaign: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    callback: Optional[str] = None

class TemplateBasedRequest(BaseModel):
    """Formato com template: to + template/message"""
    to: str
    template: Optional[str] = None
    message: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    campaign: Optional[str] = None
    callback: Optional[str] = None
