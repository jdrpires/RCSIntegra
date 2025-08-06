from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class RCSMessage(Base):
    __tablename__ = "rcs_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String(255), nullable=True)
    account = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    template_id = Column(String(100), nullable=True)
    webhook = Column(String(500), nullable=True)
    bot_id = Column(String(100), nullable=True)
    callback_url = Column(String(500), nullable=True)
    
    # Content fields
    content_type = Column(String(50), nullable=False)  # text, image, video, pdf, richCard, carousel, suggestion
    content_data = Column(JSON, nullable=False)
    
    # Variables
    variables = Column(JSON, nullable=True)
    
    # Fallback
    fallback_enabled = Column(Boolean, default=False)
    fallback_channel = Column(String(10), nullable=True)
    fallback_content = Column(Text, nullable=True)
    
    # Status and tracking
    status = Column(String(50), default="pending")  # pending, sent, delivered, read, failed
    api_response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Tracking de eventos
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    
    # Contadores de interação
    click_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RCSTemplate(Base):
    __tablename__ = "rcs_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    template_data = Column(JSON, nullable=False)
    account = Column(String(100), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RCSCallback(Base):
    __tablename__ = "rcs_callbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, nullable=True)  # Reference to RCSMessage
    phone_number = Column(String(20), nullable=False)
    
    # Tipos de evento
    event_type = Column(String(50), nullable=False)  # delivered, read, opened, clicked, replied, failed
    event_status = Column(String(50), nullable=True)  # success, failed, pending
    
    # Dados específicos do evento
    callback_data = Column(JSON, nullable=False)
    
    # Dados de interação (para clicks, replies, etc)
    interaction_type = Column(String(50), nullable=True)  # button_click, reply, url_open
    interaction_value = Column(Text, nullable=True)  # valor do botão clicado, texto da resposta, etc
    
    # Metadados
    user_agent = Column(String(500), nullable=True)
    device_info = Column(JSON, nullable=True)
    
    # Timestamps
    event_timestamp = Column(DateTime(timezone=True), nullable=True)  # Quando o evento ocorreu
    received_at = Column(DateTime(timezone=True), server_default=func.now())  # Quando recebemos o callback
