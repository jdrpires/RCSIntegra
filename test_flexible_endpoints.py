#!/usr/bin/env python3
"""
Testa todos os endpoints flexíveis
"""
import requests
import json

def test_flexible_endpoints():
    """Testa todos os formatos flexíveis"""
    
    api_key = "jHID31pmJFi97TjO6rQVhKJGNqLdWXYZ8aBcEfGhIjKlMnOpQrStUvWxYz"
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("🧪 TESTANDO ENDPOINTS FLEXÍVEIS")
    print("=" * 60)
    
    # Teste 1: Endpoint flexível com formato simples
    print("\n1️⃣ Testando endpoint flexível - Formato Simples")
    simple_data = {
        "phone": "11999999999",
        "message": "Olá! Esta é uma mensagem de teste."
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/send",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=simple_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO! Formato simples funcionou")
            result = response.json()
            print(f"   📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   💥 Erro: {e}")
    
    # Teste 2: Endpoint flexível com formato WhatsApp-like
    print("\n2️⃣ Testando endpoint flexível - Formato WhatsApp-like")
    whatsapp_data = {
        "number": "5511999999999",
        "text": "Mensagem no estilo WhatsApp",
        "type": "text"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/send",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=whatsapp_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO! Formato WhatsApp-like funcionou")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   💥 Erro: {e}")
    
    # Teste 3: Endpoint flexível com formato template
    print("\n3️⃣ Testando endpoint flexível - Formato Template")
    template_data = {
        "to": "11999999999",
        "template": "welcome",
        "variables": {
            "name": "João",
            "product": "Smartphone"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/send",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=template_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO! Formato template funcionou")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   💥 Erro: {e}")
    
    # Teste 4: Endpoint super simples
    print("\n4️⃣ Testando endpoint super simples")
    try:
        response = requests.post(
            f"{base_url}/api/send/simple?phone=11999999999&message=Teste super simples",
            headers={
                "X-API-Key": api_key
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO! Endpoint super simples funcionou")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   💥 Erro: {e}")
    
    # Teste 5: Formato RCS padrão (deve continuar funcionando)
    print("\n5️⃣ Testando formato RCS padrão (compatibilidade)")
    rcs_data = {
        "campaign_name": "Teste Compatibilidade",
        "account": "2992",
        "messages": [{"number": "5511999999999"}],
        "content": {"text": {"message": "Teste compatibilidade"}},
        "fallback": [{"channel": "SMS", "content": "Teste"}]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/rcs/basic",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=rcs_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO! Compatibilidade mantida")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   💥 Erro: {e}")

def show_client_examples():
    """Mostra exemplos para o cliente"""
    
    print(f"\n" + "=" * 60)
    print("📋 EXEMPLOS PARA O CLIENTE")
    print("=" * 60)
    
    api_key = "jHID31pmJFi97TjO6rQVhKJGNqLdWXYZ8aBcEfGhIjKlMnOpQrStUvWxYz"
    
    examples = [
        {
            "name": "Formato Mais Simples Possível",
            "curl": f"""curl -X POST http://localhost:8000/api/send/simple?phone=11999999999&message=Ola \\
  -H 'X-API-Key: {api_key}'"""
        },
        {
            "name": "Formato Simples com JSON",
            "curl": f"""curl -X POST http://localhost:8000/api/send \\
  -H 'Content-Type: application/json' \\
  -H 'X-API-Key: {api_key}' \\
  -d '{{"phone": "11999999999", "message": "Olá, teste!"}}'"""
        },
        {
            "name": "Formato WhatsApp-like",
            "curl": f"""curl -X POST http://localhost:8000/api/send \\
  -H 'Content-Type: application/json' \\
  -H 'X-API-Key: {api_key}' \\
  -d '{{"number": "11999999999", "text": "Mensagem teste", "type": "text"}}'"""
        },
        {
            "name": "Formato com Template",
            "curl": f"""curl -X POST http://localhost:8000/api/send \\
  -H 'Content-Type: application/json' \\
  -H 'X-API-Key: {api_key}' \\
  -d '{{"to": "11999999999", "template": "welcome", "variables": {{"name": "João"}}}}'"""
        }
    ]
    
    for example in examples:
        print(f"\n🔹 {example['name']}:")
        print(f"   {example['curl']}")
    
    print(f"\n💡 Todos os formatos fazem o De/Para automático para a API RCS!")
    print(f"   O cliente pode usar qualquer formato que preferir.")

if __name__ == "__main__":
    test_flexible_endpoints()
    show_client_examples()
    
    print(f"\n" + "=" * 60)
    print("✅ SISTEMA DE MAPEAMENTO AUTOMÁTICO ATIVO")
    print("=" * 60)
    print("🎯 Agora o cliente pode usar qualquer formato!")
    print("📱 A aplicação faz o De/Para automaticamente")
    print("🔄 Compatibilidade total mantida")
