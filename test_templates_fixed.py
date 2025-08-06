#!/usr/bin/env python3
"""
Script corrigido para testar templates RCS.
"""

import requests
import json
import time
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}
TARGET_PHONE = "5516982089942"
TEST_ACCOUNT = "15885"

def make_request(method, endpoint, data=None):
    """Faz uma requisição HTTP."""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"📤 {method} {endpoint}")
    if data:
        print(f"📋 Payload: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"❌ Erro HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Erro (texto): {response.text}")
            return None
        
        try:
            result = response.json()
            print(f"📄 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        except:
            print(f"📄 Resposta (texto): {response.text}")
            return response.text
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def create_sample_templates():
    """Cria templates de exemplo."""
    print("=" * 70)
    print("📝 Criando Templates de Exemplo")
    print("=" * 70)
    
    templates = [
        {
            "name": f"Template Texto {datetime.now().strftime('%H%M%S')}",
            "account": TEST_ACCOUNT,
            "content_type": "text",
            "template_data": {
                "message": "Olá {{nome}}! Bem-vindo à {{empresa}}. Seu código: {{codigo}}"
            }
        },
        {
            "name": f"Template Rich Card {datetime.now().strftime('%H%M%S')}",
            "account": TEST_ACCOUNT,
            "content_type": "richCard",
            "template_data": {
                "title": "🎉 Oferta para {{nome}}!",
                "description": "{{desconto}}% OFF em {{produto}} por {{preco}}!",
                "fileUrl": "https://picsum.photos/600/400",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Produto",
                        "value": "https://exemplo.com/produto"
                    },
                    {
                        "type": "call",
                        "title": "Ligar",
                        "value": "1140001234"
                    }
                ]
            }
        }
    ]
    
    created = []
    for template in templates:
        print(f"\n📝 Criando: {template['name']}")
        result = make_request("POST", "/api/rcs/templates", template)
        
        if result and result.get("success"):
            template_id = result.get("template_id")
            print(f"✅ Template criado com ID: {template_id}")
            created.append(template_id)
        else:
            print("❌ Falha ao criar template")
        
        time.sleep(1)
    
    return created

def list_templates():
    """Lista todos os templates."""
    print("=" * 70)
    print("📋 Listando Templates")
    print("=" * 70)
    
    result = make_request("GET", "/api/templates")
    return result if result else []

def send_template_message(template_id):
    """Envia mensagem usando template."""
    print(f"\n📤 Enviando template ID: {template_id}")
    
    payload = {
        "account": TEST_ACCOUNT,
        "template_id": template_id,
        "messages": [
            {
                "number": TARGET_PHONE,
                "vars": {
                    "nome": "João Silva",
                    "empresa": "TechStore",
                    "codigo": "ABC123",
                    "produto": "Smartphone XYZ",
                    "preco": "R$ 1.299,00",
                    "desconto": "25"
                }
            }
        ]
    }
    
    result = make_request("POST", "/api/rcs/template", payload)
    
    if result and result.get("success"):
        print(f"✅ Template {template_id} enviado com sucesso!")
        return True
    else:
        print(f"❌ Falha ao enviar template {template_id}")
        return False

def main():
    """Função principal."""
    print("🚀 Teste de Templates RCS")
    print(f"📱 Número: {TARGET_PHONE}")
    print(f"🏢 Account: {TEST_ACCOUNT}")
    print(f"🌐 Servidor: {BASE_URL}")
    
    # Verificar templates existentes
    templates = list_templates()
    
    if not templates:
        print("\n⚠️  Nenhum template encontrado. Criando exemplos...")
        created_ids = create_sample_templates()
        
        if created_ids:
            print("\n🔄 Buscando templates novamente...")
            time.sleep(2)
            templates = list_templates()
    
    if not templates:
        print("❌ Não foi possível encontrar templates")
        return
    
    print(f"\n📊 Encontrados {len(templates)} template(s)")
    
    # Enviar cada template
    results = []
    for i, template in enumerate(templates, 1):
        template_id = template.get("id")
        template_name = template.get("name", "Sem nome")
        
        print(f"\n🔄 Processando {i}/{len(templates)}: {template_name}")
        
        success = send_template_message(template_id)
        results.append({
            "name": template_name,
            "id": template_id,
            "success": success
        })
        
        if i < len(templates):
            print("⏳ Aguardando 3 segundos...")
            time.sleep(3)
    
    # Relatório final
    print("=" * 70)
    print("📊 RELATÓRIO FINAL")
    print("=" * 70)
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"📱 Número: {TARGET_PHONE}")
    print(f"📝 Templates: {len(results)}")
    print(f"✅ Sucessos: {successful}")
    print(f"❌ Falhas: {failed}")
    print(f"📈 Taxa de sucesso: {(successful/len(results)*100):.1f}%")
    
    print(f"\n📋 Detalhes:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['name']} (ID: {result['id']})")
    
    if successful > 0:
        print(f"\n🎉 {successful} mensagem(s) enviadas para {TARGET_PHONE}!")

if __name__ == "__main__":
    main()
