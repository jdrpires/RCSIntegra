#!/usr/bin/env python3
"""
Script para criar perfis necessários e validar sistema de autenticação
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db, engine
from auth_service import AuthService
from auth_models import Client, User, APIKey, ClientTemplate
import httpx
import json

# Configurações dos perfis
PROFILES = {
    "admin_client": {
        "name": "Cliente Administrador",
        "email": "admin@rcsgateway.com",
        "rcs_account": "ADMIN_ACCOUNT",
        "allowed_message_types": ["basic", "single", "webhook", "template"],
        "max_messages_per_day": "10000",
        "callback_url": "https://admin.rcsgateway.com/callback"
    },
    "demo_client": {
        "name": "Cliente Demo",
        "email": "demo@exemplo.com",
        "rcs_account": "DEMO_ACCOUNT",
        "allowed_message_types": ["basic", "single"],
        "max_messages_per_day": "1000",
        "callback_url": "https://demo.exemplo.com/callback"
    },
    "test_client": {
        "name": "Cliente Teste",
        "email": "teste@teste.com",
        "rcs_account": "TEST_ACCOUNT",
        "allowed_message_types": ["basic"],
        "max_messages_per_day": "100"
    }
}

USERS = {
    "admin_user": {
        "username": "admin",
        "email": "admin@rcsgateway.com",
        "name": "Administrador do Sistema",
        "password": "Admin123!",
        "client_key": "admin_client",
        "permissions": {
            "can_send_basic": True,
            "can_send_single": True,
            "can_use_templates": True,
            "can_view_reports": True,
            "can_manage_users": True,
            "can_manage_templates": True
        }
    },
    "demo_user": {
        "username": "demo",
        "email": "demo@exemplo.com", 
        "name": "Usuário Demo",
        "password": "Demo123!",
        "client_key": "demo_client",
        "permissions": {
            "can_send_basic": True,
            "can_send_single": True,
            "can_use_templates": True,
            "can_view_reports": True
        }
    },
    "test_user": {
        "username": "teste",
        "email": "teste@teste.com",
        "name": "Usuário de Teste",
        "password": "Teste123!",
        "client_key": "test_client",
        "permissions": {
            "can_send_basic": True,
            "can_send_single": False,
            "can_use_templates": False,
            "can_view_reports": True
        }
    }
}

def create_profiles():
    """Cria os perfis de clientes e usuários"""
    print("🔧 Criando perfis de autenticação...")
    
    # Obter sessão do banco
    db = next(get_db())
    auth_service = AuthService(db)
    
    created_clients = {}
    created_users = {}
    created_api_keys = {}
    
    try:
        # Criar clientes
        print("\n📋 Criando clientes...")
        for client_key, client_data in PROFILES.items():
            try:
                # Verificar se já existe
                existing = db.query(Client).filter(Client.email == client_data["email"]).first()
                if existing:
                    print(f"  ⚠️  Cliente {client_key} já existe: {existing.client_code}")
                    created_clients[client_key] = existing
                    continue
                
                client = auth_service.create_client(**client_data)
                created_clients[client_key] = client
                print(f"  ✅ Cliente criado: {client.client_code} - {client.name}")
                
            except Exception as e:
                print(f"  ❌ Erro ao criar cliente {client_key}: {e}")
        
        # Criar usuários
        print("\n👥 Criando usuários...")
        for user_key, user_data in USERS.items():
            try:
                client_key = user_data.pop("client_key")
                if client_key not in created_clients:
                    print(f"  ⚠️  Cliente {client_key} não encontrado para usuário {user_key}")
                    continue
                
                # Verificar se já existe
                existing = db.query(User).filter(User.username == user_data["username"]).first()
                if existing:
                    print(f"  ⚠️  Usuário {user_key} já existe: {existing.username}")
                    created_users[user_key] = existing
                    continue
                
                client = created_clients[client_key]
                user = auth_service.create_user(
                    client_id=client.id,
                    **user_data
                )
                created_users[user_key] = user
                print(f"  ✅ Usuário criado: {user.username} - {user.name}")
                
            except Exception as e:
                print(f"  ❌ Erro ao criar usuário {user_key}: {e}")
        
        # Criar API Keys
        print("\n🔑 Criando API Keys...")
        for client_key, client in created_clients.items():
            try:
                # Verificar se já existe
                existing = db.query(APIKey).filter(APIKey.client_id == client.id).first()
                if existing:
                    print(f"  ⚠️  API Key já existe para {client_key}: {existing.key_name}")
                    created_api_keys[client_key] = existing
                    continue
                
                api_key = auth_service.create_api_key(
                    client_id=client.id,
                    key_name=f"Chave Principal - {client.name}",
                    scopes=["send_messages", "view_messages", "manage_templates"],
                    requests_per_minute="120",
                    requests_per_day="5000"
                )
                created_api_keys[client_key] = api_key
                print(f"  ✅ API Key criada para {client_key}: {api_key.key_name}")
                
            except Exception as e:
                print(f"  ❌ Erro ao criar API Key para {client_key}: {e}")
        
        # Criar templates de exemplo
        print("\n📄 Criando templates de exemplo...")
        create_sample_templates(db, created_clients)
        
        print("\n✅ Perfis criados com sucesso!")
        return created_clients, created_users, created_api_keys
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        db.rollback()
        return {}, {}, {}
    finally:
        db.close()

def create_sample_templates(db: Session, clients: dict):
    """Cria templates de exemplo para os clientes"""
    
    templates = [
        {
            "template_name": "Boas Vindas",
            "template_type": "basic",
            "template_data": {
                "text": {
                    "message": "Olá {{nome}}! Bem-vindo à nossa plataforma. Seu código de acesso é: {{codigo}}"
                }
            },
            "variables": ["nome", "codigo"]
        },
        {
            "template_name": "Promoção Rich Card",
            "template_type": "single",
            "template_data": {
                "richCard": {
                    "title": "🎉 Oferta Especial para {{nome}}!",
                    "description": "Aproveite {{desconto}}% de desconto em {{produto}}. Válido até {{validade}}.",
                    "fileUrl": "https://exemplo.com/promocao.jpg",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Ver Oferta",
                            "value": "https://loja.exemplo.com/promocao"
                        },
                        {
                            "type": "call",
                            "title": "Ligar",
                            "value": "1140001234"
                        }
                    ]
                }
            },
            "variables": ["nome", "desconto", "produto", "validade"]
        }
    ]
    
    for client_key, client in clients.items():
        for template_data in templates:
            try:
                # Verificar se já existe
                existing = db.query(ClientTemplate).filter(
                    ClientTemplate.client_id == client.id,
                    ClientTemplate.template_name == template_data["template_name"]
                ).first()
                
                if existing:
                    continue
                
                template = ClientTemplate(
                    client_id=client.id,
                    **template_data
                )
                db.add(template)
                db.commit()
                print(f"  ✅ Template '{template_data['template_name']}' criado para {client_key}")
                
            except Exception as e:
                print(f"  ❌ Erro ao criar template para {client_key}: {e}")

async def validate_authentication():
    """Valida o sistema de autenticação"""
    print("\n🔍 Validando sistema de autenticação...")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # Teste 1: Login com usuário válido
            print("\n1️⃣ Testando login com usuário válido...")
            login_data = {
                "username": "admin",
                "password": "Admin123!"
            }
            
            response = await client.post(f"{base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                print(f"  ✅ Login bem-sucedido! Token: {token_data['access_token'][:20]}...")
                access_token = token_data["access_token"]
            else:
                print(f"  ❌ Falha no login: {response.status_code} - {response.text}")
                return False
            
            # Teste 2: Acesso a endpoint protegido
            print("\n2️⃣ Testando acesso a endpoint protegido...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = await client.get(f"{base_url}/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"  ✅ Acesso autorizado! Usuário: {user_data['username']}")
            else:
                print(f"  ❌ Falha na autorização: {response.status_code} - {response.text}")
                return False
            
            # Teste 3: Login com credenciais inválidas
            print("\n3️⃣ Testando login com credenciais inválidas...")
            invalid_login = {
                "username": "admin",
                "password": "senhaerrada"
            }
            
            response = await client.post(f"{base_url}/auth/login", json=invalid_login)
            if response.status_code == 401:
                print("  ✅ Credenciais inválidas rejeitadas corretamente!")
            else:
                print(f"  ❌ Falha na validação: {response.status_code} - {response.text}")
                return False
            
            # Teste 4: Acesso sem token
            print("\n4️⃣ Testando acesso sem token...")
            response = await client.get(f"{base_url}/auth/me")
            if response.status_code == 401:
                print("  ✅ Acesso não autorizado rejeitado corretamente!")
            else:
                print(f"  ❌ Falha na proteção: {response.status_code} - {response.text}")
                return False
            
            # Teste 5: Listar clientes (admin)
            print("\n5️⃣ Testando listagem de clientes...")
            response = await client.get(f"{base_url}/auth/clients", headers=headers)
            if response.status_code == 200:
                clients = response.json()
                print(f"  ✅ Clientes listados: {len(clients)} encontrados")
            else:
                print(f"  ❌ Falha na listagem: {response.status_code} - {response.text}")
                return False
            
            print("\n✅ Todos os testes de autenticação passaram!")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante validação: {e}")
            return False

def print_summary(clients, users, api_keys):
    """Imprime resumo dos perfis criados"""
    print("\n" + "="*60)
    print("📊 RESUMO DOS PERFIS CRIADOS")
    print("="*60)
    
    print("\n🏢 CLIENTES:")
    for client_key, client in clients.items():
        print(f"  • {client.name}")
        print(f"    Código: {client.client_code}")
        print(f"    Email: {client.email}")
        print(f"    Account RCS: {client.rcs_account}")
        print(f"    Tipos permitidos: {', '.join(client.allowed_message_types)}")
        print()
    
    print("👥 USUÁRIOS:")
    for user_key, user in users.items():
        print(f"  • {user.name} (@{user.username})")
        print(f"    Email: {user.email}")
        print(f"    Cliente: {user.client.name}")
        print(f"    Permissões: {len([k for k, v in user.permissions.items() if v])} ativas")
        print()
    
    print("🔑 API KEYS:")
    for client_key, api_key in api_keys.items():
        print(f"  • {api_key.key_name}")
        print(f"    Cliente: {api_key.client.name}")
        print(f"    Chave: {api_key.api_key[:20]}...")
        print(f"    Escopos: {', '.join(api_key.scopes)}")
        print()
    
    print("🔐 CREDENCIAIS DE TESTE:")
    print("  Admin:")
    print("    Username: admin")
    print("    Password: Admin123!")
    print()
    print("  Demo:")
    print("    Username: demo") 
    print("    Password: Demo123!")
    print()
    print("  Teste:")
    print("    Username: teste")
    print("    Password: Teste123!")
    print()
    
    print("🌐 ENDPOINTS DISPONÍVEIS:")
    print("  • POST /auth/login - Login de usuário")
    print("  • GET /auth/me - Dados do usuário logado")
    print("  • GET /auth/clients - Listar clientes")
    print("  • POST /auth/clients - Criar cliente")
    print("  • GET /docs - Documentação da API")
    print()

async def main():
    """Função principal"""
    print("🚀 Configurando Sistema de Autenticação RCS Gateway")
    print("="*60)
    
    # Criar perfis
    clients, users, api_keys = create_profiles()
    
    if not clients:
        print("❌ Falha ao criar perfis. Abortando validação.")
        return
    
    # Aguardar um pouco para o sistema estabilizar
    print("\n⏳ Aguardando sistema estabilizar...")
    await asyncio.sleep(2)
    
    # Validar autenticação
    validation_success = await validate_authentication()
    
    # Imprimir resumo
    print_summary(clients, users, api_keys)
    
    if validation_success:
        print("🎉 Sistema de autenticação configurado e validado com sucesso!")
        print("\n💡 Próximos passos:")
        print("  1. Acesse http://localhost:8000/docs para ver a documentação")
        print("  2. Faça login com as credenciais acima")
        print("  3. Teste os endpoints de envio de mensagens")
        print("  4. Configure seus próprios clientes e usuários")
    else:
        print("⚠️ Sistema configurado, mas validação falhou. Verifique os logs.")

if __name__ == "__main__":
    asyncio.run(main())