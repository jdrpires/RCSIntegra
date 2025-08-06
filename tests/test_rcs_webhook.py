import pytest
from unittest.mock import patch, MagicMock
import json

class TestRCSWebhook:
    """Testes para o endpoint RCS Webhook (conversacional)."""

    def test_rcs_webhook_success(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste de mensagem conversacional com webhook."""
        payload = {
            "account": sample_account,
            "webhook": "https://exemplo.com/webhook-rcs",
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": sample_text_content
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/webhook", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 1

    def test_rcs_webhook_with_rich_card(self, client, sample_account, sample_phone_numbers, sample_rich_card_content):
        """Teste de webhook com Rich Card."""
        payload = {
            "account": sample_account,
            "webhook": "https://exemplo.com/webhook-rcs",
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": sample_rich_card_content
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/webhook", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_webhook_invalid_url(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste com URL de webhook inválida."""
        payload = {
            "account": sample_account,
            "webhook": "http://exemplo.com/webhook",  # HTTP em vez de HTTPS
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": sample_text_content
        }

        response = client.post("/api/rcs/webhook", json=payload)
        
        assert response.status_code == 400

    def test_rcs_webhook_missing_webhook_url(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste sem URL de webhook."""
        payload = {
            "account": sample_account,
            # webhook ausente
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": sample_text_content
        }

        response = client.post("/api/rcs/webhook", json=payload)
        
        assert response.status_code == 422  # Validation error

    def test_rcs_webhook_with_suggestions(self, client, sample_account, sample_phone_numbers):
        """Teste de webhook com sugestões interativas."""
        payload = {
            "account": sample_account,
            "webhook": "https://exemplo.com/webhook-rcs",
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {
                "suggestion": {
                    "message": "Como posso ajudá-lo?",
                    "suggestions": [
                        {
                            "type": "reply",
                            "title": "Suporte",
                            "value": "suporte"
                        },
                        {
                            "type": "reply",
                            "title": "Vendas",
                            "value": "vendas"
                        },
                        {
                            "type": "openUrl",
                            "title": "Site",
                            "value": "https://exemplo.com"
                        }
                    ]
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/webhook", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_webhook_multiple_recipients(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste de webhook para múltiplos destinatários."""
        payload = {
            "account": sample_account,
            "webhook": "https://exemplo.com/webhook-rcs",
            "messages": [
                {"number": sample_phone_numbers[0]},
                {"number": sample_phone_numbers[1]}
            ],
            "content": sample_text_content
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/webhook", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 2
            assert mock_send.call_count == 2

    def test_rcs_webhook_api_error(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste quando a API RCS retorna erro."""
        payload = {
            "account": sample_account,
            "webhook": "https://exemplo.com/webhook-rcs",
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": sample_text_content
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": False,
                "error": "Webhook URL not reachable",
                "code": "WEBHOOK_ERROR"
            }

            response = client.post("/api/rcs/webhook", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["results"][0]["status"] == "error"

    def test_rcs_webhook_with_carousel(self, client, sample_account, sample_phone_numbers, sample_carousel_content):
        """Teste de webhook com carousel."""
        payload = {
            "account": sample_account,
            "webhook": "https://exemplo.com/webhook-rcs",
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": sample_carousel_content
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/webhook", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

class TestRCSCallbacks:
    """Testes para recebimento de callbacks."""

    def test_callback_delivery_status(self, client, db_session):
        """Teste de callback de status de entrega."""
        # Primeiro, criar uma mensagem no banco
        from models import RCSMessage
        message = RCSMessage(
            message_id="msg_123456789",
            phone_number="5511999999999",
            account="test_account",
            content_type="text",
            content={"text": {"message": "Teste"}},
            status="sent"
        )
        db_session.add(message)
        db_session.commit()

        # Simular callback de entrega
        callback_payload = {
            "message_id": "msg_123456789",
            "status": "delivered",
            "timestamp": "2024-01-01T12:00:00Z",
            "phone_number": "5511999999999"
        }

        response = client.post("/api/rcs/callback", json=callback_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verificar se o status foi atualizado no banco
        updated_message = db_session.query(RCSMessage).filter_by(message_id="msg_123456789").first()
        assert updated_message.status == "delivered"

    def test_callback_user_reply(self, client, db_session):
        """Teste de callback de resposta do usuário."""
        callback_payload = {
            "message_id": "msg_123456789",
            "type": "user_reply",
            "phone_number": "5511999999999",
            "reply_text": "Sim, tenho interesse",
            "timestamp": "2024-01-01T12:05:00Z"
        }

        response = client.post("/api/rcs/callback", json=callback_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verificar se o callback foi salvo no banco
        from models import RCSCallback
        callback = db_session.query(RCSCallback).filter_by(message_id="msg_123456789").first()
        assert callback is not None
        assert callback.callback_type == "user_reply"
        assert callback.callback_data["reply_text"] == "Sim, tenho interesse"

    def test_callback_button_click(self, client, db_session):
        """Teste de callback de clique em botão."""
        callback_payload = {
            "message_id": "msg_123456789",
            "type": "button_click",
            "phone_number": "5511999999999",
            "button_value": "suporte",
            "button_title": "Suporte",
            "timestamp": "2024-01-01T12:10:00Z"
        }

        response = client.post("/api/rcs/callback", json=callback_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verificar se o callback foi salvo no banco
        from models import RCSCallback
        callback = db_session.query(RCSCallback).filter_by(message_id="msg_123456789").first()
        assert callback is not None
        assert callback.callback_type == "button_click"
        assert callback.callback_data["button_value"] == "suporte"

    def test_callback_invalid_message_id(self, client):
        """Teste de callback com message_id inválido."""
        callback_payload = {
            "message_id": "invalid_msg_id",
            "status": "delivered",
            "timestamp": "2024-01-01T12:00:00Z",
            "phone_number": "5511999999999"
        }

        response = client.post("/api/rcs/callback", json=callback_payload)
        
        # Deve aceitar o callback mesmo se a mensagem não existir no banco
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
