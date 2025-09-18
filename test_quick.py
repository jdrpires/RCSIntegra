#!/usr/bin/env python3
"""
Script de teste rápido para a API RCS Gateway
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Testa se a API está funcionando"""
    print("🔍 Testando health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_simple_message():
    """Testa envio de mensagem simples"""
    print("\n📱 Testando mensagem simples...")
    
    data = {
        "campaign_name": "Teste API",
        "account": "teste_account",
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
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/rcs/basic", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_rich_card():
    """Testa envio de Rich Card"""
    print("\n🎨 Testando Rich Card...")
    
    data = {
        "account": "teste_account",
        "messages": [
            {
                "number": "5511999999999"
            }
        ],
        "content": {
            "richCard": {
                "title": "Oferta Especial! 🎉",
                "description": "Aproveite 20% de desconto em todos os produtos.",
                "fileUrl": "https://via.placeholder.com/300x200/4CAF50/FFFFFF?text=Oferta+Especial",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Produtos",
                        "value": "https://www.google.com"
                    },
                    {
                        "type": "reply",
                        "title": "Mais Info",
                        "value": "Quero mais informações"
                    }
                ]
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/rcs/single", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_flexible_endpoint():
    """Testa endpoint flexível"""
    print("\n🔄 Testando endpoint flexível...")
    
    data = {
        "phone": "11999999999",
        "message": "Teste do endpoint flexível! 🚀"
    }
    
    response = requests.post(f"{BASE_URL}/api/send", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def list_messages():
    """Lista mensagens enviadas"""
    print("\n📋 Listando mensagens...")
    
    response = requests.get(f"{BASE_URL}/api/messages?limit=5")
    print(f"Status: {response.status_code}")
    messages = response.json()
    print(f"Total de mensagens: {len(messages)}")
    
    for msg in messages:
        print(f"  - ID: {msg['id']}, Status: {msg['status']}, Telefone: {msg['phone_number']}")
    
    return response.status_code == 200

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API RCS Gateway\n")
    
    tests = [
        ("Health Check", test_health),
        ("Mensagem Simples", test_simple_message),
        ("Rich Card", test_rich_card),
        ("Endpoint Flexível", test_flexible_endpoint),
        ("Listar Mensagens", list_messages)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASSOU" if success else "❌ FALHOU"))
        except Exception as e:
            print(f"Erro no teste {test_name}: {e}")
            results.append((test_name, f"❌ ERRO: {e}"))
        
        time.sleep(1)  # Pausa entre testes
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    for test_name, result in results:
        print(f"{result} {test_name}")
    
    print("\n🌐 Acesse a documentação em: http://localhost:8000/docs")
    print("🔍 Health check em: http://localhost:8000/health")

if __name__ == "__main__":
    main()