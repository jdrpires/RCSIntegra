#!/usr/bin/env python3
"""
Teste apenas de mensagens básicas RCS
"""

import requests
import json

BASE_URL = "http://localhost:8000"
TARGET_PHONE = "5516982089942"
TEST_ACCOUNT = "15886"

def test_basic_messages():
    """Testa apenas mensagens básicas"""
    print("Teste de Mensagens Basicas RCS")
    print(f"Numero: {TARGET_PHONE}")
    print(f"Account: {TEST_ACCOUNT}")
    print("=" * 50)
    
    # Teste 1: Mensagem de texto simples
    print("\n1. Mensagem de texto simples...")
    payload = {
        "campaign_name": "Teste Basico",
        "account": TEST_ACCOUNT,
        "messages": [
            {
                "number": TARGET_PHONE,
                "vars": {
                    "nome": "Jean Pires",
                    "empresa": "RCS Integra"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Ola {{nome}}! Gateway {{empresa}} funcionando!"
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/rcs/basic", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result and len(result) > 0:
        message_id = result[0].get("id")
        status = result[0].get("status")
        print(f"Mensagem ID: {message_id}, Status: {status}")
        
        # Verificar detalhes da mensagem
        detail_response = requests.get(f"{BASE_URL}/api/messages/{message_id}")
        if detail_response.status_code == 200:
            detail = detail_response.json()
            print(f"Status no banco: {detail.get('status')}")
            if detail.get('error_message'):
                print(f"Erro: {detail.get('error_message')}")
    
    print("\n" + "=" * 50)
    print("Teste concluido!")

if __name__ == "__main__":
    test_basic_messages()