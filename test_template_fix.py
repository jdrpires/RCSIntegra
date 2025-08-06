#!/usr/bin/env python3
"""
Teste rápido para verificar se a correção do template funcionou
"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def test_template_fix():
    """Testa se a correção do template funcionou"""
    
    print("🔧 Testando correção do template...")
    
    # Dados de teste
    data = {
        "account": "15885",  # Seu account real
        "template_id": "teste_operadoras",  # Template que você testou
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Jean",
                    "empresa": "RCS Integra"
                }
            }
        ]
    }
    
    print(f"📤 Enviando para template: {data['template_id']}")
    print(f"📱 Número: {data['messages'][0]['number']}")
    print(f"🏢 Account: {data['account']}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/rcs/single", json=data)
            
            print(f"\n📊 Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCESSO! Correção funcionou!")
                print(f"📝 Message ID: {result[0]['id']}")
                print(f"📊 Status: {result[0]['status']}")
                
                # Verifica no banco
                message_id = result[0]['id']
                detail_response = await client.get(f"{BASE_URL}/api/messages/{message_id}")
                if detail_response.status_code == 200:
                    details = detail_response.json()
                    print(f"🆔 Template ID salvo: {details.get('template_id')}")
                    print(f"📅 Criado em: {details['created_at']}")
                    print(f"📊 Status no banco: {details['status']}")
                    
                    if details.get('error_message'):
                        print(f"❌ Erro: {details['error_message']}")
                    else:
                        print("✅ Sem erros no banco!")
                
            else:
                print("❌ Ainda há erro:")
                try:
                    error_data = response.json()
                    print(f"📄 Erro: {error_data}")
                except:
                    print(f"📄 Resposta: {response.text}")
                    
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")

if __name__ == "__main__":
    print("🔧 Teste da Correção do Template")
    print("=" * 40)
    
    asyncio.run(test_template_fix())
