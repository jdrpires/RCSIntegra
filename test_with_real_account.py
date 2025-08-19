#!/usr/bin/env python3
"""
Script para testar com conta real da Eugen
"""
import requests
import json

def test_with_real_account():
    """Testa com diferentes formatos de conta"""
    
    print("=" * 60)
    print("🧪 TESTE COM CONTAS REAIS DA PONTALTECH")
    print("=" * 60)
    
    # API Key válida
    api_key = "jHID31pmJFi97TjO6rQVhKJGNqLdWXYZ8aBcEfGhIjKlMnOpQrStUvWxYz"
    
    # Diferentes formatos de conta para testar
    accounts_to_test = [
        "2992",  # Formato numérico simples
        "account_2992",  # Com prefixo
        "pontal_2992",  # Com prefixo pontal
        "rcs_2992",  # Com prefixo rcs
        "client_2992",  # Com prefixo client
    ]
    
    for account in accounts_to_test:
        print(f"\n🔍 Testando conta: {account}")
        
        payload = {
            "campaign_name": "Teste Conta",
            "account": account,
            "messages": [{"number": "5511999999999"}],
            "content": {"text": {"message": "Teste"}},
            "fallback": [{"channel": "SMS", "content": "Teste"}]
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/api/rcs/basic",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": api_key
                },
                json=payload,
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message_status = result[0].get("status", "unknown")
                
                if message_status == "sent" or message_status == "pending":
                    print(f"   ✅ SUCESSO! Conta válida: {account}")
                    print(f"   📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    break
                elif "account does not exists" in result[0].get("message", ""):
                    print(f"   ❌ Conta não existe: {account}")
                else:
                    print(f"   ⚠️  Status: {message_status}")
                    print(f"   📄 Message: {result[0].get('message', 'N/A')}")
            else:
                print(f"   ❌ Erro HTTP: {response.text}")
                
        except Exception as e:
            print(f"   💥 Erro: {e}")
    
    print(f"\n" + "=" * 60)
    print("💡 INSTRUÇÕES PARA O CLIENTE:")
    print("=" * 60)
    print("1. Entre em contato com apoio.ca@eugen.com.br")
    print("2. Solicite o ID da sua conta RCS")
    print("3. Use esse ID no campo 'account' das requisições")
    print("4. Exemplo de requisição correta:")
    print(json.dumps({
        "campaign_name": "Minha Campanha",
        "account": "SEU_ID_CONTA_AQUI",  # ← ID fornecido pela Eugen
        "messages": [{"number": "5511999999999"}],
        "content": {"text": {"message": "Sua mensagem"}},
        "fallback": [{"channel": "SMS", "content": "Sua mensagem"}]
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_with_real_account()
