"""
Modelos de autenticação e multi-tenancy para RCS Gateway
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid


class Client(Base):
    """Modelo para clientes da API"""
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    client_code = Column(String(50), unique=True, nullable=False)  # Código único do cliente
    rcs_account = Column(String(100), nullable=False)  # Account ID da Eugen
    api_token = Column(String(500), nullable=True)  # Token da Eugen (opcional)
    is_active = Column(Boolean, default=True)
    
    # Configurações do cliente
    allowed_message_types = Column(JSON, default=["basic", "single"])  # Tipos permitidos
    max_messages_per_day = Column(String, default="1000")
    callback_url = Column(String(500), nullable=True)  # URL de callback padrão
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    users = relationship("User", back_populates="client", cascade="all, delete-orphan")
    # messages = relationship("RCSMessage", back_populates="client")  # Comentado por enquanto


class User(Base):
    """Modelo para usuários dos clientes"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Relacionamento com cliente
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    
    # Permissões específicas do usuário
    permissions = Column(JSON, default={
        "can_send_basic": True,
        "can_send_single": True,
        "can_use_templates": True,
        "can_view_reports": True
    })
    
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    client = relationship("Client", back_populates="users")


class APIKey(Base):
    """Modelo para chaves de API dos clientes"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    key_name = Column(String(100), nullable=False)  # Nome da chave
    api_key = Column(String(500), unique=True, nullable=False)  # Chave da API
    
    # Configurações da chave
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Permissões específicas da chave
    scopes = Column(JSON, default=["send_messages", "view_messages"])
    
    # Rate limiting
    requests_per_minute = Column(String, default="60")
    requests_per_day = Column(String, default="1000")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    client = relationship("Client")


class ClientTemplate(Base):
    """Modelo para templates específicos dos clientes"""
    __tablename__ = "client_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    template_name = Column(String(255), nullable=False)
    template_type = Column(String(50), nullable=False)  # basic, single, richCard, etc.
    
    # Conteúdo do template
    template_data = Column(JSON, nullable=False)
    variables = Column(JSON, default=[])  # Lista de variáveis disponíveis
    
    # Configurações
    is_active = Column(Boolean, default=True)
    usage_count = Column(String, default="0")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    client = relationship("Client")


class MessageLog(Base):
    """Log de mensagens enviadas por cliente"""
    __tablename__ = "message_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Referência à mensagem original (sem FK por enquanto)
    rcs_message_id = Column(Integer, nullable=False)
    
    # Dados da requisição
    endpoint_used = Column(String(100), nullable=False)  # /api/client/send-basic, etc.
    request_data = Column(JSON, nullable=True)
    
    # Resultado
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    client = relationship("Client")
    user = relationship("User")
    # rcs_message = relationship("RCSMessage")  # Comentado por enquanto
