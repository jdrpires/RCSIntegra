#!/usr/bin/env python3
"""
Script para testar se o token da API RCS está válido
"""
import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_rcs_token():
    """Testa se o token da API RCS está válido"""
    
    base_url = os.getenv("RCS_API_BASE_URL", "https://pointer-rcs-api-node.eugen.com.br")
    token = os.getenv("RCS_API_TOKEN")
    
    print(f"🔍 Testando conectividade com a API RCS...")
    print(f"📡 Base URL: {base_url}")
    print(f"🔑 Token: {token[:20]}..." if token else "❌ Token não encontrado")
    
    if not token:
        print("❌ ERRO: RCS_API_TOKEN não configurado no .env")
        return False
    
    # Headers para autenticação
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Tentar fazer uma requisição simples para testar o token
    # Vamos usar um endpoint que deve retornar erro 400 se o token estiver válido
    # mas os dados estiverem incorretos (melhor que 401/403 para token inválido)
    test_url = f"{base_url}/api/v3/basic"
    
    try:
        print(f"🚀 Fazendo requisição de teste para: {test_url}")
        
        # Payload mínimo inválido para testar autenticação
        test_payload = {
            "account": "test",
            "messages": []
        }
        
        response = requests.post(
            test_url,
            json=test_payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:500]}")
        
        if response.status_code == 401:
            print("❌ ERRO: Token inválido ou expirado (401 Unauthorized)")
            return False
        elif response.status_code == 403:
            print("❌ ERRO: Token sem permissão (403 Forbidden)")
            return False
        elif response.status_code == 400:
            print("✅ Token válido! (400 Bad Request indica que a autenticação passou)")
            return True
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            print("🔍 Verificar se a API está funcionando corretamente")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ ERRO: Timeout na conexão com a API")
        return False
    except requests.exceptions.ConnectionError:
        print("🌐 ERRO: Não foi possível conectar com a API")
        return False
    except Exception as e:
        print(f"💥 ERRO inesperado: {str(e)}")
        return False

def test_alternative_endpoints():
    """Testa endpoints alternativos para validar o token"""
    
    base_url = os.getenv("RCS_API_BASE_URL", "https://pointer-rcs-api-node.eugen.com.br")
    token = os.getenv("RCS_API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Lista de endpoints para testar
    endpoints = [
        "/api/v3/single",
        "/api/v3/webhook",
        "/api/v3/templates",
        "/health",
        "/status"
    ]
    
    print(f"\n🔍 Testando endpoints alternativos...")
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Testando: {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code not in [401, 403]:
                print(f"   ✅ Token aceito em {endpoint}")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE TOKEN DA API RCS")
    print("=" * 60)
    
    result = test_rcs_token()
    
    if result is False:
        print("\n" + "=" * 60)
        print("❌ TOKEN INVÁLIDO OU EXPIRADO")
        print("=" * 60)
        print("📞 Entre em contato com a Eugen:")
        print("   Email: apoio.ca@eugen.com.br")
        print("   Para solicitar um novo token")
        
        # Testar endpoints alternativos
        test_alternative_endpoints()
        
    elif result is True:
        print("\n" + "=" * 60)
        print("✅ TOKEN VÁLIDO!")
        print("=" * 60)
        print("🎉 O token está funcionando corretamente")
        
    else:
        print("\n" + "=" * 60)
        print("⚠️  RESULTADO INCONCLUSIVO")
        print("=" * 60)
        print("🔍 Verificar logs da aplicação para mais detalhes")
