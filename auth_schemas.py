"""
Schemas Pydantic para autenticação e multi-tenancy
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Schemas para Cliente
class ClientBase(BaseModel):
    name: str
    email: EmailStr
    rcs_account: str
    api_token: Optional[str] = None
    allowed_message_types: List[str] = ["basic", "single"]
    max_messages_per_day: str = "1000"
    callback_url: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    rcs_account: Optional[str] = None
    api_token: Optional[str] = None
    allowed_message_types: Optional[List[str]] = None
    max_messages_per_day: Optional[str] = None
    callback_url: Optional[str] = None
    is_active: Optional[bool] = None


class Client(ClientBase):
    id: str
    client_code: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schemas para Usuário
class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    permissions: Dict[str, bool] = {
        "can_send_basic": True,
        "can_send_single": True,
        "can_use_templates": True,
        "can_view_reports": True
    }


class UserCreate(UserBase):
    password: str
    client_id: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: str
    client_id: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schemas para API Key
class APIKeyBase(BaseModel):
    key_name: str
    scopes: List[str] = ["send_messages", "view_messages"]
    requests_per_minute: str = "60"
    requests_per_day: str = "1000"
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    client_id: str


class APIKey(APIKeyBase):
    id: str
    client_id: str
    api_key: str
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas para Template do Cliente
class ClientTemplateBase(BaseModel):
    template_name: str
    template_type: str
    template_data: Dict[str, Any]
    variables: List[str] = []


class ClientTemplateCreate(ClientTemplateBase):
    client_id: str


class ClientTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    template_type: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ClientTemplate(ClientTemplateBase):
    id: str
    client_id: str
    is_active: bool
    usage_count: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schemas para autenticação
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    client_code: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    client_id: Optional[str] = None
    client_code: Optional[str] = None
    scopes: List[str] = []


class LoginRequest(BaseModel):
    username: str
    password: str


# Schemas para o novo serviço de envio
class ClientSendMessageRequest(BaseModel):
    client_code: str
    user_code: Optional[str] = None  # Código do usuário (opcional)
    message_type: str  # "basic" ou "single"
    template_id: Optional[str] = None  # ID do template da plataforma (opcional)
    
    # Dados da mensagem
    phone_numbers: List[str]
    variables: Optional[Dict[str, Any]] = {}
    
    # Conteúdo personalizado (se não usar template)
    content: Optional[Dict[str, Any]] = None
    
    # Configurações
    callback_url: Optional[str] = None
    campaign_name: Optional[str] = None


class ClientSendMessageResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    client_message_id: str  # ID único para o cliente
    status: str
    message: str
    sent_count: int
    failed_count: int
    details: Optional[Dict[str, Any]] = None


# Schema para consulta de mensagens do cliente
class ClientMessageQuery(BaseModel):
    client_code: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    phone_number: Optional[str] = None
    limit: int = 100
    offset: int = 0


class ClientMessageResponse(BaseModel):
    id: str
    client_message_id: str
    phone_number: str
    status: str
    message_type: str
    campaign_name: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
