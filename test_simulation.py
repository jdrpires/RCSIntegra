#!/usr/bin/env python3
"""
Script para testar o gateway em modo simulação
"""

import os
import asyncio
import httpx

# Configura modo simulação
os.environ["SIMULATION_MODE"] = "True"

BASE_URL = "http://localhost:8000"

async def test_simulation_mode():
    """Testa o gateway em modo simulação"""
    print("🧪 Testando Gateway RCS em Modo Simulação\n")
    
    # Teste 1: Mensagem básica
    print("1. Testando mensagem básica...")
    data = {
        "campaign_name": "Teste Simulação",
        "account": "test_account",
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
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/api/rcs/basic", json=data)
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Resposta: {result[0]['status']}")
            print(f"✅ Mensagem: {result[0]['message']}\n")
        except Exception as e:
            print(f"❌ Erro: {str(e)}\n")
    
    # Teste 2: Rich Card
    print("2. Testando Rich Card...")
    data = {
        "account": "test_account",
        "messages": [{"number": "5511999999999"}],
        "content": {
            "richCard": {
                "title": "Oferta Especial!",
                "description": "Aproveite 20% de desconto.",
                "fileUrl": "https://exemplo.com/promocao.jpg",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Produtos",
                        "value": "https://loja.exemplo.com"
                    }
                ]
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/api/rcs/single", json=data)
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Resposta: {result[0]['status']}")
            print(f"✅ Mensagem: {result[0]['message']}\n")
        except Exception as e:
            print(f"❌ Erro: {str(e)}\n")
    
    # Teste 3: Consultar mensagens
    print("3. Consultando mensagens enviadas...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/messages")
            messages = response.json()
            print(f"✅ Total de mensagens: {len(messages)}")
            for msg in messages[-2:]:  # Últimas 2 mensagens
                print(f"   - ID: {msg['id']}, Status: {msg['status']}, Número: {msg['phone_number']}")
            print()
        except Exception as e:
            print(f"❌ Erro: {str(e)}\n")
    
    print("🎉 Teste em modo simulação concluído!")
    print("\n📋 Próximos passos:")
    print("1. Entre em contato com apoio.ca@eugen.com.br")
    print("2. Solicite liberação do IP: 200.170.180.129")
    print("3. Solicite token Bearer válido")
    print("4. Configure SIMULATION_MODE=False no .env")

if __name__ == "__main__":
    asyncio.run(test_simulation_mode())
