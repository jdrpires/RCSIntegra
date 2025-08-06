#!/usr/bin/env python3
"""
Teste para buscar todos os templates e enviar uma mensagem de cada para um número específico.
Este script é útil para testar todos os templates existentes de uma vez.

IMPORTANTE: Configure seu token RCS no arquivo .env antes de executar!
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuração
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}
TARGET_PHONE = "5516982089942"  # Número de destino
TEST_ACCOUNT = "15886"  # Ajuste conforme necessário

def print_separator(title):
    """Imprime um separador visual."""
    print(f"\n{'='*70}")
    print(f"📱 {title}")
    print(f"{'='*70}")

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

def get_all_templates():
    """Busca todos os templates disponíveis."""
    print_separator("Buscando Todos os Templates")
    
    # Primeiro, tentar buscar sem filtro de account
    result = make_request("GET", "/api/rcs/templates")
    
    if result is None:
        # Se falhar, tentar com account específico
        print("🔄 Tentando com account específico...")
        result = make_request("GET", f"/api/rcs/templates?account={TEST_ACCOUNT}")
    
    return result if result else []

def generate_sample_vars_for_template(template_data, template_name):
    """Gera variáveis de exemplo baseadas no template."""
    # Variáveis comuns que podem aparecer em templates
    common_vars = {
        "nome": "João Silva",
        "produto": "Smartphone XYZ",
        "preco": "R$ 1.299,00",
        "desconto": "25",
        "empresa": "TechStore",
        "data": datetime.now().strftime("%d/%m/%Y"),
        "hora": datetime.now().strftime("%H:%M"),
        "codigo": "ABC123",
        "quantidade": "3",
        "categoria": "smartphones",
        "produto_id": "prod123",
        "produto1_nome": "iPhone 15",
        "produto1_desc": "Smartphone Apple mais recente",
        "produto1_img": "iphone15.jpg",
        "produto1_id": "iphone15",
        "produto2_nome": "Samsung Galaxy S24",
        "produto2_desc": "Smartphone Samsung flagship",
        "produto2_img": "galaxy-s24.jpg",
        "produto2_id": "galaxy-s24",
        "link": "https://www.google.com",
        "telefone": "11999999999",
        "email": "contato@exemplo.com"
    }
    
    # Converter template_data para string para buscar variáveis
    template_str = json.dumps(template_data, ensure_ascii=False)
    
    # Encontrar todas as variáveis {{variavel}} no template
    import re
    variables = re.findall(r'\{\{(\w+)\}\}', template_str)
    
    # Criar dicionário com as variáveis encontradas
    vars_dict = {}
    for var in set(variables):  # usar set para remover duplicatas
        if var in common_vars:
            vars_dict[var] = common_vars[var]
        else:
            # Se não temos uma variável comum, criar um valor genérico
            vars_dict[var] = f"Valor_{var}"
    
    print(f"🔧 Variáveis detectadas no template '{template_name}': {list(vars_dict.keys())}")
    return vars_dict

def send_template_message(template):
    """Envia uma mensagem usando um template específico."""
    template_id = template.get("id")
    template_name = template.get("name", "Template sem nome")
    template_data = template.get("template_data", {})
    account = template.get("account", TEST_ACCOUNT)
    
    print_separator(f"Enviando Template: {template_name}")
    
    # Gerar variáveis de exemplo baseadas no template
    sample_vars = generate_sample_vars_for_template(template_data, template_name)
    
    payload = {
        "account": account,
        "template_id": template_id,
        "messages": [
            {
                "number": TARGET_PHONE,
                "vars": sample_vars
            }
        ]
    }
    
    print(f"📋 Template ID: {template_id}")
    print(f"📋 Template Name: {template_name}")
    print(f"📋 Account: {account}")
    print(f"📋 Variáveis: {json.dumps(sample_vars, indent=2, ensure_ascii=False)}")
    
    result = make_request("POST", "/api/rcs/template", payload)
    
    if result and result.get("success"):
        print(f"✅ Template '{template_name}' enviado com sucesso!")
        return True
    else:
        print(f"❌ Falha ao enviar template '{template_name}'")
        return False

def create_sample_templates_if_none():
    """Cria templates de exemplo se não houver nenhum."""
    print_separator("Criando Templates de Exemplo")
    
    sample_templates = [
        {
            "name": f"Template Texto Exemplo {datetime.now().strftime('%H%M%S')}",
            "account": TEST_ACCOUNT,
            "content_type": "text",
            "template_data": {
                "message": "Olá {{nome}}! Bem-vindo à {{empresa}}. Seu código de acesso é: {{codigo}}"
            }
        },
        {
            "name": f"Template Rich Card Exemplo {datetime.now().strftime('%H%M%S')}",
            "account": TEST_ACCOUNT,
            "content_type": "richCard",
            "template_data": {
                "title": "🎉 Oferta Especial para {{nome}}!",
                "description": "{{desconto}}% de desconto em {{produto}} por apenas {{preco}}!",
                "fileUrl": "https://picsum.photos/600/400",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Produto",
                        "value": "https://loja.exemplo.com/{{produto_id}}"
                    },
                    {
                        "type": "call",
                        "title": "Ligar",
                        "value": "1140001234"
                    },
                    {
                        "type": "reply",
                        "title": "Tenho Interesse",
                        "value": "interesse"
                    }
                ]
            }
        },
        {
            "name": f"Template Carousel Exemplo {datetime.now().strftime('%H%M%S')}",
            "account": TEST_ACCOUNT,
            "content_type": "carousel",
            "template_data": {
                "cards": [
                    {
                        "title": "{{produto1_nome}}",
                        "description": "{{produto1_desc}}",
                        "fileUrl": "https://picsum.photos/400/300?random=1",
                        "suggestions": [
                            {
                                "type": "openUrl",
                                "title": "Comprar",
                                "value": "https://loja.exemplo.com/{{produto1_id}}"
                            }
                        ]
                    },
                    {
                        "title": "{{produto2_nome}}",
                        "description": "{{produto2_desc}}",
                        "fileUrl": "https://picsum.photos/400/300?random=2",
                        "suggestions": [
                            {
                                "type": "openUrl",
                                "title": "Comprar",
                                "value": "https://loja.exemplo.com/{{produto2_id}}"
                            }
                        ]
                    }
                ]
            }
        }
    ]
    
    created_templates = []
    for template_data in sample_templates:
        print(f"📝 Criando template: {template_data['name']}")
        result = make_request("POST", "/api/rcs/templates", template_data)
        
        if result and result.get("success"):
            print(f"✅ Template criado com ID: {result.get('template_id')}")
            created_templates.append(result.get("template_id"))
        else:
            print(f"❌ Falha ao criar template")
        
        time.sleep(1)  # Pequena pausa entre criações
    
    return created_templates

def test_server_connection():
    """Testa se o servidor está rodando."""
    print_separator("Testando Conexão com o Servidor")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando e acessível")
            return True
        else:
            print(f"⚠️  Servidor respondeu com status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Não foi possível conectar ao servidor: {e}")
        print("💡 Certifique-se de que o servidor está rodando com: python main.py")
        return False

def main():
    """Função principal."""
    print("🚀 Teste de Envio de Todos os Templates")
    print(f"📱 Número de destino: {TARGET_PHONE}")
    print(f"🏢 Account: {TEST_ACCOUNT}")
    print(f"🌐 Servidor: {BASE_URL}")
    
    print("\n⚠️  IMPORTANTE:")
    print("1. Certifique-se de que o servidor está rodando (python main.py)")
    print("2. Configure seu token RCS no arquivo .env")
    print("3. O número de destino deve ser válido e capaz de receber RCS")
    print("4. Este teste enviará uma mensagem para cada template encontrado")
    
    # Confirmar execução
    confirm = input(f"\n🔄 Deseja continuar e enviar mensagens para {TARGET_PHONE}? (s/N): ")
    if confirm.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Teste cancelado pelo usuário")
        return
    
    # Testar conexão
    if not test_server_connection():
        return
    
    # Buscar templates
    templates = get_all_templates()
    
    if not templates:
        print("⚠️  Nenhum template encontrado. Criando templates de exemplo...")
        created_ids = create_sample_templates_if_none()
        
        if created_ids:
            print("🔄 Buscando templates novamente...")
            time.sleep(2)
            templates = get_all_templates()
    
    if not templates:
        print("❌ Não foi possível encontrar ou criar templates")
        return
    
    print(f"\n📊 Encontrados {len(templates)} template(s)")
    
    # Enviar cada template
    results = []
    for i, template in enumerate(templates, 1):
        print(f"\n🔄 Processando template {i}/{len(templates)}")
        
        success = send_template_message(template)
        results.append({
            "template_name": template.get("name", "Sem nome"),
            "template_id": template.get("id"),
            "success": success
        })
        
        # Pausa entre envios para não sobrecarregar a API
        if i < len(templates):
            print("⏳ Aguardando 3 segundos antes do próximo envio...")
            time.sleep(3)
    
    # Relatório final
    print_separator("RELATÓRIO FINAL")
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"📊 Resumo do Teste:")
    print(f"📱 Número de destino: {TARGET_PHONE}")
    print(f"📝 Templates processados: {len(results)}")
    print(f"✅ Envios bem-sucedidos: {successful}")
    print(f"❌ Envios falharam: {failed}")
    print(f"📈 Taxa de sucesso: {(successful/len(results)*100):.1f}%")
    
    print(f"\n📋 Detalhes por Template:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['template_name']} (ID: {result['template_id']})")
    
    if successful > 0:
        print(f"\n🎉 {successful} mensagem(s) foram enviadas para {TARGET_PHONE}!")
        print("📱 Verifique o dispositivo de destino para ver as mensagens RCS")
    
    if failed > 0:
        print(f"\n⚠️  {failed} template(s) falharam. Verifique:")
        print("- Se o token RCS está configurado corretamente")
        print("- Se o número de destino é válido")
        print("- Se há problemas de conectividade")
        print("- Os logs do servidor para mais detalhes")

if __name__ == "__main__":
    main()
