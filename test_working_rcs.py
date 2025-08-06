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
    print("🎯 Testando RCS Single (que está funcionando)\n")
    
    # Teste 1: Mensagem de texto simples
    print("1. Mensagem de texto simples...")
    data = {
        "account": "15885",  # Seu account ID real
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
                "message": "Olá {{nome}}! Teste do gateway {{empresa}} funcionando perfeitamente! 🚀"
            }
        }
    }
    
    await send_and_check(data, "/api/rcs/single", "Texto simples")
    
    # Teste 2: Rich Card
    print("\n2. Rich Card com botões...")
    data = {
        "account": "15885",
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
                "title": "Olá {{nome}}! 👋",
                "description": "Gateway RCS funcionando perfeitamente! Escolha uma opção abaixo:",
                "fileUrl": "https://via.placeholder.com/500x300/4CAF50/FFFFFF?text=RCS+Gateway+OK",
                "suggestions": [
                    {
                        "type": "reply",
                        "title": "✅ Funcionou!",
                        "value": "Gateway funcionando perfeitamente!"
                    },
                    {
                        "type": "reply",
                        "title": "📱 Mais testes",
                        "value": "Quero fazer mais testes"
                    }
                ]
            }
        }
    }
    
    await send_and_check(data, "/api/rcs/single", "Rich Card")
    
    # Teste 3: Carousel
    print("\n3. Carousel de opções...")
    data = {
        "account": "15885",
        "messages": [
            {
                "number": "5516982089942"
            }
        ],
        "content": {
            "carousel": [
                {
                    "title": "🚀 Gateway RCS",
                    "description": "Sistema funcionando perfeitamente!",
                    "fileUrl": "https://via.placeholder.com/500x300/2196F3/FFFFFF?text=Gateway+RCS",
                    "suggestions": [
                        {
                            "type": "reply",
                            "title": "✅ Perfeito",
                            "value": "Gateway funcionando!"
                        }
                    ]
                },
                {
                    "title": "📊 Status API",
                    "description": "Conexão com PontalTech estabelecida!",
                    "fileUrl": "https://via.placeholder.com/500x300/4CAF50/FFFFFF?text=API+OK",
                    "suggestions": [
                        {
                            "type": "reply",
                            "title": "📈 Detalhes",
                            "value": "Quero ver mais detalhes"
                        }
                    ]
                }
            ]
        }
    }
    
    await send_and_check(data, "/api/rcs/single", "Carousel")

async def send_and_check(data, endpoint, test_name):
    """Envia mensagem e verifica resultado"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                result = response.json()
                message_id = result[0]['id']
                status = result[0]['status']
                
                print(f"   ✅ {test_name}: {status}")
                print(f"   📝 ID: {message_id}")
                
                # Verifica status no banco
                status_response = await client.get(f"{BASE_URL}/api/messages/{message_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   📊 Status no banco: {status_data['status']}")
                    if status_data.get('error_message'):
                        print(f"   ❌ Erro: {status_data['error_message']}")
                
            else:
                print(f"   ❌ {test_name}: HTTP {response.status_code}")
                print(f"   📄 Resposta: {response.text}")
                
        except Exception as e:
            print(f"   ❌ {test_name}: {str(e)}")

async def main():
    print("🎉 Teste do RCS Single (Funcionando)\n")
    print("📱 Número de destino: 5516982089942")
    print("🏢 Account: 2992")
    print("🔗 Endpoint: /api/rcs/single")
    print("=" * 50)
    
    await test_working_rcs_single()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    print("📱 Verifique seu celular para as mensagens RCS")
    print("🔍 Monitore os logs do servidor para detalhes")

if __name__ == "__main__":
    asyncio.run(main())
