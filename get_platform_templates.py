#!/usr/bin/env python3
"""
Script para listar templates disponíveis na plataforma Eugen
"""

import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def get_platform_templates():
    """Tenta listar templates da plataforma Eugen"""
    
    base_url = os.getenv("RCS_API_BASE_URL", "https://pointer-rcs-api-node.eugen.com.br")
    token = os.getenv("RCS_API_TOKEN")
    
    if not token:
        print("❌ RCS_API_TOKEN não configurado!")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Possíveis endpoints para listar templates
    endpoints_to_try = [
        "/api/v3/templates",
        "/api/templates",
        "/templates",
        "/api/v3/template/list",
        "/api/template/list"
    ]
    
    print("🔍 Tentando encontrar endpoint para listar templates...")
    print(f"🌐 Base URL: {base_url}")
    print(f"🔑 Token: {token[:20]}...")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints_to_try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Testando: {endpoint}")
            
            try:
                # Tenta GET
                response = await client.get(url, headers=headers)
                print(f"   GET {response.status_code}: {response.text[:100]}...")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("   ✅ SUCESSO! Templates encontrados:")
                        print(f"   📄 Resposta: {data}")
                        return data
                    except:
                        print("   ⚠️  Resposta não é JSON válido")
                
                # Se GET não funcionar, tenta POST
                if response.status_code in [404, 405]:
                    post_response = await client.post(url, headers=headers, json={})
                    print(f"   POST {post_response.status_code}: {post_response.text[:100]}...")
                    
                    if post_response.status_code == 200:
                        try:
                            data = post_response.json()
                            print("   ✅ SUCESSO com POST! Templates encontrados:")
                            print(f"   📄 Resposta: {data}")
                            return data
                        except:
                            print("   ⚠️  Resposta POST não é JSON válido")
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
            
            print()
    
    print("❌ Não foi possível encontrar endpoint para listar templates")
    print("\n📋 Alternativas:")
    print("1. Acesse a plataforma Eugen via web")
    print("2. Vá na seção de Templates/Modelos")
    print("3. Copie os IDs dos templates manualmente")
    print("4. Entre em contato com apoio.ca@eugen.com.br")

async def test_account_info():
    """Testa endpoint para informações da conta"""
    
    base_url = os.getenv("RCS_API_BASE_URL")
    token = os.getenv("RCS_API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Endpoints para informações da conta
    account_endpoints = [
        "/api/v3/account",
        "/api/account",
        "/account",
        "/api/v3/account/info",
        "/api/account/templates"
    ]
    
    print("🏢 Testando endpoints de informações da conta...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in account_endpoints:
            url = f"{base_url}{endpoint}"
            print(f"📡 Testando: {endpoint}")
            
            try:
                response = await client.get(url, headers=headers)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("   ✅ SUCESSO!")
                        print(f"   📄 Dados da conta: {data}")
                        return data
                    except:
                        print(f"   📄 Resposta: {response.text}")
                else:
                    print(f"   📄 Erro: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
            
            print()

async def main():
    print("🎯 Buscando Templates da Plataforma Eugen")
    print("=" * 60)
    
    # Tenta listar templates
    await get_platform_templates()
    
    print("\n" + "=" * 60)
    
    # Tenta informações da conta
    await test_account_info()
    
    print("\n📋 Próximos passos:")
    print("1. Se encontrou templates, use os IDs nos testes")
    print("2. Se não encontrou, acesse a plataforma web da Eugen")
    print("3. Copie os template_ids manualmente")
    print("4. Use o script test_template_direct.py para testar")

if __name__ == "__main__":
    asyncio.run(main())
