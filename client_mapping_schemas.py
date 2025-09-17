"""
Schemas Pydantic para mapeamentos DE/PARA
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ClientPointerMappingBase(BaseModel):
    pointer_account: str
    pointer_code: str
    pointer_token: Optional[str] = None
    environment: str = "production"
    description: Optional[str] = None
    created_by: Optional[str] = None

    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['production', 'staging', 'test']
        if v not in allowed:
            raise ValueError(f'Environment deve ser um de: {allowed}')
        return v


class ClientPointerMappingCreate(ClientPointerMappingBase):
    client_id: str


class ClientPointerMappingUpdate(BaseModel):
    pointer_account: Optional[str] = None
    pointer_code: Optional[str] = None
    pointer_token: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ClientPointerMapping(ClientPointerMappingBase):
    id: str
    client_id: str
    client_code: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PointerAccountConfigBase(BaseModel):
    pointer_account: str
    account_name: str
    api_base_url: str = "https://pointer-rcs-api-node.eugen.com.br"
    api_token: Optional[str] = None
    webhook_url: Optional[str] = None
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 1000
    max_message_length: int = 5000
    supported_message_types: List[str] = ["basic", "single", "webhook", "template"]
    fallback_enabled: bool = True
    fallback_provider: str = "SMS"
    environment: str = "production"


class PointerAccountConfigCreate(PointerAccountConfigBase):
    pass


class PointerAccountConfig(PointerAccountConfigBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MappingAuditLog(BaseModel):
    id: str
    mapping_id: str
    action: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_by: Optional[str] = None
    change_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClientMappingInfo(BaseModel):
    """Informações completas do mapeamento para um cliente"""
    client_code: str
    client_name: str
    pointer_account: str
    pointer_code: str
    environment: str
    is_active: bool
    api_config: Dict[str, Any]


class MappingValidationRequest(BaseModel):
    """Request para validar acesso de cliente"""
    client_code: str
    message_type: str
    environment: str = "production"


class MappingValidationResponse(BaseModel):
    """Response da validação de acesso"""
    valid: bool
    client_code: str
    pointer_account: Optional[str] = None
    pointer_code: Optional[str] = None
    message_type: str
    environment: str
    error_message: Optional[str] = None


class BulkMappingCreate(BaseModel):
    """Criação em lote de mapeamentos"""
    mappings: List[Dict[str, Any]]
    environment: str = "production"
    created_by: Optional[str] = None


class MappingStatsResponse(BaseModel):
    """Estatísticas dos mapeamentos"""
    total_mappings: int
    active_mappings: int
    inactive_mappings: int
    by_environment: Dict[str, int]
    by_pointer_account: Dict[str, int]