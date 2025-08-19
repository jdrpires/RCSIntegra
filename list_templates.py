#!/usr/bin/env python3
"""
Script simples para listar templates da plataforma
"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def simple_list_templates():
    """Lista templates de forma simples"""
    print("🔍 Buscando templates na plataforma Eugen...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/platform/templates")
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Resposta da API:")
                print(f"📄 {data}")
                
                # Tenta extrair templates
                templates = []
                if isinstance(data, dict):
                    if 'templates' in data:
                        templates = data['templates']
                    elif 'data' in data:
                        templates = data['data']
                elif isinstance(data, list):
                    templates = data
                
                if templates:
                    print(f"\n📋 {len(templates)} template(s) encontrado(s):")
                    for template in templates:
                        template_id = template.get('id', template.get('template_id', 'N/A'))
                        name = template.get('name', 'Sem nome')
                        print(f"   🆔 {template_id} - {name}")
                else:
                    print("ℹ️  Estrutura de resposta não reconhecida")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    asyncio.run(simple_list_templates())
