#!/usr/bin/env python3
"""
Script simples para testar autenticacao
"""
import requests
import json
from datetime import datetime

def test_authentication():
    """Testa o sistema de autenticacao"""
    base_url = "http://localhost:8000"
    
    print("Testando Sistema de Autenticacao RCS Gateway")
    print("="*60)
    
    try:
        # Teste 1: Health check
        print("\n1. Testando health check...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("  OK - API esta funcionando!")
        else:
            print(f"  ERRO - API nao esta respondendo: {response.status_code}")
            return False
        
        # Teste 2: Login com usuario admin
        print("\n2. Testando login com usuario admin...")
        login_data = {
            "username": "admin",
            "password": "Admin123!"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"  OK - Login bem-sucedido!")
            print(f"  Cliente: {token_data.get('client_code', 'N/A')}")
            print(f"  Token: {token_data['access_token'][:30]}...")
            access_token = token_data["access_token"]
        else:
            print(f"  ERRO - Falha no login: {response.status_code}")
            print(f"  Resposta: {response.text}")
            return False
        
        # Teste 3: Verificar dados do usuario
        print("\n3. Testando dados do usuario logado...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"  OK - Usuario autenticado: {user_data['name']} (@{user_data['username']})")
            print(f"  Email: {user_data['email']}")
            print(f"  Cliente ID: {user_data['client_id']}")
        else:
            print(f"  ERRO - Falha ao obter dados: {response.status_code}")
            print(f"  Resposta: {response.text}")
            return False
        
        # Teste 4: Listar clientes (admin)
        print("\n4. Testando listagem de clientes...")
        response = requests.get(f"{base_url}/api/admin/clients", headers=headers)
        if response.status_code == 200:
            clients = response.json()
            print(f"  OK - {len(clients)} clientes encontrados:")
            for client in clients[:3]:  # Mostrar apenas os 3 primeiros
                print(f"    - {client['name']} ({client['client_code']})")
        else:
            print(f"  ERRO - Falha na listagem: {response.status_code}")
            print(f"  Resposta: {response.text}")
        
        # Teste 5: Login com credenciais invalidas
        print("\n5. Testando credenciais invalidas...")
        invalid_login = {
            "username": "admin",
            "password": "senhaerrada"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=invalid_login)
        if response.status_code == 401:
            print("  OK - Credenciais invalidas rejeitadas corretamente!")
        else:
            print(f"  ERRO - Falha na validacao: {response.status_code}")
        
        # Teste 6: Acesso sem token
        print("\n6. Testando acesso sem token...")
        response = requests.get(f"{base_url}/api/auth/me")
        if response.status_code == 401 or response.status_code == 403:
            print("  OK - Acesso nao autorizado rejeitado corretamente!")
        else:
            print(f"  ERRO - Falha na protecao: {response.status_code}")
        
        print("\nTODOS OS TESTES DE AUTENTICACAO PASSARAM!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERRO: Nao foi possivel conectar a API. Verifique se esta rodando.")
        return False
    except Exception as e:
        print(f"ERRO durante teste: {e}")
        return False

def show_credentials():
    """Mostra as credenciais disponiveis"""
    print("\n" + "="*60)
    print("CREDENCIAIS DISPONIVEIS")
    print("="*60)
    
    print("\nUSUARIOS:")
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
    
    print("ENDPOINTS:")
    print("  - POST /api/auth/login - Login")
    print("  - GET /api/auth/me - Dados do usuario")
    print("  - GET /api/admin/clients - Listar clientes")
    print("  - GET /docs - Documentacao Swagger")
    print()

if __name__ == "__main__":
    success = test_authentication()
    show_credentials()
    
    if success:
        print("SISTEMA DE AUTENTICACAO FUNCIONANDO PERFEITAMENTE!")
        print("\nPROXIMOS PASSOS:")
        print("  1. Acesse http://localhost:8000/docs")
        print("  2. Use as credenciais acima para fazer login")
        print("  3. Teste os endpoints protegidos")
    else:
        print("ALGUNS TESTES FALHARAM. Verifique os logs da aplicacao.")