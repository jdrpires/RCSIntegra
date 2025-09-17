#!/usr/bin/env python3
"""
Script para criar mapeamentos DE/PARA de exemplo
"""
from sqlalchemy.orm import Session
from database import get_db
from client_mapping_service import ClientMappingService
from client_mapping_models import PointerAccountConfig
from auth_models import Client

def setup_mappings():
    """Cria mapeamentos DE/PARA de exemplo"""
    print("🔗 Configurando Mapeamentos DE/PARA")
    print("="*50)
    
    db = next(get_db())
    mapping_service = ClientMappingService(db)
    
    try:
        # 1. Criar configurações de contas Pointer
        print("\n📋 Criando configurações Pointer...")
        
        pointer_configs = [
            {
                "pointer_account": "ADMIN_POINTER_001",
                "account_name": "Conta Admin Pointer",
                "api_token": "admin_pointer_token_123",
                "rate_limit_per_minute": 120,
                "rate_limit_per_day": 10000,
                "supported_message_types": ["basic", "single", "webhook", "template"],
                "environment": "production"
            },
            {
                "pointer_account": "DEMO_POINTER_002", 
                "account_name": "Conta Demo Pointer",
                "api_token": "demo_pointer_token_456",
                "rate_limit_per_minute": 60,
                "rate_limit_per_day": 5000,
                "supported_message_types": ["basic", "single"],
                "environment": "production"
            },
            {
                "pointer_account": "TEST_POINTER_003",
                "account_name": "Conta Teste Pointer",
                "api_token": "test_pointer_token_789",
                "rate_limit_per_minute": 30,
                "rate_limit_per_day": 1000,
                "supported_message_types": ["basic"],
                "environment": "test"
            }
        ]
        
        for config in pointer_configs:
            try:
                existing = db.query(PointerAccountConfig).filter(
                    PointerAccountConfig.pointer_account == config["pointer_account"]
                ).first()
                
                if existing:
                    print(f"  ⚠️  Configuração já existe: {config['pointer_account']}")
                    continue
                
                pointer_config = mapping_service.create_pointer_account_config(**config)
                print(f"  ✅ Configuração criada: {pointer_config.pointer_account}")
                
            except Exception as e:
                print(f"  ❌ Erro ao criar configuração {config['pointer_account']}: {e}")
        
        # 2. Buscar clientes existentes
        print("\n👥 Buscando clientes existentes...")
        clients = db.query(Client).all()
        
        if not clients:
            print("  ⚠️  Nenhum cliente encontrado. Execute setup_auth_profiles.py primeiro.")
            return
        
        # 3. Criar mapeamentos DE/PARA
        print("\n🔗 Criando mapeamentos DE/PARA...")
        
        mappings_data = [
            {
                "client_code": "CLI_2EDF5B7E",  # Admin
                "pointer_account": "ADMIN_POINTER_001",
                "pointer_code": "ADM_PTR_001",
                "description": "Mapeamento Admin - Conta principal com todos os recursos",
                "environment": "production"
            },
            {
                "client_code": "CLI_57BC2C59",  # Demo
                "pointer_account": "DEMO_POINTER_002", 
                "pointer_code": "DEMO_PTR_002",
                "description": "Mapeamento Demo - Conta limitada para demonstrações",
                "environment": "production"
            },
            {
                "client_code": "CLI_5D67211A",  # Teste
                "pointer_account": "TEST_POINTER_003",
                "pointer_code": "TEST_PTR_003", 
                "description": "Mapeamento Teste - Conta para testes básicos",
                "environment": "test"
            }
        ]
        
        for mapping_data in mappings_data:
            try:
                # Buscar cliente pelo código
                client = db.query(Client).filter(
                    Client.client_code == mapping_data["client_code"]
                ).first()
                
                if not client:
                    print(f"  ⚠️  Cliente não encontrado: {mapping_data['client_code']}")
                    continue
                
                # Verificar se mapeamento já existe
                existing = mapping_service.get_mapping_by_client_code(
                    mapping_data["client_code"],
                    mapping_data["environment"]
                )
                
                if existing:
                    print(f"  ⚠️  Mapeamento já existe: {mapping_data['client_code']} -> {existing.pointer_account}")
                    continue
                
                # Criar mapeamento
                mapping = mapping_service.create_mapping(
                    client_id=client.id,
                    pointer_account=mapping_data["pointer_account"],
                    pointer_code=mapping_data["pointer_code"],
                    description=mapping_data["description"],
                    environment=mapping_data["environment"],
                    created_by="setup_script"
                )
                
                print(f"  ✅ Mapeamento criado: {mapping.client_code} -> {mapping.pointer_account}")
                
            except Exception as e:
                print(f"  ❌ Erro ao criar mapeamento {mapping_data['client_code']}: {e}")
        
        # 4. Mostrar resumo
        print("\n📊 Resumo dos Mapeamentos:")
        mappings = mapping_service.list_mappings()
        
        for mapping in mappings:
            print(f"  • {mapping['client_code']} -> {mapping['pointer_account']}")
            print(f"    Ambiente: {mapping['environment']}")
            print(f"    Status: {'Ativo' if mapping['is_active'] else 'Inativo'}")
            print()
        
        print("✅ Mapeamentos DE/PARA configurados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        db.rollback()
    finally:
        db.close()

def test_mappings():
    """Testa os mapeamentos criados"""
    print("\n🧪 Testando Mapeamentos...")
    print("="*50)
    
    db = next(get_db())
    mapping_service = ClientMappingService(db)
    
    try:
        # Testar cada cliente
        test_clients = ["CLI_2EDF5B7E", "CLI_57BC2C59", "CLI_5D67211A"]
        
        for client_code in test_clients:
            print(f"\n🔍 Testando cliente: {client_code}")
            
            # Obter configuração
            config = mapping_service.get_pointer_config(client_code)
            
            if config:
                print(f"  ✅ Configuração encontrada:")
                print(f"    Pointer Account: {config['pointer_account']}")
                print(f"    Pointer Code: {config['pointer_code']}")
                print(f"    API URL: {config['api_base_url']}")
                print(f"    Rate Limits: {config['rate_limits']['per_minute']}/min, {config['rate_limits']['per_day']}/dia")
                print(f"    Tipos suportados: {', '.join(config['supported_types'])}")
                
                # Testar validação de acesso
                for msg_type in ["basic", "single", "webhook"]:
                    valid = mapping_service.validate_pointer_access(client_code, msg_type)
                    status = "✅" if valid else "❌"
                    print(f"    {status} {msg_type}: {'Permitido' if valid else 'Negado'}")
            else:
                print(f"  ❌ Configuração não encontrada")
        
        print("\n✅ Testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro durante testes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_mappings()
    test_mappings()