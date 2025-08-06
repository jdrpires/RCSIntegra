from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Suggestion schema
class Suggestion(BaseModel):
    type: str = Field(..., description="Tipo do botão: openUrl, call, reply")
    title: str = Field(..., description="Nome/etiqueta do botão")
    value: str = Field(..., description="Valor do botão (URL, número ou texto)")

# Content schemas
class TextContent(BaseModel):
    message: str = Field(..., max_length=5000)

class ImageContent(BaseModel):
    image: str = Field(..., description="URL HTTPS da imagem")

class VideoContent(BaseModel):
    video: str = Field(..., description="URL HTTPS do vídeo")

class PDFContent(BaseModel):
    pdf: str = Field(..., description="URL HTTPS do PDF")

class SuggestionContent(BaseModel):
    suggestions: List[Suggestion] = Field(..., max_items=4)

class RichCardContent(BaseModel):
    title: str
    description: str = Field(..., max_length=2000)
    fileUrl: str = Field(..., description="URL HTTPS da mídia")
    suggestions: Optional[List[Suggestion]] = Field(None, max_items=4)

class CarouselItem(BaseModel):
    title: str
    description: str = Field(..., max_length=2000)
    fileUrl: str = Field(..., description="URL HTTPS da mídia")
    suggestions: Optional[List[Suggestion]] = Field(None, max_items=4)

class CarouselContent(BaseModel):
    carousel: List[CarouselItem]

# Main content union
class MessageContent(BaseModel):
    text: Optional[TextContent] = None
    image: Optional[ImageContent] = None
    video: Optional[VideoContent] = None
    pdf: Optional[PDFContent] = None
    suggestion: Optional[SuggestionContent] = None
    richCard: Optional[RichCardContent] = None
    carousel: Optional[List[CarouselItem]] = None

# Fallback schema
class Fallback(BaseModel):
    channel: str = Field(default="SMS")
    content: str = Field(..., max_length=160, description="Mensagem SMS sem acentos")

# Message schema
class MessageRecipient(BaseModel):
    number: str = Field(..., description="Número do telefone")
    vars: Optional[Dict[str, str]] = Field(None, description="Variáveis dinâmicas")

# Base request schemas
class RCSBasicRequest(BaseModel):
    campaign_name: Optional[str] = None
    account: str
    messages: List[MessageRecipient]
    content: MessageContent
    callback: Optional[str] = None
    fallback: Optional[List[Fallback]] = None

class RCSSingleRequest(BaseModel):
    campaign_name: Optional[str] = None
    account: str
    messages: List[MessageRecipient]
    template_id: Optional[str] = None
    content: Optional[MessageContent] = None
    callback: Optional[str] = None
    fallback: Optional[List[Fallback]] = None

class RCSWebhookRequest(BaseModel):
    campaign_name: Optional[str] = None
    account: str
    webhook: str
    messages: List[MessageRecipient]
    template_id: Optional[str] = None
    content: Optional[MessageContent] = None
    callback: Optional[str] = None
    fallback: Optional[List[Fallback]] = None

class RCSTemplateRequest(BaseModel):
    campaign_name: Optional[str] = None
    account: str
    webhook: str
    messages: List[MessageRecipient]
    template_id: str
    bot_id: str
    content: Optional[MessageContent] = None
    callback: Optional[str] = None
    fallback: Optional[List[Fallback]] = None

# Template creation schema
class CreateTemplateRequest(BaseModel):
    name: str
    account: str
    content_type: str
    template_data: Dict[str, Any]

# Callback schemas
class CallbackData(BaseModel):
    message_id: Optional[int] = None
    phone_number: str
    event_type: str  # delivered, read, opened, clicked, replied, failed
    event_status: Optional[str] = None
    interaction_type: Optional[str] = None  # button_click, reply, url_open
    interaction_value: Optional[str] = None
    event_timestamp: Optional[datetime] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    raw_data: Dict[str, Any]

# Event tracking schemas
class MessageStats(BaseModel):
    id: int
    phone_number: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None
    click_count: int = 0
    reply_count: int = 0

class EventSummary(BaseModel):
    total_sent: int
    total_delivered: int
    total_read: int
    total_opened: int
    total_clicked: int
    total_replied: int
    delivery_rate: float
    read_rate: float
    engagement_rate: float

# Response schemas
class MessageResponse(BaseModel):
    id: int
    status: str
    message: str
    created_at: datetime
