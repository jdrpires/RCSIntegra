#!/usr/bin/env python3
"""
Exemplos de testes manuais para o RCS Gateway.
Execute este arquivo para testar manualmente os endpoints.

IMPORTANTE: Configure seu token RCS no arquivo .env antes de executar!
"""

import requests
import json
import time
from datetime import datetime

# Configuração base
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Dados de teste - AJUSTE CONFORME NECESSÁRIO
TEST_ACCOUNT = "sua_conta_teste"
TEST_PHONE = "5511999999999"  # Substitua por um número real para teste
CALLBACK_URL = "https://webhook.site/unique-id"  # Use webhook.site para testes

def print_separator(title):
    """Imprime um separador visual."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def make_request(method, endpoint, data=None):
    """Faz uma requisição HTTP e exibe o resultado."""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"📤 {method} {endpoint}")
    if data:
        print(f"📋 Payload: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        
        print(f"📥 Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"📄 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        except:
            print(f"📄 Resposta (texto): {response.text}")
            return response.text
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def test_rcs_basic():
    """Teste do endpoint RCS Basic."""
    print_separator("Teste RCS Basic - Mensagem Simples")
    
    payload = {
        "campaign_name": "Teste Manual Basic",
        "account": TEST_ACCOUNT,
        "messages": [
            {
                "number": TEST_PHONE,
                "vars": {
                    "nome": "João Teste",
                    "produto": "Smartphone XYZ"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}, seu {{produto}} está disponível para retirada!"
            }
        },
        "callback": CALLBACK_URL,
        "fallback": [
            {
                "channel": "SMS",
                "content": "Ola {{nome}}, seu {{produto}} esta disponivel!"
            }
        ]
    }
    
    return make_request("POST", "/api/rcs/basic", payload)

def test_rcs_single_rich_card():
    """Teste do endpoint RCS Single com Rich Card."""
    print_separator("Teste RCS Single - Rich Card")
    
    payload = {
        "account": TEST_ACCOUNT,
        "messages": [
            {
                "number": TEST_PHONE
            }
        ],
        "content": {
            "richCard": {
                "title": "🎉 Oferta Especial!",
                "description": "Aproveite 50% de desconto em todos os produtos até o final do mês!",
                "fileUrl": "https://picsum.photos/800/600",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Produtos",
                        "value": "https://www.google.com"
                    },
                    {
                        "type": "call",
                        "title": "Ligar Agora",
                        "value": "1140001234"
                    },
                    {
                        "type": "reply",
                        "title": "Tenho Interesse",
                        "value": "interesse"
                    }
                ]
            }
        }
    }
    
    return make_request("POST", "/api/rcs/single", payload)

def test_rcs_single_carousel():
    """Teste do endpoint RCS Single com Carousel."""
    print_separator("Teste RCS Single - Carousel")
    
    payload = {
        "account": TEST_ACCOUNT,
        "messages": [
            {
                "number": TEST_PHONE
            }
        ],
        "content": {
            "carousel": {
                "cards": [
                    {
                        "title": "📱 iPhone 15",
                        "description": "O mais novo iPhone com tecnologia avançada",
                        "fileUrl": "https://picsum.photos/400/300?random=1",
                        "suggestions": [
                            {
                                "type": "openUrl",
                                "title": "Comprar",
                                "value": "https://www.apple.com"
                            }
                        ]
                    },
                    {
                        "title": "💻 MacBook Pro",
                        "description": "Notebook profissional para desenvolvedores",
                        "fileUrl": "https://picsum.photos/400/300?random=2",
                        "suggestions": [
                            {
                                "type": "openUrl",
                                "title": "Comprar",
                                "value": "https://www.apple.com"
                            }
                        ]
                    },
                    {
                        "title": "⌚ Apple Watch",
                        "description": "Smartwatch com monitoramento de saúde",
                        "fileUrl": "https://picsum.photos/400/300?random=3",
                        "suggestions": [
                            {
                                "type": "openUrl",
                                "title": "Comprar",
                                "value": "https://www.apple.com"
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    return make_request("POST", "/api/rcs/single", payload)

def test_rcs_webhook():
    """Teste do endpoint RCS Webhook."""
    print_separator("Teste RCS Webhook - Conversacional")
    
    payload = {
        "account": TEST_ACCOUNT,
        "webhook": CALLBACK_URL,
        "messages": [
            {
                "number": TEST_PHONE
            }
        ],
        "content": {
            "suggestion": {
                "message": "👋 Olá! Como posso ajudá-lo hoje?",
                "suggestions": [
                    {
                        "type": "reply",
                        "title": "🛒 Produtos",
                        "value": "produtos"
                    },
                    {
                        "type": "reply",
                        "title": "📞 Suporte",
                        "value": "suporte"
                    },
                    {
                        "type": "reply",
                        "title": "💰 Preços",
                        "value": "precos"
                    },
                    {
                        "type": "openUrl",
                        "title": "🌐 Site",
                        "value": "https://www.google.com"
                    }
                ]
            }
        }
    }
    
    return make_request("POST", "/api/rcs/webhook", payload)

def test_create_template():
    """Teste de criação de template."""
    print_separator("Teste Criação de Template")
    
    payload = {
        "name": f"Template Teste Manual {datetime.now().strftime('%H%M%S')}",
        "account": TEST_ACCOUNT,
        "content_type": "richCard",
        "template_data": {
            "title": "Bem-vindo {{nome}}! 🎉",
            "description": "Obrigado por se cadastrar em nossa plataforma. Aproveite {{desconto}}% de desconto na primeira compra!",
            "fileUrl": "https://picsum.photos/600/400",
            "suggestions": [
                {
                    "type": "openUrl",
                    "title": "Explorar Produtos",
                    "value": "https://loja.exemplo.com/{{categoria}}"
                },
                {
                    "type": "reply",
                    "title": "Usar Desconto",
                    "value": "usar_desconto"
                }
            ]
        }
    }
    
    result = make_request("POST", "/api/rcs/templates", payload)
    return result.get("template_id") if result else None

def test_use_template(template_id):
    """Teste de uso de template."""
    if not template_id:
        print("❌ Template ID não fornecido")
        return
        
    print_separator("Teste Uso de Template")
    
    payload = {
        "account": TEST_ACCOUNT,
        "template_id": template_id,
        "messages": [
            {
                "number": TEST_PHONE,
                "vars": {
                    "nome": "Maria Silva",
                    "desconto": "25",
                    "categoria": "smartphones"
                }
            }
        ]
    }
    
    return make_request("POST", "/api/rcs/template", payload)

def test_list_templates():
    """Teste de listagem de templates."""
    print_separator("Teste Listagem de Templates")
    
    return make_request("GET", f"/api/rcs/templates?account={TEST_ACCOUNT}")

def test_list_messages():
    """Teste de listagem de mensagens."""
    print_separator("Teste Listagem de Mensagens")
    
    return make_request("GET", "/api/messages?limit=10")

def test_health_check():
    """Teste de health check."""
    print_separator("Teste Health Check")
    
    return make_request("GET", "/health")

def main():
    """Função principal para executar todos os testes."""
    print("🚀 Iniciando testes manuais do RCS Gateway")
    print(f"📍 URL Base: {BASE_URL}")
    print(f"📱 Telefone de teste: {TEST_PHONE}")
    print(f"🏢 Conta de teste: {TEST_ACCOUNT}")
    print(f"🔗 Callback URL: {CALLBACK_URL}")
    
    print("\n⚠️  IMPORTANTE:")
    print("1. Certifique-se de que o servidor está rodando (python main.py)")
    print("2. Configure seu token RCS no arquivo .env")
    print("3. Substitua TEST_PHONE por um número real")
    print("4. Use webhook.site para testar callbacks")
    
    input("\n🔄 Pressione Enter para continuar...")
    
    # Executar testes
    tests_results = []
    
    # Health check
    result = test_health_check()
    tests_results.append(("Health Check", result is not None))
    
    # RCS Basic
    result = test_rcs_basic()
    tests_results.append(("RCS Basic", result and result.get("success")))
    time.sleep(2)
    
    # RCS Single - Rich Card
    result = test_rcs_single_rich_card()
    tests_results.append(("RCS Single Rich Card", result and result.get("success")))
    time.sleep(2)
    
    # RCS Single - Carousel
    result = test_rcs_single_carousel()
    tests_results.append(("RCS Single Carousel", result and result.get("success")))
    time.sleep(2)
    
    # RCS Webhook
    result = test_rcs_webhook()
    tests_results.append(("RCS Webhook", result and result.get("success")))
    time.sleep(2)
    
    # Templates
    template_id = test_create_template()
    tests_results.append(("Criar Template", template_id is not None))
    time.sleep(1)
    
    if template_id:
        result = test_use_template(template_id)
        tests_results.append(("Usar Template", result and result.get("success")))
        time.sleep(2)
    
    # Listagens
    result = test_list_templates()
    tests_results.append(("Listar Templates", result is not None))
    
    result = test_list_messages()
    tests_results.append(("Listar Mensagens", result is not None))
    
    # Relatório final
    print_separator("RELATÓRIO FINAL")
    
    passed = 0
    failed = 0
    
    for test_name, success in tests_results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Resumo:")
    print(f"✅ Testes que passaram: {passed}")
    print(f"❌ Testes que falharam: {failed}")
    print(f"📈 Taxa de sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 Todos os testes passaram! O RCS Gateway está funcionando corretamente.")
    else:
        print(f"\n⚠️  {failed} teste(s) falharam. Verifique a configuração e logs do servidor.")

if __name__ == "__main__":
    main()
