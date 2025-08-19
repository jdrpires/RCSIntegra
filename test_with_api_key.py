#!/usr/bin/env python3
"""
Script para testar a aplicação RCS Gateway com API Key
"""
import requests
import json

def test_rcs_basic_with_api_key():
    """Testa envio de mensagem RCS Basic com API Key"""
    
    # URL da sua aplicação local
    url = "http://localhost:8000/api/rcs/basic"
    
    # API Key do banco de dados (primeira encontrada)
    api_key = "jHID31pmJFi97TjO6rQVhKJGNqLdWXYZ8aBcEfGhIjKlMnOpQrStUvWxYz"
    
    # Headers com API Key
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Payload de teste
    payload = {
        "campaign_name": "Teste Cliente",
        "account": "sua_conta_id",
        "messages": [
            {
                "number": "5511999999999",
                "vars": {
                    "nome": "João",
                    "produto": "Smartphone"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}, seu {{produto}} está disponível!"
            }
        },
        "callback": "https://seu-dominio.com/callback",
        "fallback": [
            {
                "channel": "SMS",
                "content": "Ola {{nome}}, seu {{produto}} esta disponivel!"
            }
        ]
    }
    
    print("=" * 60)
    print("🧪 TESTE RCS BASIC COM API KEY")
    print("=" * 60)
    print(f"🔗 URL: {url}")
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        print(f"\n🚀 Enviando requisição...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ SUCESSO! Mensagem enviada com sucesso")
            result = response.json()
            if result.get("simulation"):
                print("🎭 Modo simulação ativo - mensagem não foi enviada para API real")
            else:
                print("📱 Mensagem enviada para API RCS real")
        elif response.status_code == 401:
            print("\n❌ ERRO: API Key inválida ou expirada")
            print("💡 Verifique se a API Key está correta")
        elif response.status_code == 403:
            print("\n❌ ERRO: API Key sem permissão")
            print("💡 Verifique se a API Key tem permissão 'send_messages'")
        else:
            print(f"\n⚠️  Status inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n🌐 ERRO: Não foi possível conectar com a aplicação")
        print("💡 Verifique se a aplicação está rodando em http://localhost:8000")
    except requests.exceptions.Timeout:
        print("\n⏰ ERRO: Timeout na requisição")
    except Exception as e:
        print(f"\n💥 ERRO inesperado: {str(e)}")

def test_api_keys_from_db():
    """Testa todas as API Keys do banco de dados"""
    
    from database import get_db
    from auth_models import APIKey
    
    db = next(get_db())
    api_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
    
    print("=" * 60)
    print("🔑 TESTANDO TODAS AS API KEYS DO BANCO")
    print("=" * 60)
    
    for i, key in enumerate(api_keys, 1):
        print(f"\n🧪 Teste {i}/{len(api_keys)}")
        print(f"📝 Nome: {key.key_name}")
        print(f"🔑 Key: {key.api_key[:20]}...")
        print(f"👤 Client ID: {key.client_id}")
        print(f"🔐 Scopes: {key.scopes}")
        
        # Testar esta API Key
        url = "http://localhost:8000/api/rcs/basic"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": key.api_key
        }
        
        payload = {
            "campaign_name": f"Teste {key.key_name}",
            "account": "test_account",
            "messages": [{"number": "5511999999999"}],
            "content": {"text": {"message": "Teste de API Key"}},
            "fallback": [{"channel": "SMS", "content": "Teste"}]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ API Key válida e funcionando!")
            elif response.status_code == 401:
                print("   ❌ API Key inválida")
            elif response.status_code == 403:
                print("   ⚠️  API Key sem permissão")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Erro: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando testes da aplicação RCS Gateway...")
    
    # Primeiro, testar com uma API Key específica
    test_rcs_basic_with_api_key()
    
    print("\n" + "=" * 60)
    
    # Depois, testar todas as API Keys do banco
    test_api_keys_from_db()
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
    print("💡 Se todos os testes falharam, verifique se a aplicação está rodando:")
    print("   python3 main.py")
