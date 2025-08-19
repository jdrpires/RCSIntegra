#!/usr/bin/env python3
"""
Teste RCS Single usando template da plataforma Eugen
"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_rcs_single_with_template():
    """Testa RCS Single usando template_id da plataforma"""
    print("🎯 Testando RCS Single com Template da Plataforma\n")
    
    # IMPORTANTE: Substitua pelo template_id real da sua conta Eugen
    template_tests = [
        {
            "name": "Template Básico",
            "template_id": "SEU_TEMPLATE_ID_AQUI",  # ← Substitua pelo ID real
            "vars": {
                "nome": "Jean",
                "empresa": "RCS Integra",
                "produto": "Gateway RCS"
            }
        },
        {
            "name": "Template com Variáveis Específicas",
            "template_id": "OUTRO_TEMPLATE_ID",  # ← Se tiver outro template
            "vars": {
                "cliente": "Jean Pires",
                "valor": "R$ 99,90",
                "data": "31/07/2025"
            }
        }
    ]
    
    for i, test in enumerate(template_tests, 1):
        print(f"{i}. Testando {test['name']}...")
        
        # Dados para RCS Single com template
        data = {
            "account": "2992",  # Seu account ID
            "template_id": test["template_id"],
            "messages": [
                {
                    "number": "5516982089942",
                    "vars": test["vars"]
                }
            ]
            # Nota: Quando usa template_id, NÃO precisa do campo "content"
        }
        
        await send_template_message(data, test["name"])
        print()

async def test_rcs_single_template_with_content():
    """Testa RCS Single com template_id E content personalizado"""
    print("🔄 Testando Template + Content Personalizado\n")
    
    # Algumas APIs permitem sobrescrever o template com content personalizado
    data = {
        "account": "2992",
        "template_id": "SEU_TEMPLATE_ID_AQUI",  # ← Substitua pelo ID real
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Jean",
                    "status": "funcionando"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}! O gateway está {{status}} com templates! 🎉"
            }
        }
    }
    
    await send_template_message(data, "Template + Content Override")

async def send_template_message(data, test_name):
    """Envia mensagem com template e verifica resultado"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"   📤 Enviando: {test_name}")
            print(f"   🆔 Template ID: {data.get('template_id', 'N/A')}")
            print(f"   📱 Para: {data['messages'][0]['number']}")
            print(f"   🔧 Variáveis: {data['messages'][0].get('vars', {})}")
            
            response = await client.post(f"{BASE_URL}/api/rcs/single", json=data)
            
            if response.status_code == 200:
                result = response.json()
                message_id = result[0]['id']
                status = result[0]['status']
                
                print(f"   ✅ Status: {status}")
                print(f"   📝 Message ID: {message_id}")
                
                # Verifica detalhes no banco
                status_response = await client.get(f"{BASE_URL}/api/messages/{message_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   📊 Status no banco: {status_data['status']}")
                    print(f"   🕐 Criado em: {status_data['created_at']}")
                    if status_data.get('sent_at'):
                        print(f"   📨 Enviado em: {status_data['sent_at']}")
                    if status_data.get('error_message'):
                        print(f"   ❌ Erro: {status_data['error_message']}")
                
            else:
                print(f"   ❌ Erro HTTP {response.status_code}")
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"   📄 Resposta: {error_data}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {str(e)}")

async def list_available_templates():
    """Lista templates disponíveis no banco local"""
    print("📋 Templates Salvos Localmente:")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/templates")
            if response.status_code == 200:
                templates = response.json()
                if templates:
                    for template in templates:
                        print(f"   🆔 ID: {template['template_id']}")
                        print(f"   📝 Nome: {template['name']}")
                        print(f"   📊 Tipo: {template['content_type']}")
                        print(f"   🏢 Account: {template['account']}")
                        print(f"   📅 Criado: {template['created_at']}")
                        print("   " + "-" * 40)
                else:
                    print("   ℹ️  Nenhum template salvo localmente ainda")
            else:
                print(f"   ❌ Erro ao listar templates: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

async def main():
    print("🎯 Teste RCS Single com Templates da Plataforma")
    print("=" * 60)
    
    # Lista templates salvos localmente
    await list_available_templates()
    print()
    
    print("⚠️  IMPORTANTE:")
    print("   1. Você precisa ter templates criados na plataforma Eugen")
    print("   2. Substitua 'SEU_TEMPLATE_ID_AQUI' pelos IDs reais")
    print("   3. Acesse a plataforma Eugen para ver seus template_ids")
    print("   4. As variáveis devem corresponder às definidas no template")
    print()
    
    confirm = input("Você já configurou os template_ids reais? (s/N): ")
    if confirm.lower() != 's':
        print("\n📋 Próximos passos:")
        print("1. Acesse a plataforma Eugen")
        print("2. Vá na seção de Templates")
        print("3. Copie os IDs dos templates que quer usar")
        print("4. Edite o arquivo test_rcs_template.py")
        print("5. Substitua 'SEU_TEMPLATE_ID_AQUI' pelos IDs reais")
        print("6. Execute novamente este script")
        return
    
    print("🚀 Iniciando testes com templates...")
    print("=" * 60)
    
    # Executa os testes
    await test_rcs_single_with_template()
    await test_rcs_single_template_with_content()
    
    print("=" * 60)
    print("✅ Testes concluídos!")
    print("📱 Verifique seu celular para as mensagens RCS")
    print("🔍 Monitore os logs do servidor para detalhes")

if __name__ == "__main__":
    asyncio.run(main())
