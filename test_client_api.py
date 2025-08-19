#!/usr/bin/env python3
"""
Script para testar a API RCS Gateway como cliente
"""
import requests
import json
import time
from datetime import datetime

# Configurações do cliente (dados do banco inicializado)
BASE_URL = "http://localhost:8000"
API_KEY = "jHID31pmJFi97TjO6rQVAzeC6WkZba6TII_Hn1q6nHY"  # Cliente 1
CLIENT_CODE = "CLI_7FB141C8"  # Cliente 1

# Headers para autenticação
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health():
    """Testa se a API está funcionando"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_api_info():
    """Testa informações da API"""
    print("\n📋 Obtendo informações da API...")
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        info = response.json()
        print(f"✅ API Info: {info['name']} v{info['version']}")
        print(f"   📚 Documentação: {BASE_URL}/docs")
        return True
    except Exception as e:
        print(f"❌ Erro ao obter info: {e}")
        return False

def test_send_basic_message():
    """Testa envio de mensagem básica"""
    print("\n📤 Testando envio de mensagem básica...")
    
    payload = {
        "client_code": CLIENT_CODE,
        "user_code": "admin",
        "message_type": "basic",
        "phone_numbers": ["5511999999999"],
        "content": {
            "text": {
                "message": "🚀 Teste da API RCS Gateway! Esta é uma mensagem básica enviada via API."
            }
        },
        "campaign_name": "Teste_API_Cliente",
        "callback_url": "https://webhook.site/unique-id"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/client/send-message",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Mensagem enviada com sucesso!")
            print(f"   📧 Message ID: {result.get('message_id')}")
            print(f"   🆔 Client Message ID: {result.get('client_message_id')}")
            print(f"   📊 Status: {result.get('status')}")
            print(f"   ✉️  Enviadas: {result.get('sent_count')}")
            print(f"   ❌ Falhas: {result.get('failed_count')}")
            return result.get('client_message_id')
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return None

def test_send_rich_card():
    """Testa envio de Rich Card"""
    print("\n🎨 Testando envio de Rich Card...")
    
    payload = {
        "client_code": CLIENT_CODE,
        "user_code": "admin",
        "message_type": "single",
        "phone_numbers": ["5511999999999"],
        "content": {
            "richCard": {
                "title": "🎉 Oferta Especial da API!",
                "description": "Teste do Rich Card via API RCS Gateway. Aproveite esta demonstração de funcionalidade!",
                "fileUrl": "https://via.placeholder.com/800x600/4CAF50/FFFFFF?text=RCS+Gateway+API",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "🌐 Ver Documentação",
                        "value": "http://localhost:8000/docs"
                    },
                    {
                        "type": "reply",
                        "title": "✅ Funcionou!",
                        "value": "O Rich Card funcionou perfeitamente!"
                    },
                    {
                        "type": "reply",
                        "title": "ℹ️ Mais Info",
                        "value": "Quero saber mais sobre a API"
                    }
                ]
            }
        },
        "campaign_name": "Teste_RichCard_API"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/client/send-message",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Rich Card enviado com sucesso!")
            print(f"   📧 Message ID: {result.get('message_id')}")
            print(f"   🆔 Client Message ID: {result.get('client_message_id')}")
            print(f"   📊 Status: {result.get('status')}")
            return result.get('client_message_id')
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao enviar Rich Card: {e}")
        return None

def test_get_messages():
    """Testa consulta de mensagens"""
    print("\n📋 Consultando mensagens enviadas...")
    
    try:
        # Consultar todas as mensagens
        response = requests.get(
            f"{BASE_URL}/api/client/messages",
            headers=HEADERS,
            params={"client_code": CLIENT_CODE, "limit": 10}
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Encontradas {len(messages)} mensagens:")
            
            for i, msg in enumerate(messages[:5], 1):  # Mostrar apenas as 5 primeiras
                print(f"   {i}. ID: {msg.get('client_message_id', 'N/A')}")
                print(f"      📱 Número: {msg.get('phone_number')}")
                print(f"      📊 Status: {msg.get('status')}")
                print(f"      📅 Criada: {msg.get('created_at', '')[:19]}")
                print(f"      🏷️  Campanha: {msg.get('campaign_name', 'N/A')}")
                print()
            
            if len(messages) > 5:
                print(f"   ... e mais {len(messages) - 5} mensagens")
            
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao consultar mensagens: {e}")
        return False

def test_get_stats():
    """Testa consulta de estatísticas"""
    print("\n📊 Consultando estatísticas do cliente...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/client/stats",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estatísticas do cliente:")
            print(f"   🏢 Cliente: {stats.get('client_name')}")
            print(f"   🆔 Código: {stats.get('client_code')}")
            print(f"   📧 Total de mensagens: {stats.get('total_messages')}")
            print(f"   📅 Mensagens hoje: {stats.get('messages_today')}")
            print(f"   🎯 Tipos permitidos: {', '.join(stats.get('allowed_message_types', []))}")
            print(f"   📈 Limite diário: {stats.get('max_messages_per_day')}")
            
            # Mostrar distribuição por status
            by_status = stats.get('messages_by_status', {})
            if by_status:
                print(f"   📊 Por status:")
                for status, count in by_status.items():
                    print(f"      - {status}: {count}")
            
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao consultar estatísticas: {e}")
        return False

def test_invalid_api_key():
    """Testa autenticação com API Key inválida"""
    print("\n🔐 Testando autenticação com API Key inválida...")
    
    invalid_headers = {
        "X-API-Key": "api_key_invalida_123",
        "Content-Type": "application/json"
    }
    
    payload = {
        "client_code": CLIENT_CODE,
        "message_type": "basic",
        "phone_numbers": ["5511999999999"],
        "content": {"text": {"message": "Teste"}}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/client/send-message",
            headers=invalid_headers,
            json=payload
        )
        
        if response.status_code == 401:
            print(f"✅ Autenticação funcionando corretamente (401 Unauthorized)")
            print(f"   📝 Resposta: {response.json().get('detail')}")
            return True
        else:
            print(f"❌ Esperado 401, recebido {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de autenticação: {e}")
        return False

def test_wrong_client_code():
    """Testa com client_code errado"""
    print("\n🚫 Testando com client_code incorreto...")
    
    payload = {
        "client_code": "CLI_WRONG123",  # Client code errado
        "message_type": "basic",
        "phone_numbers": ["5511999999999"],
        "content": {"text": {"message": "Teste"}}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/client/send-message",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 403:
            print(f"✅ Validação de client_code funcionando (403 Forbidden)")
            print(f"   📝 Resposta: {response.json().get('detail')}")
            return True
        else:
            print(f"❌ Esperado 403, recebido {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de client_code: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 RCS Gateway API - Teste como Cliente")
    print("=" * 50)
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"🆔 Client Code: {CLIENT_CODE}")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("API Info", test_api_info),
        ("Envio Mensagem Básica", test_send_basic_message),
        ("Envio Rich Card", test_send_rich_card),
        ("Consulta Mensagens", test_get_messages),
        ("Estatísticas", test_get_stats),
        ("Autenticação Inválida", test_invalid_api_key),
        ("Client Code Errado", test_wrong_client_code),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            # Pequena pausa entre testes
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Erro no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! A API está funcionando perfeitamente.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    print(f"\n📚 Documentação completa: {BASE_URL}/docs")
    print("🔧 Para usar em produção, substitua a BASE_URL e configure suas credenciais.")

if __name__ == "__main__":
    main()
