#!/usr/bin/env python3
"""
Teste com API real da Eugen
"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_real_api():
    """Testa com API real da Eugen"""
    print("🚀 Testando com API REAL da Eugen\n")
    
    # IMPORTANTE: Use seus dados reais aqui
    real_data = {
        "campaign_name": "Teste Real API",
        "account": "15885",  # ← Substitua pelo seu account ID real
        "messages": [
            {
                "number": "5516982089942",  # ← Seu número real
                "vars": {
                    "nome": "Jean",
                    "produto": "Teste Gateway"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}, teste do gateway RCS para {{produto}}!"
            }
        },
        "callback": "https://webhook.site/unique-id",  # ← Use um webhook real se tiver
        "fallback": [
            {
                "channel": "SMS",
                "content": "Ola {{nome}}, teste do gateway RCS para {{produto}}!"
            }
        ]
    }
    
    print("📤 Enviando mensagem de teste...")
    print(f"📱 Para: {real_data['messages'][0]['number']}")
    print(f"🏢 Account: {real_data['account']}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/rcs/basic", json=real_data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCESSO!")
                print(f"   Status: {result[0]['status']}")
                print(f"   Mensagem: {result[0]['message']}")
                print(f"   ID: {result[0]['id']}")
                print()
                
                # Consulta o status da mensagem
                message_id = result[0]['id']
                print(f"🔍 Consultando status da mensagem {message_id}...")
                
                status_response = await client.get(f"{BASE_URL}/api/messages/{message_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status atual: {status_data['status']}")
                    print(f"   Criada em: {status_data['created_at']}")
                    if status_data.get('sent_at'):
                        print(f"   Enviada em: {status_data['sent_at']}")
                    if status_data.get('error_message'):
                        print(f"   Erro: {status_data['error_message']}")
                
            else:
                print(f"❌ ERRO HTTP {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
    
    print("\n📋 Próximos passos:")
    print("1. Verifique se recebeu a mensagem RCS no celular")
    print("2. Se não recebeu, verifique:")
    print("   - Account ID está correto")
    print("   - Número de telefone está correto")
    print("   - Celular suporta RCS")
    print("3. Monitore os logs do servidor para mais detalhes")

if __name__ == "__main__":
    print("⚠️  ATENÇÃO: Este script usa a API REAL!")
    print("⚠️  Certifique-se de que:")
    print("   - SIMULATION_MODE=False no .env")
    print("   - Account ID está correto")
    print("   - Token está válido")
    print("   - IP foi liberado pela Eugen")
    print()
    
    confirm = input("Deseja continuar? (s/N): ")
    if confirm.lower() == 's':
        asyncio.run(test_real_api())
    else:
        print("Teste cancelado.")
