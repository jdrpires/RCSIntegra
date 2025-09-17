"""
Rotas para gerenciar mapeamentos DE/PARA entre clientes internos e códigos Pointer
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from client_mapping_service import ClientMappingService
from client_mapping_schemas import (
    ClientPointerMappingCreate, ClientPointerMappingUpdate, ClientPointerMapping,
    PointerAccountConfigCreate, PointerAccountConfig,
    MappingAuditLog, ClientMappingInfo, MappingValidationRequest, MappingValidationResponse,
    BulkMappingCreate, MappingStatsResponse
)
from auth_routes import get_current_user
from auth_models import User

router = APIRouter()


def get_mapping_service(db: Session = Depends(get_db)) -> ClientMappingService:
    return ClientMappingService(db)


@router.post("/mappings", response_model=ClientPointerMapping)
def create_mapping(
    mapping_data: ClientPointerMappingCreate,
    current_user: User = Depends(get_current_user),
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Criar novo mapeamento DE/PARA"""
    return mapping_service.create_mapping(
        created_by=current_user.username,
        **mapping_data.dict()
    )


@router.get("/mappings", response_model=List[dict])
def list_mappings(
    environment: Optional[str] = None,
    active_only: bool = True,
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Listar todos os mapeamentos"""
    return mapping_service.list_mappings(environment=environment, active_only=active_only)


@router.get("/mappings/{mapping_id}", response_model=ClientPointerMapping)
def get_mapping(
    mapping_id: str,
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Obter mapeamento específico"""
    mapping = mapping_service.db.query(mapping_service.db.query(ClientPointerMapping).filter(
        ClientPointerMapping.id == mapping_id
    ).first())
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapeamento não encontrado")
    
    return mapping


@router.put("/mappings/{mapping_id}", response_model=ClientPointerMapping)
def update_mapping(
    mapping_id: str,
    mapping_data: ClientPointerMappingUpdate,
    current_user: User = Depends(get_current_user),
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Atualizar mapeamento existente"""
    return mapping_service.update_mapping(
        mapping_id=mapping_id,
        **mapping_data.dict(exclude_unset=True)
    )


@router.delete("/mappings/{mapping_id}")
def deactivate_mapping(
    mapping_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Desativar mapeamento"""
    success = mapping_service.deactivate_mapping(mapping_id, reason)
    return {"message": "Mapeamento desativado com sucesso", "success": success}


@router.get("/mappings/client/{client_code}")
def get_mapping_by_client(
    client_code: str,
    environment: str = "production",
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Obter mapeamento por código do cliente"""
    config = mapping_service.get_pointer_config(client_code, environment)
    
    if not config:
        raise HTTPException(
            status_code=404, 
            detail=f"Mapeamento não encontrado para cliente {client_code} no ambiente {environment}"
        )
    
    return config


@router.post("/mappings/validate", response_model=MappingValidationResponse)
def validate_client_access(
    validation_request: MappingValidationRequest,
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Validar se cliente tem acesso ao tipo de mensagem"""
    
    valid = mapping_service.validate_pointer_access(
        validation_request.client_code,
        validation_request.message_type,
        validation_request.environment
    )
    
    config = mapping_service.get_pointer_config(
        validation_request.client_code,
        validation_request.environment
    )
    
    return MappingValidationResponse(
        valid=valid,
        client_code=validation_request.client_code,
        pointer_account=config.get("pointer_account") if config else None,
        pointer_code=config.get("pointer_code") if config else None,
        message_type=validation_request.message_type,
        environment=validation_request.environment,
        error_message=None if valid else f"Cliente {validation_request.client_code} não tem acesso ao tipo {validation_request.message_type}"
    )


@router.post("/pointer-configs", response_model=PointerAccountConfig)
def create_pointer_config(
    config_data: PointerAccountConfigCreate,
    current_user: User = Depends(get_current_user),
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Criar configuração para conta Pointer"""
    return mapping_service.create_pointer_account_config(**config_data.dict())


@router.get("/pointer-configs")
def list_pointer_configs(
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Listar configurações de contas Pointer"""
    from client_mapping_models import PointerAccountConfig
    
    configs = mapping_service.db.query(PointerAccountConfig).filter(
        PointerAccountConfig.is_active == True
    ).all()
    
    return configs


@router.get("/mappings/{mapping_id}/audit", response_model=List[MappingAuditLog])
def get_mapping_audit_log(
    mapping_id: str,
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Obter histórico de mudanças de um mapeamento"""
    return mapping_service.get_audit_log(mapping_id)


@router.post("/mappings/bulk")
def create_bulk_mappings(
    bulk_data: BulkMappingCreate,
    current_user: User = Depends(get_current_user),
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Criar múltiplos mapeamentos em lote"""
    
    results = []
    errors = []
    
    for i, mapping_data in enumerate(bulk_data.mappings):
        try:
            mapping = mapping_service.create_mapping(
                environment=bulk_data.environment,
                created_by=bulk_data.created_by or current_user.username,
                **mapping_data
            )
            results.append({
                "index": i,
                "success": True,
                "mapping_id": mapping.id,
                "client_code": mapping.client_code
            })
        except Exception as e:
            errors.append({
                "index": i,
                "success": False,
                "error": str(e),
                "data": mapping_data
            })
    
    return {
        "total_processed": len(bulk_data.mappings),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@router.get("/mappings/stats", response_model=MappingStatsResponse)
def get_mapping_stats(
    mapping_service: ClientMappingService = Depends(get_mapping_service)
):
    """Obter estatísticas dos mapeamentos"""
    from client_mapping_models import ClientPointerMapping
    from sqlalchemy import func
    
    # Total de mapeamentos
    total = mapping_service.db.query(ClientPointerMapping).count()
    
    # Ativos vs Inativos
    active = mapping_service.db.query(ClientPointerMapping).filter(
        ClientPointerMapping.is_active == True
    ).count()
    
    inactive = total - active
    
    # Por ambiente
    by_env = mapping_service.db.query(
        ClientPointerMapping.environment,
        func.count(ClientPointerMapping.id)
    ).group_by(ClientPointerMapping.environment).all()
    
    # Por conta Pointer
    by_account = mapping_service.db.query(
        ClientPointerMapping.pointer_account,
        func.count(ClientPointerMapping.id)
    ).group_by(ClientPointerMapping.pointer_account).all()
    
    return MappingStatsResponse(
        total_mappings=total,
        active_mappings=active,
        inactive_mappings=inactive,
        by_environment={env: count for env, count in by_env},
        by_pointer_account={account: count for account, count in by_account}
    )