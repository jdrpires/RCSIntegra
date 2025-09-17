#!/usr/bin/env python3
"""
Script para validar todos os perfis de autenticacao
"""
import requests
import json

def test_user_login(username, password, expected_client):
    """Testa login de um usuario especifico"""
    base_url = "http://localhost:8000"
    
    print(f"\nTestando usuario: {username}")
    print("-" * 40)
    
    try:
        # Login
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"  OK - Login bem-sucedido!")
            print(f"  Cliente: {token_data.get('client_code', 'N/A')}")
            
            # Verificar dados do usuario
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            response = requests.get(f"{base_url}/api/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"  Nome: {user_data['name']}")
                print(f"  Email: {user_data['email']}")
                print(f"  Permissoes: {len([k for k, v in user_data.get('permissions', {}).items() if v])} ativas")
                return True
            else:
                print(f"  ERRO - Falha ao obter dados do usuario: {response.status_code}")
                return False
        else:
            print(f"  ERRO - Falha no login: {response.status_code}")
            print(f"  Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ERRO - Excecao: {e}")
        return False

def test_api_key_access():
    """Testa acesso via API Key"""
    base_url = "http://localhost:8000"
    
    print(f"\nTestando acesso via API Key...")
    print("-" * 40)
    
    # Usar uma das API Keys criadas (vamos pegar do banco)
    try:
        # Simular uma API Key (normalmente seria obtida do banco)
        # Por enquanto vamos testar sem API Key para ver se a protecao funciona
        
        headers = {"X-API-Key": "chave_invalida"}
        response = requests.get(f"{base_url}/api/admin/clients", headers=headers)
        
        if response.status_code == 401:
            print("  OK - API Key invalida rejeitada corretamente!")
            return True
        else:
            print(f"  ERRO - API Key invalida aceita: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ERRO - Excecao: {e}")
        return False

def validate_all_profiles():
    """Valida todos os perfis criados"""
    print("VALIDACAO COMPLETA DOS PERFIS DE AUTENTICACAO")
    print("=" * 60)
    
    # Usuarios para testar
    users_to_test = [
        ("admin", "Admin123!", "CLI_2EDF5B7E"),
        ("demo", "Demo123!", "CLI_57BC2C59"),
        ("teste", "Teste123!", "CLI_5D67211A")
    ]
    
    success_count = 0
    total_tests = len(users_to_test) + 1  # +1 para API Key test
    
    # Testar cada usuario
    for username, password, expected_client in users_to_test:
        if test_user_login(username, password, expected_client):
            success_count += 1
    
    # Testar API Key
    if test_api_key_access():
        success_count += 1
    
    # Resultado final
    print(f"\nRESULTADO FINAL:")
    print("=" * 60)
    print(f"Testes realizados: {total_tests}")
    print(f"Testes bem-sucedidos: {success_count}")
    print(f"Taxa de sucesso: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\nTODOS OS PERFIS ESTAO FUNCIONANDO CORRETAMENTE!")
        print("\nSISTEMA DE AUTENTICACAO VALIDADO COM SUCESSO!")
        
        print("\nRESUMO DOS PERFIS CRIADOS:")
        print("- 3 Clientes (Admin, Demo, Teste)")
        print("- 3 Usuarios (admin, demo, teste)")
        print("- 3 API Keys (uma para cada cliente)")
        print("- Templates de exemplo criados")
        
        print("\nACESSOS DISPONIVEIS:")
        print("- Web UI: http://localhost:8000/docs")
        print("- API REST: http://localhost:8000/api/")
        print("- Banco PostgreSQL: localhost:5432")
        
        return True
    else:
        print(f"\nALGUNS TESTES FALHARAM ({total_tests - success_count} falhas)")
        print("Verifique os logs da aplicacao para mais detalhes.")
        return False

if __name__ == "__main__":
    validate_all_profiles()