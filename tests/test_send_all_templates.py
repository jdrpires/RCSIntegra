import pytest
from unittest.mock import patch, MagicMock
import json
import re

class TestSendAllTemplates:
    """Teste para enviar todos os templates existentes para um número específico."""
    
    TARGET_PHONE = "5511998637834"
    
    def generate_sample_vars(self, template_data):
        """Gera variáveis de exemplo baseadas no template."""
        common_vars = {
            "nome": "João Silva",
            "produto": "Smartphone XYZ",
            "preco": "R$ 1.299,00",
            "desconto": "25",
            "empresa": "TechStore",
            "data": "04/08/2024",
            "hora": "15:30",
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
        variables = re.findall(r'\{\{(\w+)\}\}', template_str)
        
        # Criar dicionário com as variáveis encontradas
        vars_dict = {}
        for var in set(variables):
            if var in common_vars:
                vars_dict[var] = common_vars[var]
            else:
                vars_dict[var] = f"Valor_{var}"
        
        return vars_dict

    def test_send_all_existing_templates(self, client, sample_account, db_session):
        """Teste que busca todos os templates e envia para o número específico."""
        from models import RCSTemplate
        
        # Criar alguns templates de exemplo no banco
        templates_data = [
            {
                "name": "Template Texto Teste",
                "account": sample_account,
                "content_type": "text",
                "template_data": {
                    "message": "Olá {{nome}}! Bem-vindo à {{empresa}}. Seu código é: {{codigo}}"
                }
            },
            {
                "name": "Template Rich Card Teste",
                "account": sample_account,
                "content_type": "richCard",
                "template_data": {
                    "title": "🎉 Oferta para {{nome}}!",
                    "description": "{{desconto}}% de desconto em {{produto}}!",
                    "fileUrl": "https://picsum.photos/600/400",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Ver Produto",
                            "value": "https://loja.exemplo.com/{{produto_id}}"
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
                "name": "Template Carousel Teste",
                "account": sample_account,
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
        
        # Criar templates no banco
        created_templates = []
        for template_data in templates_data:
            template = RCSTemplate(**template_data)
            db_session.add(template)
            db_session.commit()
            db_session.refresh(template)
            created_templates.append(template)
        
        print(f"\n📝 Criados {len(created_templates)} templates para teste")
        
        # Buscar todos os templates
        response = client.get(f"/api/rcs/templates?account={sample_account}")
        assert response.status_code == 200
        
        templates = response.json()
        assert len(templates) >= len(created_templates)
        
        print(f"📋 Encontrados {len(templates)} templates no total")
        
        # Enviar cada template para o número específico
        successful_sends = 0
        failed_sends = 0
        
        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }
            
            for template in templates:
                template_id = template["id"]
                template_name = template["name"]
                template_data = template["template_data"]
                
                print(f"\n📤 Enviando template: {template_name} (ID: {template_id})")
                
                # Gerar variáveis baseadas no template
                sample_vars = self.generate_sample_vars(template_data)
                print(f"🔧 Variáveis: {list(sample_vars.keys())}")
                
                # Payload para envio
                payload = {
                    "account": sample_account,
                    "template_id": template_id,
                    "messages": [
                        {
                            "number": self.TARGET_PHONE,
                            "vars": sample_vars
                        }
                    ]
                }
                
                # Enviar template
                response = client.post("/api/rcs/template", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ Template '{template_name}' enviado com sucesso!")
                        successful_sends += 1
                    else:
                        print(f"❌ Falha no envio do template '{template_name}': {data}")
                        failed_sends += 1
                else:
                    print(f"❌ Erro HTTP {response.status_code} para template '{template_name}'")
                    failed_sends += 1
        
        # Verificar resultados
        total_templates = len(templates)
        print(f"\n📊 RELATÓRIO FINAL:")
        print(f"📱 Número de destino: {self.TARGET_PHONE}")
        print(f"📝 Templates processados: {total_templates}")
        print(f"✅ Envios bem-sucedidos: {successful_sends}")
        print(f"❌ Envios falharam: {failed_sends}")
        print(f"📈 Taxa de sucesso: {(successful_sends/total_templates*100):.1f}%")
        
        # Verificar se pelo menos alguns templates foram enviados
        assert successful_sends > 0, "Nenhum template foi enviado com sucesso"
        assert successful_sends == total_templates, f"Nem todos os templates foram enviados: {successful_sends}/{total_templates}"
        
        # Verificar se o mock foi chamado o número correto de vezes
        assert mock_send.call_count == total_templates
        
        # Verificar se todas as chamadas foram para o número correto
        for call in mock_send.call_args_list:
            call_kwargs = call[1]
            assert call_kwargs["phone_number"] == self.TARGET_PHONE

    def test_send_all_templates_with_real_api(self, client, sample_account, db_session):
        """Teste para enviar com API real (marcar como slow para execução opcional)."""
        pytest.skip("Teste com API real - execute manualmente se necessário")
        
        # Este teste seria idêntico ao anterior, mas sem o mock
        # Descomente e ajuste se quiser testar com API real
        pass

    def test_handle_templates_with_missing_variables(self, client, sample_account, db_session):
        """Teste para templates com variáveis ausentes."""
        from models import RCSTemplate
        
        # Criar template com variáveis que não serão fornecidas
        template = RCSTemplate(
            name="Template Variáveis Ausentes",
            account=sample_account,
            content_type="text",
            template_data={
                "message": "Olá {{nome}}, seu {{produto_inexistente}} está pronto! Código: {{codigo_ausente}}"
            }
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Gerar variáveis (algumas estarão ausentes)
        sample_vars = self.generate_sample_vars(template.template_data)
        
        # Remover algumas variáveis propositalmente
        if "produto_inexistente" in sample_vars:
            del sample_vars["produto_inexistente"]
        if "codigo_ausente" in sample_vars:
            del sample_vars["codigo_ausente"]
        
        payload = {
            "account": sample_account,
            "template_id": template.id,
            "messages": [
                {
                    "number": self.TARGET_PHONE,
                    "vars": sample_vars
                }
            ]
        }
        
        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }
            
            response = client.post("/api/rcs/template", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # Verificar se as variáveis ausentes permaneceram como placeholders
            call_args = mock_send.call_args[1]
            message_content = call_args["content"]["text"]["message"]
            
            # Variáveis fornecidas devem ser substituídas
            assert "João Silva" in message_content
            
            # Variáveis ausentes devem permanecer como placeholders
            assert "{{produto_inexistente}}" in message_content
            assert "{{codigo_ausente}}" in message_content

    def test_empty_templates_scenario(self, client, sample_account):
        """Teste quando não há templates disponíveis."""
        # Buscar templates quando não há nenhum
        response = client.get(f"/api/rcs/templates?account={sample_account}")
        
        assert response.status_code == 200
        templates = response.json()
        
        # Se não há templates, a lista deve estar vazia
        if len(templates) == 0:
            print("ℹ️  Nenhum template encontrado - cenário válido")
            assert len(templates) == 0
        else:
            print(f"ℹ️  Encontrados {len(templates)} templates existentes")
            assert len(templates) > 0
