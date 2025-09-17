"""
Serviço para gerenciar mapeamentos DE/PARA entre clientes internos e códigos Pointer
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from client_mapping_models import ClientPointerMapping, PointerAccountConfig, MappingAuditLog
from auth_models import Client
import json


class ClientMappingService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_mapping(self, client_id: str, pointer_account: str, pointer_code: str, 
                      environment: str = "production", **kwargs) -> ClientPointerMapping:
        """Cria novo mapeamento DE/PARA"""
        
        # Verificar se cliente existe
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        # Verificar se já existe mapeamento para este cliente/ambiente
        existing = self.db.query(ClientPointerMapping).filter(
            ClientPointerMapping.client_id == client_id,
            ClientPointerMapping.environment == environment
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Mapeamento já existe para cliente {client.client_code} no ambiente {environment}"
            )
        
        # Criar mapeamento
        mapping = ClientPointerMapping(
            client_id=client_id,
            client_code=client.client_code,
            pointer_account=pointer_account,
            pointer_code=pointer_code,
            environment=environment,
            **kwargs
        )
        
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        
        # Log de auditoria
        self._log_mapping_change(mapping.id, "CREATE", None, {
            "client_code": client.client_code,
            "pointer_account": pointer_account,
            "pointer_code": pointer_code,
            "environment": environment
        })
        
        return mapping
    
    def get_pointer_config(self, client_code: str, environment: str = "production") -> Optional[Dict[str, Any]]:
        """Obtém configuração Pointer para um cliente interno"""
        
        mapping = self.db.query(ClientPointerMapping).join(Client).filter(
            Client.client_code == client_code,
            ClientPointerMapping.environment == environment,
            ClientPointerMapping.is_active == True
        ).first()
        
        if not mapping:
            return None
        
        # Buscar configurações da conta Pointer
        pointer_config = self.db.query(PointerAccountConfig).filter(
            PointerAccountConfig.pointer_account == mapping.pointer_account,
            PointerAccountConfig.environment == environment,
            PointerAccountConfig.is_active == True
        ).first()
        
        return {
            "client_code": mapping.client_code,
            "pointer_account": mapping.pointer_account,
            "pointer_code": mapping.pointer_code,
            "pointer_token": mapping.pointer_token,
            "api_base_url": pointer_config.api_base_url if pointer_config else "https://pointer-rcs-api-node.eugen.com.br",
            "api_token": pointer_config.api_token if pointer_config else mapping.pointer_token,
            "webhook_url": pointer_config.webhook_url if pointer_config else None,
            "rate_limits": {
                "per_minute": pointer_config.rate_limit_per_minute if pointer_config else 60,
                "per_day": pointer_config.rate_limit_per_day if pointer_config else 1000
            },
            "supported_types": pointer_config.supported_message_types if pointer_config else ["basic", "single"],
            "fallback_enabled": pointer_config.fallback_enabled if pointer_config else True
        }
    
    def list_mappings(self, environment: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Lista todos os mapeamentos"""
        
        query = self.db.query(ClientPointerMapping).join(Client)
        
        if environment:
            query = query.filter(ClientPointerMapping.environment == environment)
        
        if active_only:
            query = query.filter(ClientPointerMapping.is_active == True)
        
        mappings = query.all()
        
        return [
            {
                "id": mapping.id,
                "client_name": mapping.client.name,
                "client_code": mapping.client_code,
                "pointer_account": mapping.pointer_account,
                "pointer_code": mapping.pointer_code,
                "environment": mapping.environment,
                "is_active": mapping.is_active,
                "description": mapping.description,
                "created_at": mapping.created_at
            }
            for mapping in mappings
        ]
    
    def update_mapping(self, mapping_id: str, **updates) -> ClientPointerMapping:
        """Atualiza mapeamento existente"""
        
        mapping = self.db.query(ClientPointerMapping).filter(
            ClientPointerMapping.id == mapping_id
        ).first()
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapeamento não encontrado")
        
        # Salvar valores antigos para auditoria
        old_values = {
            "pointer_account": mapping.pointer_account,
            "pointer_code": mapping.pointer_code,
            "is_active": mapping.is_active,
            "description": mapping.description
        }
        
        # Aplicar atualizações
        for field, value in updates.items():
            if hasattr(mapping, field):
                setattr(mapping, field, value)
        
        self.db.commit()
        self.db.refresh(mapping)
        
        # Log de auditoria
        new_values = {
            "pointer_account": mapping.pointer_account,
            "pointer_code": mapping.pointer_code,
            "is_active": mapping.is_active,
            "description": mapping.description
        }
        
        self._log_mapping_change(mapping.id, "UPDATE", old_values, new_values)
        
        return mapping
    
    def deactivate_mapping(self, mapping_id: str, reason: Optional[str] = None) -> bool:
        """Desativa mapeamento"""
        
        mapping = self.db.query(ClientPointerMapping).filter(
            ClientPointerMapping.id == mapping_id
        ).first()
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapeamento não encontrado")
        
        old_active = mapping.is_active
        mapping.is_active = False
        
        self.db.commit()
        
        # Log de auditoria
        self._log_mapping_change(
            mapping.id, 
            "DEACTIVATE", 
            {"is_active": old_active}, 
            {"is_active": False},
            reason
        )
        
        return True
    
    def create_pointer_account_config(self, pointer_account: str, account_name: str, **config) -> PointerAccountConfig:
        """Cria configuração para conta Pointer"""
        
        # Verificar se já existe
        existing = self.db.query(PointerAccountConfig).filter(
            PointerAccountConfig.pointer_account == pointer_account
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Configuração já existe para conta {pointer_account}"
            )
        
        pointer_config = PointerAccountConfig(
            pointer_account=pointer_account,
            account_name=account_name,
            **config
        )
        
        self.db.add(pointer_config)
        self.db.commit()
        self.db.refresh(pointer_config)
        
        return pointer_config
    
    def get_mapping_by_client_code(self, client_code: str, environment: str = "production") -> Optional[ClientPointerMapping]:
        """Busca mapeamento por código do cliente"""
        
        return self.db.query(ClientPointerMapping).join(Client).filter(
            Client.client_code == client_code,
            ClientPointerMapping.environment == environment,
            ClientPointerMapping.is_active == True
        ).first()
    
    def validate_pointer_access(self, client_code: str, message_type: str, environment: str = "production") -> bool:
        """Valida se cliente tem acesso ao tipo de mensagem na Pointer"""
        
        config = self.get_pointer_config(client_code, environment)
        
        if not config:
            return False
        
        return message_type in config.get("supported_types", [])
    
    def _log_mapping_change(self, mapping_id: str, action: str, old_values: Optional[Dict], 
                           new_values: Optional[Dict], reason: Optional[str] = None):
        """Registra mudança no log de auditoria"""
        
        log = MappingAuditLog(
            mapping_id=mapping_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            change_reason=reason
        )
        
        self.db.add(log)
        self.db.commit()
    
    def get_audit_log(self, mapping_id: str) -> List[Dict[str, Any]]:
        """Obtém histórico de mudanças de um mapeamento"""
        
        logs = self.db.query(MappingAuditLog).filter(
            MappingAuditLog.mapping_id == mapping_id
        ).order_by(MappingAuditLog.created_at.desc()).all()
        
        return [
            {
                "id": log.id,
                "action": log.action,
                "old_values": log.old_values,
                "new_values": log.new_values,
                "changed_by": log.changed_by,
                "change_reason": log.change_reason,
                "created_at": log.created_at
            }
            for log in logs
        ]