#!/usr/bin/env python3
"""
Teste focado no RCS Single que está funcionando
"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_working_rcs_single():
    """Testa RCS Single que está funcionando"""
    print("Testando RCS Single (que esta funcionando)\n")
    
    # Teste 1: Mensagem de texto simples
    print("1. Mensagem de texto simples...")
    data = {
        "account": "15886",
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Jean",
                    "empresa": "RCS Integra"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Ola {{nome}}! Teste do gateway {{empresa}} funcionando perfeitamente!"
            }
        }
    }
    
    await send_and_check(data, "/api/rcs/single", "Texto simples")
    
    # Teste 2: Rich Card
    print("\n2. Rich Card com botoes...")
    data = {
        "account": "15886",
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Jean"
                }
            }
        ],
        "content": {
            "richCard": {
                "title": "Ola {{nome}}!",
                "description": "Gateway RCS funcionando perfeitamente! Escolha uma opcao abaixo:",
                "fileUrl": "https://via.placeholder.com/500x300/4CAF50/FFFFFF?text=RCS+Gateway+OK",
                "suggestions": [
                    {
                        "type": "reply",
                        "title": "Funcionou!",
                        "value": "Gateway funcionando perfeitamente!"
                    },
                    {
                        "type": "reply",
                        "title": "Mais testes",
                        "value": "Quero fazer mais testes"
                    }
                ]
            }
        }
    }
    
    await send_and_check(data, "/api/rcs/single", "Rich Card")

async def send_and_check(data, endpoint, test_name):
    """Envia mensagem e verifica resultado"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                result = response.json()
                message_id = result[0]['id']
                status = result[0]['status']
                
                print(f"   OK {test_name}: {status}")
                print(f"   ID: {message_id}")
                
                # Verifica status no banco
                status_response = await client.get(f"{BASE_URL}/api/messages/{message_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status no banco: {status_data['status']}")
                    if status_data.get('error_message'):
                        print(f"   Erro: {status_data['error_message']}")
                
            else:
                print(f"   ERRO {test_name}: HTTP {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except Exception as e:
            print(f"   ERRO {test_name}: {str(e)}")

async def main():
    print("Teste do RCS Single (Funcionando)\n")
    print("Numero de destino: 5516982089942")
    print("Account: 15886")
    print("Endpoint: /api/rcs/single")
    print("=" * 50)
    
    await test_working_rcs_single()
    
    print("\n" + "=" * 50)
    print("Testes concluidos!")
    print("Verifique seu celular para as mensagens RCS")
    print("Monitore os logs do servidor para detalhes")

if __name__ == "__main__":
    asyncio.run(main())