#!/usr/bin/env python3
"""
Teste simples para verificar se a API está funcionando.
"""

import requests
import json

def test_api():
    """Testa a API básica."""
    
    # Teste health check
    print("Testando health check...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Teste envio de mensagem
    print("\nTestando envio de mensagem...")
    payload = {
        "campaign_name": "Teste Simples",
        "account": "15886",
        "messages": [
            {
                "number": "5516982089942",
                "vars": {"nome": "JEAN PIRES"}
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}!"
            }
        }
    }
    
    response = requests.post(
        "http://localhost:8000/api/rcs/basic",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Teste listagem de mensagens
    print("\nTestando listagem de mensagens...")
    response = requests.get("http://localhost:8000/api/messages")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_api()