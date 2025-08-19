#!/usr/bin/env python3
"""
Teste direto e rápido com template_id
"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def quick_template_test():
    """Teste rápido com template"""
    
    # CONFIGURE AQUI:
    TEMPLATE_ID = input("Digite o template_id da plataforma Eugen: ").strip()
    
    if not TEMPLATE_ID:
        print("❌ Template ID é obrigatório!")
        return
    
    print(f"\n🎯 Testando template: {TEMPLATE_ID}")
    
    # Dados mínimos para teste
    data = {
        "account": "15885",
        "template_id": TEMPLATE_ID,
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Jean",
                    "empresa": "RCS Integra",
                    "produto": "Gateway",
                    "valor": "R$ 99,90",
                    "data": "31/07/2025",
                    "cliente": "Jean Pires"
                }
            }
        ]
    }
    
    print("📤 Enviando mensagem...")
    print(f"📱 Para: {data['messages'][0]['number']}")
    print(f"🔧 Variáveis: {data['messages'][0]['vars']}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/rcs/single", json=data)
            
            print(f"\n📊 Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCESSO!")
                print(f"📝 Message ID: {result[0]['id']}")
                print(f"📊 Status: {result[0]['status']}")
                print(f"💬 Mensagem: {result[0]['message']}")
                
                # Consulta detalhes
                message_id = result[0]['id']
                detail_response = await client.get(f"{BASE_URL}/api/messages/{message_id}")
                if detail_response.status_code == 200:
                    details = detail_response.json()
                    print(f"🏢 Account: {details['account']}")
                    print(f"🆔 Template ID usado: {details.get('template_id', 'N/A')}")
                    print(f"📅 Criado: {details['created_at']}")
                
            else:
                print("❌ ERRO!")
                try:
                    error_data = response.json()
                    print(f"📄 Erro: {error_data}")
                except:
                    print(f"📄 Resposta: {response.text}")
                    
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")
    
    print("\n🎉 Teste concluído!")
    print("📱 Verifique seu celular para a mensagem RCS")

if __name__ == "__main__":
    print("🚀 Teste Rápido - RCS Single com Template")
    print("=" * 50)
    print("ℹ️  Este teste usa um template_id da plataforma Eugen")
    print("ℹ️  O template deve estar criado na sua conta")
    print()
    
    asyncio.run(quick_template_test())
