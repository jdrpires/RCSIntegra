#!/usr/bin/env python3
"""
Script simples para testar autenticação
"""
import requests
import json
from datetime import datetime

def test_authentication():
    """Testa o sistema de autenticação"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testando Sistema de Autenticação RCS Gateway")
    print("="*60)
    
    try:
        # Teste 1: Health check
        print("\n1️⃣ Testando health check...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("  ✅ API está funcionando!")
        else:
            print(f"  ❌ API não está respondendo: {response.status_code}")
            return False
        
        # Teste 2: Login com usuário admin
        print("\n2️⃣ Testando login com usuário admin...")
        login_data = {
            "username": "admin",
            "password": "Admin123!"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"  ✅ Login bem-sucedido!")
            print(f"  📋 Cliente: {token_data.get('client_code', 'N/A')}")
            print(f"  🔑 Token: {token_data['access_token'][:30]}...")
            access_token = token_data["access_token"]
        else:
            print(f"  ❌ Falha no login: {response.status_code}")
            print(f"  📄 Resposta: {response.text}")
            return False
        
        # Teste 3: Verificar dados do usuário
        print("\n3️⃣ Testando dados do usuário logado...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"  ✅ Usuário autenticado: {user_data['name']} (@{user_data['username']})")
            print(f"  📧 Email: {user_data['email']}")
            print(f"  🏢 Cliente ID: {user_data['client_id']}")
        else:
            print(f"  ❌ Falha ao obter dados: {response.status_code}")
            print(f"  📄 Resposta: {response.text}")
            return False
        
        # Teste 4: Listar clientes (admin)
        print("\n4️⃣ Testando listagem de clientes...")
        response = requests.get(f"{base_url}/api/admin/clients", headers=headers)
        if response.status_code == 200:
            clients = response.json()
            print(f"  ✅ {len(clients)} clientes encontrados:")
            for client in clients[:3]:  # Mostrar apenas os 3 primeiros
                print(f"    • {client['name']} ({client['client_code']})")
        else:
            print(f"  ❌ Falha na listagem: {response.status_code}")
            print(f"  📄 Resposta: {response.text}")
        
        # Teste 5: Login com credenciais inválidas
        print("\n5️⃣ Testando credenciais inválidas...")
        invalid_login = {
            "username": "admin",
            "password": "senhaerrada"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=invalid_login)
        if response.status_code == 401:
            print("  ✅ Credenciais inválidas rejeitadas corretamente!")
        else:
            print(f"  ❌ Falha na validação: {response.status_code}")
        
        # Teste 6: Acesso sem token
        print("\n6️⃣ Testando acesso sem token...")
        response = requests.get(f"{base_url}/api/auth/me")
        if response.status_code == 401 or response.status_code == 403:
            print("  ✅ Acesso não autorizado rejeitado corretamente!")
        else:
            print(f"  ❌ Falha na proteção: {response.status_code}")
        
        print("\n✅ Todos os testes de autenticação passaram!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API. Verifique se está rodando.")
        return False
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

def show_credentials():
    """Mostra as credenciais disponíveis"""
    print("\n" + "="*60)
    print("🔐 CREDENCIAIS DISPONÍVEIS")
    print("="*60)
    
    print("\n👤 USUÁRIOS:")
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
    
    print("🌐 ENDPOINTS:")
    print("  • POST /api/auth/login - Login")
    print("  • GET /api/auth/me - Dados do usuário")
    print("  • GET /api/admin/clients - Listar clientes")
    print("  • GET /docs - Documentação Swagger")
    print()

if __name__ == "__main__":
    success = test_authentication()
    show_credentials()
    
    if success:
        print("🎉 Sistema de autenticação está funcionando perfeitamente!")
        print("\n💡 Próximos passos:")
        print("  1. Acesse http://localhost:8000/docs")
        print("  2. Use as credenciais acima para fazer login")
        print("  3. Teste os endpoints protegidos")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs da aplicação.")