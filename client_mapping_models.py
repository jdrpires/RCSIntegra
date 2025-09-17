"""
Modelos para mapeamento DE/PARA entre clientes internos e códigos Pointer
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid


class ClientPointerMapping(Base):
    """Mapeamento DE/PARA: Cliente Interno → Código Pointer"""
    __tablename__ = "client_pointer_mappings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # DE: Cliente interno
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    client_code = Column(String(50), nullable=False)  # Código do cliente interno
    
    # PARA: Código na Pointer (Eugen)
    pointer_account = Column(String(100), nullable=False)  # Account ID na Pointer
    pointer_code = Column(String(100), nullable=False)     # Código específico na Pointer
    pointer_token = Column(String(500), nullable=True)     # Token específico (opcional)
    
    # Configurações do mapeamento
    is_active = Column(Boolean, default=True)
    environment = Column(String(20), default="production")  # production, staging, test
    
    # Metadados
    description = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    client = relationship("Client")
    
    # Constraint para evitar duplicatas
    __table_args__ = (
        UniqueConstraint('client_id', 'environment', name='unique_client_env'),
    )


class PointerAccountConfig(Base):
    """Configurações específicas por conta Pointer"""
    __tablename__ = "pointer_account_configs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação da conta Pointer
    pointer_account = Column(String(100), unique=True, nullable=False)
    account_name = Column(String(255), nullable=False)
    
    # Configurações técnicas
    api_base_url = Column(String(500), default="https://pointer-rcs-api-node.eugen.com.br")
    api_token = Column(String(500), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    
    # Limites e configurações
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_day = Column(Integer, default=1000)
    max_message_length = Column(Integer, default=5000)
    
    # Tipos de mensagem suportados
    supported_message_types = Column(JSON, default=["basic", "single", "webhook", "template"])
    
    # Configurações de fallback
    fallback_enabled = Column(Boolean, default=True)
    fallback_provider = Column(String(50), default="SMS")
    
    # Status
    is_active = Column(Boolean, default=True)
    environment = Column(String(20), default="production")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MappingAuditLog(Base):
    """Log de auditoria para mudanças nos mapeamentos"""
    __tablename__ = "mapping_audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Referência ao mapeamento
    mapping_id = Column(String, ForeignKey("client_pointer_mappings.id"), nullable=False)
    
    # Ação realizada
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, ACTIVATE, DEACTIVATE
    
    # Dados da mudança
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Quem fez a mudança
    changed_by = Column(String, nullable=True)
    change_reason = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    mapping = relationship("ClientPointerMapping")