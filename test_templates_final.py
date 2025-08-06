#!/usr/bin/env python3
"""
Script final para testar templates RCS com todos os campos obrigatórios.
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
TEST_BOT_ID = "bot_test_123"
TEST_WEBHOOK = "https://webhook.exemplo.com/rcs"

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
        },
        {
            "name": f"Template Carousel {datetime.now().strftime('%H%M%S')}",
            "account": TEST_ACCOUNT,
            "content_type": "carousel",
            "template_data": {
                "cards": [
                    {
                        "title": "{{produto1}}",
                        "description": "Produto incrível com desconto especial!",
                        "fileUrl": "https://picsum.photos/400/300?random=1",
                        "suggestions": [
                            {
                                "type": "openUrl",
                                "title": "Comprar",
                                "value": "https://loja.exemplo.com/produto1"
                            }
                        ]
                    },
                    {
                        "title": "{{produto2}}",
                        "description": "Outro produto fantástico em promoção!",
                        "fileUrl": "https://picsum.photos/400/300?random=2",
                        "suggestions": [
                            {
                                "type": "openUrl",
                                "title": "Comprar",
                                "value": "https://loja.exemplo.com/produto2"
                            }
                        ]
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
            print(f"✅ Template criado com sucesso!")
            created.append(template['name'])
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

def send_template_message(template):
    """Envia mensagem usando template."""
    template_id = str(template.get("id"))  # Converter para string
    template_name = template.get("name", "Sem nome")
    
    print(f"\n📤 Enviando template: {template_name} (ID: {template_id})")
    
    payload = {
        "account": TEST_ACCOUNT,
        "webhook": TEST_WEBHOOK,
        "template_id": template_id,
        "bot_id": TEST_BOT_ID,
        "messages": [
            {
                "number": TARGET_PHONE,
                "vars": {
                    "nome": "João Silva",
                    "empresa": "TechStore",
                    "codigo": "ABC123",
                    "produto": "Smartphone XYZ",
                    "produto1": "iPhone 15",
                    "produto2": "Samsung Galaxy S24",
                    "preco": "R$ 1.299,00",
                    "desconto": "25"
                }
            }
        ]
    }
    
    result = make_request("POST", "/api/rcs/template", payload)
    
    if result and isinstance(result, list) and len(result) > 0:
        message_result = result[0]
        if message_result.get("status") == "sent":
            print(f"✅ Template {template_name} enviado com sucesso!")
            print(f"📱 Message ID: {message_result.get('id')}")
            return True
    
    print(f"❌ Falha ao enviar template {template_name}")
    return False

def main():
    """Função principal."""
    print("🚀 Teste Completo de Templates RCS")
    print(f"📱 Número: {TARGET_PHONE}")
    print(f"🏢 Account: {TEST_ACCOUNT}")
    print(f"🤖 Bot ID: {TEST_BOT_ID}")
    print(f"🔗 Webhook: {TEST_WEBHOOK}")
    print(f"🌐 Servidor: {BASE_URL}")
    print(f"🎭 Modo: SIMULAÇÃO ATIVADO")
    
    # Verificar templates existentes
    templates = list_templates()
    
    if not templates:
        print("\n⚠️  Nenhum template encontrado. Criando exemplos...")
        created = create_sample_templates()
        
        if created:
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
        template_name = template.get("name", "Sem nome")
        
        print(f"\n🔄 Processando {i}/{len(templates)}: {template_name}")
        
        success = send_template_message(template)
        results.append({
            "name": template_name,
            "id": template.get("id"),
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
        print(f"\n🎉 {successful} mensagem(s) simuladas para {TARGET_PHONE}!")
        print("🎭 MODO SIMULAÇÃO: As mensagens não foram enviadas realmente")
        print("📊 Verifique os logs do servidor para detalhes da simulação")
    
    if failed > 0:
        print(f"\n⚠️  {failed} template(s) falharam.")

if __name__ == "__main__":
    main()
