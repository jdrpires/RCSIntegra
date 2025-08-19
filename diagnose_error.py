#!/usr/bin/env python3
"""
Script para diagnosticar erros na aplicação RCS Gateway
"""
import requests
import json
from database import get_db
from auth_models import APIKey, Client

def test_all_scenarios():
    """Testa todos os cenários possíveis de erro"""
    
    print("=" * 60)
    print("🔍 DIAGNÓSTICO COMPLETO DE ERROS")
    print("=" * 60)
    
    # 1. Testar sem API Key
    print("\n1️⃣ Testando SEM API Key...")
    try:
        response = requests.post(
            "http://localhost:8000/api/rcs/basic",
            json={"test": "data"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 2. Testar com API Key inválida
    print("\n2️⃣ Testando com API Key INVÁLIDA...")
    try:
        response = requests.post(
            "http://localhost:8000/api/rcs/basic",
            headers={"X-API-Key": "chave_invalida_123"},
            json={"test": "data"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 3. Buscar API Keys válidas do banco
    print("\n3️⃣ Buscando API Keys válidas do banco...")
    try:
        db = next(get_db())
        api_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
        
        for i, key in enumerate(api_keys, 1):
            print(f"\n   API Key {i}:")
            print(f"   Nome: {key.key_name}")
            print(f"   Key: {key.api_key[:20]}...")
            print(f"   Client ID: {key.client_id}")
            print(f"   Scopes: {key.scopes}")
            print(f"   Ativa: {key.is_active}")
            
            # Testar esta API Key
            print(f"   🧪 Testando API Key {i}...")
            try:
                response = requests.post(
                    "http://localhost:8000/api/rcs/basic",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": key.api_key
                    },
                    json={
                        "campaign_name": f"Teste {key.key_name}",
                        "account": "test_account",
                        "messages": [{"number": "5511999999999"}],
                        "content": {"text": {"message": "Teste"}},
                        "fallback": [{"channel": "SMS", "content": "Teste"}]
                    },
                    timeout=10
                )
                
                print(f"   ✅ Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                elif response.status_code == 401:
                    print(f"   ❌ ERRO 401: {response.text}")
                    print("   💡 Esta é a mensagem 'API Key inválida ou expirada'")
                else:
                    print(f"   📄 Response: {response.text}")
                    
            except Exception as e:
                print(f"   💥 Erro na requisição: {e}")
                
    except Exception as e:
        print(f"   💥 Erro ao acessar banco: {e}")
    
    # 4. Testar endpoints de documentação
    print("\n4️⃣ Testando endpoints de documentação...")
    endpoints = ["/", "/health", "/docs", "/openapi.json"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            print(f"   {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Erro - {e}")
    
    # 5. Verificar logs recentes
    print("\n5️⃣ Verificando logs recentes...")
    try:
        with open("/Users/jeanpires/GitHub/RCSIntegra/server.log", "r") as f:
            lines = f.readlines()
            print("   Últimas 10 linhas do log:")
            for line in lines[-10:]:
                print(f"   {line.strip()}")
    except Exception as e:
        print(f"   Erro ao ler logs: {e}")

def test_specific_client_request():
    """Testa uma requisição específica como um cliente faria"""
    
    print("\n" + "=" * 60)
    print("🎯 TESTE ESPECÍFICO COMO CLIENTE")
    print("=" * 60)
    
    # Payload típico de cliente
    payload = {
        "campaign_name": "Campanha Cliente",
        "account": "sua_conta_eugen",  # Conta que o cliente deveria usar
        "messages": [
            {
                "number": "5511999999999",
                "vars": {
                    "nome": "Cliente",
                    "produto": "Teste"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}, teste do {{produto}}!"
            }
        },
        "callback": "https://webhook.site/unique-id",
        "fallback": [
            {
                "channel": "SMS",
                "content": "Ola {{nome}}, teste do {{produto}}!"
            }
        ]
    }
    
    # Buscar primeira API Key ativa
    try:
        db = next(get_db())
        api_key = db.query(APIKey).filter(APIKey.is_active == True).first()
        
        if not api_key:
            print("❌ Nenhuma API Key ativa encontrada!")
            return
        
        print(f"🔑 Usando API Key: {api_key.key_name}")
        print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            "http://localhost:8000/api/rcs/basic",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key.api_key
            },
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 401:
            print("\n❌ ESTE É O ERRO 'API Key inválida ou expirada'!")
            print("🔍 Possíveis causas:")
            print("   1. API Key expirou")
            print("   2. API Key foi desativada")
            print("   3. Cliente não tem permissão")
            print("   4. Erro no sistema de autenticação")
        elif response.status_code == 200:
            print("\n✅ Requisição processada com sucesso!")
        else:
            print(f"\n⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Erro: {e}")

if __name__ == "__main__":
    test_all_scenarios()
    test_specific_client_request()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)
    print("💡 Se você ainda está vendo 'API Key inválida ou expirada':")
    print("   1. Verifique se está usando a API Key correta")
    print("   2. Verifique se a API Key não expirou")
    print("   3. Verifique se o cliente está ativo")
    print("   4. Entre em contato com apoio.ca@eugen.com.br")
