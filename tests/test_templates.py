import pytest
from unittest.mock import patch, MagicMock
import json

class TestRCSTemplates:
    """Testes para criação e uso de templates."""

    def test_create_text_template(self, client, sample_account, db_session):
        """Teste de criação de template de texto."""
        payload = {
            "name": "Template Boas Vindas",
            "account": sample_account,
            "content_type": "text",
            "template_data": {
                "message": "Bem-vindo {{nome}} à nossa plataforma!"
            }
        }

        response = client.post("/api/rcs/templates", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "template_id" in data
        
        # Verificar se foi salvo no banco
        from models import RCSTemplate
        template = db_session.query(RCSTemplate).filter_by(name="Template Boas Vindas").first()
        assert template is not None
        assert template.content_type == "text"

    def test_create_rich_card_template(self, client, sample_account, db_session):
        """Teste de criação de template Rich Card."""
        payload = {
            "name": "Template Promoção",
            "account": sample_account,
            "content_type": "richCard",
            "template_data": {
                "title": "Oferta Especial para {{nome}}!",
                "description": "{{desconto}}% de desconto em {{produto}}",
                "fileUrl": "https://exemplo.com/promocao.jpg",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Oferta",
                        "value": "https://loja.exemplo.com/{{produto_id}}"
                    },
                    {
                        "type": "call",
                        "title": "Ligar",
                        "value": "1140001234"
                    }
                ]
            }
        }

        response = client.post("/api/rcs/templates", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verificar se foi salvo no banco
        from models import RCSTemplate
        template = db_session.query(RCSTemplate).filter_by(name="Template Promoção").first()
        assert template is not None
        assert template.content_type == "richCard"

    def test_create_carousel_template(self, client, sample_account, db_session):
        """Teste de criação de template Carousel."""
        payload = {
            "name": "Template Produtos",
            "account": sample_account,
            "content_type": "carousel",
            "template_data": {
                "cards": [
                    {
                        "title": "{{produto1_nome}}",
                        "description": "{{produto1_desc}}",
                        "fileUrl": "https://exemplo.com/{{produto1_img}}",
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
                        "fileUrl": "https://exemplo.com/{{produto2_img}}",
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

        response = client.post("/api/rcs/templates", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_templates(self, client, sample_account, db_session):
        """Teste de listagem de templates."""
        # Criar alguns templates primeiro
        from models import RCSTemplate
        
        template1 = RCSTemplate(
            name="Template 1",
            account=sample_account,
            content_type="text",
            template_data={"message": "Teste 1"}
        )
        template2 = RCSTemplate(
            name="Template 2",
            account=sample_account,
            content_type="richCard",
            template_data={"title": "Teste 2"}
        )
        
        db_session.add(template1)
        db_session.add(template2)
        db_session.commit()

        response = client.get(f"/api/rcs/templates?account={sample_account}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["Template 1", "Template 2"]
        assert data[1]["name"] in ["Template 1", "Template 2"]

    def test_get_template_by_id(self, client, sample_account, db_session):
        """Teste de busca de template por ID."""
        from models import RCSTemplate
        
        template = RCSTemplate(
            name="Template Teste",
            account=sample_account,
            content_type="text",
            template_data={"message": "Mensagem de teste"}
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        response = client.get(f"/api/rcs/templates/{template.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Template Teste"
        assert data["content_type"] == "text"

    def test_use_template_with_variables(self, client, sample_account, sample_phone_numbers, db_session):
        """Teste de uso de template com substituição de variáveis."""
        # Criar template primeiro
        from models import RCSTemplate
        
        template = RCSTemplate(
            name="Template Variáveis",
            account=sample_account,
            content_type="text",
            template_data={"message": "Olá {{nome}}, você tem {{quantidade}} mensagens!"}
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        # Usar o template
        payload = {
            "account": sample_account,
            "template_id": template.id,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {
                        "nome": "João",
                        "quantidade": "5"
                    }
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
            
            # Verificar se as variáveis foram substituídas
            call_args = mock_send.call_args[1]
            expected_message = "Olá João, você tem 5 mensagens!"
            assert call_args["content"]["text"]["message"] == expected_message

    def test_use_rich_card_template_with_variables(self, client, sample_account, sample_phone_numbers, db_session):
        """Teste de uso de template Rich Card com variáveis."""
        from models import RCSTemplate
        
        template = RCSTemplate(
            name="Template Rich Card",
            account=sample_account,
            content_type="richCard",
            template_data={
                "title": "Oferta para {{nome}}!",
                "description": "{{desconto}}% de desconto",
                "fileUrl": "https://exemplo.com/promo.jpg",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Oferta",
                        "value": "https://loja.exemplo.com/{{produto_id}}"
                    }
                ]
            }
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        payload = {
            "account": sample_account,
            "template_id": template.id,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {
                        "nome": "Maria",
                        "desconto": "20",
                        "produto_id": "smartphone123"
                    }
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
            
            # Verificar substituição de variáveis
            call_args = mock_send.call_args[1]
            rich_card = call_args["content"]["richCard"]
            assert rich_card["title"] == "Oferta para Maria!"
            assert rich_card["description"] == "20% de desconto"
            assert rich_card["suggestions"][0]["value"] == "https://loja.exemplo.com/smartphone123"

    def test_template_not_found(self, client, sample_account, sample_phone_numbers):
        """Teste com template inexistente."""
        payload = {
            "account": sample_account,
            "template_id": 99999,  # ID inexistente
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {}
                }
            ]
        }

        response = client.post("/api/rcs/template", json=payload)
        
        assert response.status_code == 404

    def test_create_template_duplicate_name(self, client, sample_account, db_session):
        """Teste de criação de template com nome duplicado."""
        # Criar primeiro template
        from models import RCSTemplate
        
        template = RCSTemplate(
            name="Template Duplicado",
            account=sample_account,
            content_type="text",
            template_data={"message": "Primeira versão"}
        )
        
        db_session.add(template)
        db_session.commit()

        # Tentar criar outro com mesmo nome
        payload = {
            "name": "Template Duplicado",
            "account": sample_account,
            "content_type": "text",
            "template_data": {
                "message": "Segunda versão"
            }
        }

        response = client.post("/api/rcs/templates", json=payload)
        
        assert response.status_code == 400

    def test_create_template_invalid_content_type(self, client, sample_account):
        """Teste de criação de template com tipo de conteúdo inválido."""
        payload = {
            "name": "Template Inválido",
            "account": sample_account,
            "content_type": "invalid_type",
            "template_data": {
                "message": "Teste"
            }
        }

        response = client.post("/api/rcs/templates", json=payload)
        
        assert response.status_code == 400

    def test_delete_template(self, client, sample_account, db_session):
        """Teste de exclusão de template."""
        from models import RCSTemplate
        
        template = RCSTemplate(
            name="Template para Deletar",
            account=sample_account,
            content_type="text",
            template_data={"message": "Será deletado"}
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        template_id = template.id

        response = client.delete(f"/api/rcs/templates/{template_id}")
        
        assert response.status_code == 200
        
        # Verificar se foi deletado do banco
        deleted_template = db_session.query(RCSTemplate).filter_by(id=template_id).first()
        assert deleted_template is None
