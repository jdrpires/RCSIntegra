#!/usr/bin/env python3
"""
Script para buscar e testar templates diretamente da plataforma Eugen
"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def list_platform_templates():
    """Lista todos os templates disponíveis na plataforma"""
    print("🔍 Buscando templates na plataforma Eugen...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/platform/templates")
            
            if response.status_code == 200:
                templates_data = response.json()
                print("✅ Templates encontrados na plataforma!")
                
                # Diferentes formatos possíveis de resposta
                templates = []
                if isinstance(templates_data, dict):
                    if 'templates' in templates_data:
                        templates = templates_data['templates']
                    elif 'data' in templates_data:
                        templates = templates_data['data']
                    else:
                        templates = [templates_data]
                elif isinstance(templates_data, list):
                    templates = templates_data
                
                if templates:
                    print(f"\n📋 {len(templates)} template(s) disponível(is):")
                    print("=" * 60)
                    
                    for i, template in enumerate(templates, 1):
                        template_id = template.get('id', template.get('template_id', 'N/A'))
                        name = template.get('name', template.get('title', 'Sem nome'))
                        template_type = template.get('type', template.get('content_type', 'N/A'))
                        
                        print(f"{i}. 🆔 ID: {template_id}")
                        print(f"   📝 Nome: {name}")
                        print(f"   📊 Tipo: {template_type}")
                        
                        if template.get('created_at'):
                            print(f"   📅 Criado: {template['created_at']}")
                        
                        print("   " + "-" * 40)
                    
                    return templates
                else:
                    print("ℹ️  Nenhum template encontrado na resposta")
                    print(f"📄 Resposta completa: {templates_data}")
                    return []
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📄 Erro: {error_data}")
                except:
                    print(f"📄 Resposta: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Erro ao buscar templates: {str(e)}")
            return []

async def get_template_details(template_id: str):
    """Busca detalhes de um template específico"""
    print(f"\n🔍 Buscando detalhes do template: {template_id}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/platform/templates/{template_id}")
            
            if response.status_code == 200:
                template = response.json()
                print("✅ Detalhes do template:")
                print(f"   🆔 ID: {template.get('id', template_id)}")
                print(f"   📝 Nome: {template.get('name', 'N/A')}")
                print(f"   📊 Tipo: {template.get('type', 'N/A')}")
                
                if template.get('variables'):
                    print(f"   🔧 Variáveis: {template['variables']}")
                
                if template.get('content'):
                    print(f"   📄 Conteúdo: {json.dumps(template['content'], indent=2, ensure_ascii=False)}")
                
                return template
            else:
                print(f"❌ Template não encontrado (HTTP {response.status_code})")
                try:
                    error_data = response.json()
                    print(f"📄 Erro: {error_data}")
                except:
                    print(f"📄 Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar template: {str(e)}")
            return None

async def test_template_message(template_id: str, variables: dict = None):
    """Testa envio de mensagem com template"""
    print(f"\n📤 Testando envio com template: {template_id}")
    
    # Variáveis padrão se não fornecidas
    if not variables:
        variables = {
            "nome": "Jean",
            "empresa": "RCS Integra",
            "produto": "Gateway RCS",
            "valor": "R$ 99,90",
            "data": "31/07/2025",
            "cliente": "Jean Pires"
        }
    
    data = {
        "account": "15886",  # Seu account ID
        "template_id": template_id,
        "messages": [
            {
                "number": "5516982089942",
                "vars": variables
            }
        ]
    }
    
    print(f"📱 Para: {data['messages'][0]['number']}")
    print(f"🔧 Variáveis: {variables}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/rcs/single", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Mensagem enviada com sucesso!")
                print(f"📝 Message ID: {result[0]['id']}")
                print(f"📊 Status: {result[0]['status']}")
                return result[0]
            else:
                print(f"❌ Erro ao enviar (HTTP {response.status_code})")
                try:
                    error_data = response.json()
                    print(f"📄 Erro: {error_data}")
                except:
                    print(f"📄 Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {str(e)}")
            return None

async def interactive_template_browser():
    """Interface interativa para navegar e testar templates"""
    print("🎯 Navegador Interativo de Templates da Plataforma")
    print("=" * 60)
    
    # Lista templates disponíveis
    templates = await list_platform_templates()
    
    if not templates:
        print("\n❌ Nenhum template encontrado. Verifique:")
        print("1. Se o servidor está rodando")
        print("2. Se o token está válido")
        print("3. Se há templates criados na plataforma")
        return
    
    while True:
        print("\n🎛️  Opções:")
        print("1. 📋 Listar templates novamente")
        print("2. 🔍 Ver detalhes de um template")
        print("3. 📤 Testar envio com template")
        print("4. 🚪 Sair")
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            templates = await list_platform_templates()
        
        elif choice == "2":
            template_id = input("Digite o ID do template: ").strip()
            if template_id:
                await get_template_details(template_id)
        
        elif choice == "3":
            template_id = input("Digite o ID do template para testar: ").strip()
            if template_id:
                print("\n🔧 Variáveis personalizadas (deixe vazio para usar padrão):")
                custom_vars = {}
                
                var_input = input("nome: ").strip()
                if var_input:
                    custom_vars["nome"] = var_input
                
                var_input = input("empresa: ").strip()
                if var_input:
                    custom_vars["empresa"] = var_input
                
                var_input = input("produto: ").strip()
                if var_input:
                    custom_vars["produto"] = var_input
                
                await test_template_message(template_id, custom_vars if custom_vars else None)
        
        elif choice == "4":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")

async def main():
    print("🎯 Buscar Templates da Plataforma Eugen")
    print("=" * 60)
    
    mode = input("Escolha o modo:\n1. 🤖 Automático (lista e testa)\n2. 🎛️  Interativo\nOpção (1-2): ").strip()
    
    if mode == "2":
        await interactive_template_browser()
    else:
        # Modo automático
        templates = await list_platform_templates()
        
        if templates and len(templates) > 0:
            # Pega o primeiro template para teste
            first_template = templates[0]
            template_id = first_template.get('id', first_template.get('template_id'))
            
            if template_id:
                print(f"\n🧪 Testando automaticamente o primeiro template: {template_id}")
                await get_template_details(template_id)
                await test_template_message(template_id)

if __name__ == "__main__":
    asyncio.run(main())
