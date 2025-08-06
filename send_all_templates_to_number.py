#!/usr/bin/env python3
"""
Script direto para enviar todos os templates para o número 11998637834.
Este script é otimizado para uso prático e imediato.

IMPORTANTE: Configure seu token RCS no arquivo .env antes de executar!
"""

import requests
import json
import time
import re
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}
TARGET_PHONE = "5511998637834"

def log(message, level="INFO"):
    """Log com timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def get_all_templates():
    """Busca todos os templates disponíveis."""
    log("Buscando todos os templates...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/rcs/templates", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            templates = response.json()
            log(f"Encontrados {len(templates)} templates")
            return templates
        else:
            log(f"Erro ao buscar templates: HTTP {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log(f"Erro de conexão: {e}", "ERROR")
        return []

def generate_variables_for_template(template_data):
    """Gera variáveis automaticamente baseadas no template."""
    # Variáveis padrão
    vars_map = {
        "nome": "João Silva",
        "produto": "iPhone 15 Pro",
        "preco": "R$ 7.999,00",
        "desconto": "20",
        "empresa": "TechStore Brasil",
        "data": datetime.now().strftime("%d/%m/%Y"),
        "hora": datetime.now().strftime("%H:%M"),
        "codigo": "TS2024",
        "quantidade": "1",
        "categoria": "smartphones",
        "produto_id": "iphone15pro",
        "produto1_nome": "iPhone 15 Pro",
        "produto1_desc": "Smartphone Apple com chip A17 Pro",
        "produto1_img": "iphone15pro.jpg",
        "produto1_id": "iphone15pro",
        "produto2_nome": "Samsung Galaxy S24 Ultra",
        "produto2_desc": "Smartphone Samsung com S Pen",
        "produto2_img": "galaxys24ultra.jpg",
        "produto2_id": "galaxys24ultra",
        "link": "https://www.apple.com",
        "telefone": "11999887766",
        "email": "contato@techstore.com.br",
        "valor": "R$ 1.299,00",
        "parcelas": "12x",
        "juros": "sem juros",
        "frete": "grátis",
        "prazo": "24h",
        "loja": "TechStore Shopping",
        "vendedor": "Carlos Silva",
        "cliente": "João Silva"
    }
    
    # Encontrar variáveis no template
    template_str = json.dumps(template_data, ensure_ascii=False)
    variables = re.findall(r'\{\{(\w+)\}\}', template_str)
    
    # Criar dicionário apenas com as variáveis necessárias
    result_vars = {}
    for var in set(variables):
        if var in vars_map:
            result_vars[var] = vars_map[var]
        else:
            result_vars[var] = f"Exemplo_{var}"
    
    return result_vars

def send_template(template):
    """Envia um template específico."""
    template_id = template.get("id")
    template_name = template.get("name", "Sem nome")
    template_data = template.get("template_data", {})
    account = template.get("account", "default")
    
    log(f"Enviando template '{template_name}' (ID: {template_id})")
    
    # Gerar variáveis
    variables = generate_variables_for_template(template_data)
    
    if variables:
        log(f"Variáveis detectadas: {', '.join(variables.keys())}")
    
    # Payload
    payload = {
        "account": account,
        "template_id": template_id,
        "messages": [
            {
                "number": TARGET_PHONE,
                "vars": variables
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/rcs/template", 
            headers=HEADERS, 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                log(f"✅ Template '{template_name}' enviado com sucesso!", "SUCCESS")
                return True
            else:
                log(f"❌ Falha no template '{template_name}': {result}", "ERROR")
                return False
        else:
            log(f"❌ Erro HTTP {response.status_code} para template '{template_name}'", "ERROR")
            try:
                error_data = response.json()
                log(f"Detalhes do erro: {error_data}", "ERROR")
            except:
                log(f"Resposta do erro: {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ Erro ao enviar template '{template_name}': {e}", "ERROR")
        return False

def test_connection():
    """Testa conexão com o servidor."""
    log("Testando conexão com o servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            log("✅ Servidor conectado e funcionando", "SUCCESS")
            return True
        else:
            log(f"⚠️ Servidor respondeu com status {response.status_code}", "WARNING")
            return False
    except Exception as e:
        log(f"❌ Não foi possível conectar: {e}", "ERROR")
        log("💡 Certifique-se de que o servidor está rodando: python main.py", "INFO")
        return False

def main():
    """Função principal."""
    print("=" * 70)
    print("🚀 ENVIO DE TODOS OS TEMPLATES PARA NÚMERO ESPECÍFICO")
    print("=" * 70)
    print(f"📱 Número de destino: {TARGET_PHONE}")
    print(f"🌐 Servidor: {BASE_URL}")
    print("=" * 70)
    
    # Testar conexão
    if not test_connection():
        return
    
    # Buscar templates
    templates = get_all_templates()
    
    if not templates:
        log("❌ Nenhum template encontrado", "ERROR")
        log("💡 Crie alguns templates primeiro usando a API", "INFO")
        return
    
    # Confirmar envio
    print(f"\n⚠️  ATENÇÃO: Este script enviará {len(templates)} mensagem(s) RCS para {TARGET_PHONE}")
    print("📋 Templates encontrados:")
    for i, template in enumerate(templates, 1):
        print(f"   {i}. {template.get('name', 'Sem nome')} (ID: {template.get('id')})")
    
    confirm = input(f"\n🔄 Confirma o envio de {len(templates)} mensagem(s)? (s/N): ")
    if confirm.lower() not in ['s', 'sim', 'y', 'yes']:
        log("❌ Operação cancelada pelo usuário", "INFO")
        return
    
    # Enviar templates
    log(f"🚀 Iniciando envio de {len(templates)} templates...")
    
    successful = 0
    failed = 0
    
    for i, template in enumerate(templates, 1):
        log(f"📤 Processando {i}/{len(templates)}")
        
        if send_template(template):
            successful += 1
        else:
            failed += 1
        
        # Pausa entre envios
        if i < len(templates):
            log("⏳ Aguardando 2 segundos...")
            time.sleep(2)
    
    # Relatório final
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL")
    print("=" * 70)
    print(f"📱 Número de destino: {TARGET_PHONE}")
    print(f"📝 Templates processados: {len(templates)}")
    print(f"✅ Envios bem-sucedidos: {successful}")
    print(f"❌ Envios falharam: {failed}")
    print(f"📈 Taxa de sucesso: {(successful/len(templates)*100):.1f}%")
    print("=" * 70)
    
    if successful > 0:
        print(f"🎉 {successful} mensagem(s) foram enviadas para {TARGET_PHONE}!")
        print("📱 Verifique o dispositivo para ver as mensagens RCS")
    
    if failed > 0:
        print(f"⚠️  {failed} envio(s) falharam. Verifique:")
        print("   - Token RCS configurado no .env")
        print("   - Conectividade com a API RCS")
        print("   - Logs do servidor para detalhes")

if __name__ == "__main__":
    main()
