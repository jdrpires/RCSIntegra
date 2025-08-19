#!/usr/bin/env python3
"""
Script para capturar e analisar como o cliente está fazendo as requisições
"""
import requests
import json

def test_client_request_formats():
    """Testa diferentes formatos que o cliente pode estar usando"""
    
    print("=" * 60)
    print("🔍 CAPTURANDO FORMATO DE REQUISIÇÃO DO CLIENTE")
    print("=" * 60)
    
    # Formatos típicos que clientes usam
    client_formats = [
        {
            "name": "Formato Simples",
            "data": {
                "phone": "11999999999",
                "message": "Olá, esta é uma mensagem de teste"
            }
        },
        {
            "name": "Formato com Template",
            "data": {
                "to": "11999999999",
                "template": "welcome",
                "variables": {
                    "name": "João",
                    "product": "Smartphone"
                }
            }
        },
        {
            "name": "Formato Padrão RCS",
            "data": {
                "campaign_name": "Teste",
                "account": "cliente_account",
                "messages": [{"number": "5511999999999"}],
                "content": {"text": {"message": "Teste"}},
                "fallback": [{"channel": "SMS", "content": "Teste"}]
            }
        },
        {
            "name": "Formato WhatsApp-like",
            "data": {
                "number": "5511999999999",
                "text": "Mensagem de teste",
                "type": "text"
            }
        },
        {
            "name": "Formato Telegram-like",
            "data": {
                "chat_id": "5511999999999",
                "text": "Mensagem de teste"
            }
        }
    ]
    
    api_key = "jHID31pmJFi97TjO6rQVhKJGNqLdWXYZ8aBcEfGhIjKlMnOpQrStUvWxYz"
    
    for format_test in client_formats:
        print(f"\n📱 Testando: {format_test['name']}")
        print(f"📦 Payload: {json.dumps(format_test['data'], indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/rcs/basic",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": api_key
                },
                json=format_test['data'],
                timeout=10
            )
            
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
            if response.status_code == 401:
                print("❌ ESTE É O ERRO 'API Key inválida ou expirada'!")
            elif response.status_code == 422:
                print("⚠️  Erro de validação - formato não suportado")
            elif response.status_code == 200:
                print("✅ Formato aceito!")
                
        except Exception as e:
            print(f"💥 Erro: {e}")

def show_client_instructions():
    """Mostra instruções para o cliente"""
    
    print(f"\n" + "=" * 60)
    print("📋 COMO O CLIENTE DEVE CHAMAR A API")
    print("=" * 60)
    
    print("🔑 Headers obrigatórios:")
    print("   Content-Type: application/json")
    print("   X-API-Key: SUA_API_KEY_AQUI")
    
    print("\n📦 Payload mínimo:")
    example = {
        "campaign_name": "Nome da Campanha",
        "account": "sua_conta_eugen",
        "messages": [
            {
                "number": "5511999999999",
                "vars": {
                    "nome": "Cliente",
                    "produto": "Produto"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}, seu {{produto}} está disponível!"
            }
        },
        "fallback": [
            {
                "channel": "SMS",
                "content": "Ola {{nome}}, seu {{produto}} esta disponivel!"
            }
        ]
    }
    
    print(json.dumps(example, indent=2, ensure_ascii=False))
    
    print(f"\n💡 Se o cliente está usando formato diferente:")
    print("   1. Capture o formato exato que ele está usando")
    print("   2. Criaremos um mapeamento automático")
    print("   3. A API aceitará o formato do cliente")

if __name__ == "__main__":
    test_client_request_formats()
    show_client_instructions()
    
    print(f"\n" + "=" * 60)
    print("🤝 PRÓXIMOS PASSOS")
    print("=" * 60)
    print("1. Mostre para o cliente como fazer a requisição")
    print("2. Se ele disser que não funciona, capture o formato exato")
    print("3. Criaremos um endpoint personalizado para ele")
    print("4. Exemplo de curl para testar:")
    print()
    print("curl -X POST http://localhost:8000/api/rcs/basic \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -H 'X-API-Key: jHID31pmJFi97TjO6rQVhKJGNqLdWXYZ8aBcEfGhIjKlMnOpQrStUvWxYz' \\")
    print("  -d '{")
    print('    "campaign_name": "Teste Cliente",')
    print('    "account": "2992",')
    print('    "messages": [{"number": "5511999999999"}],')
    print('    "content": {"text": {"message": "Teste"}},')
    print('    "fallback": [{"channel": "SMS", "content": "Teste"}]')
    print("  }'")
