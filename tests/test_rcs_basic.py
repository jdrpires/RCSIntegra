import pytest
from unittest.mock import patch, MagicMock
import json

class TestRCSBasic:
    """Testes para o endpoint RCS Basic."""

    def test_rcs_basic_success(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste de envio básico bem-sucedido."""
        payload = {
            "campaign_name": "Campanha Teste",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {
                        "nome": "João",
                        "produto": "Smartphone"
                    }
                }
            ],
            "content": sample_text_content,
            "callback": "https://exemplo.com/callback",
            "fallback": [
                {
                    "channel": "SMS",
                    "content": "Ola João, esta e uma mensagem de teste!"
                }
            ]
        }

        with patch('rcs_client.RCSAPIClient.send_basic_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/basic", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["status"] == "sent"

    def test_rcs_basic_multiple_numbers(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste de envio para múltiplos números."""
        payload = {
            "campaign_name": "Campanha Múltipla",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {"nome": "João"}
                },
                {
                    "number": sample_phone_numbers[1],
                    "vars": {"nome": "Maria"}
                },
                {
                    "number": sample_phone_numbers[2],
                    "vars": {"nome": "Pedro"}
                }
            ],
            "content": sample_text_content
        }

        with patch('rcs_client.RCSAPIClient.send_basic_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/basic", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert mock_send.call_count == 3

    def test_rcs_basic_invalid_phone(self, client, sample_account, sample_text_content):
        """Teste com número de telefone inválido."""
        payload = {
            "campaign_name": "Campanha Teste",
            "account": sample_account,
            "messages": [
                {
                    "number": "123456",  # Número inválido
                    "vars": {"nome": "João"}
                }
            ],
            "content": sample_text_content
        }

        response = client.post("/api/rcs/basic", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_rcs_basic_missing_required_fields(self, client):
        """Teste com campos obrigatórios ausentes."""
        payload = {
            "campaign_name": "Campanha Teste"
            # Faltando account, messages, content
        }

        response = client.post("/api/rcs/basic", json=payload)
        
        assert response.status_code == 422  # Validation error

    def test_rcs_basic_with_fallback(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste com fallback SMS."""
        payload = {
            "campaign_name": "Campanha com Fallback",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {"nome": "João"}
                }
            ],
            "content": sample_text_content,
            "fallback": [
                {
                    "channel": "SMS",
                    "content": "Mensagem de fallback para {{nome}}"
                }
            ]
        }

        with patch('rcs_client.RCSAPIClient.send_basic_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/basic", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_rcs_basic_api_error(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste quando a API RCS retorna erro."""
        payload = {
            "campaign_name": "Campanha Teste",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {"nome": "João"}
                }
            ],
            "content": sample_text_content
        }

        with patch('rcs_client.RCSAPIClient.send_basic_message') as mock_send:
            mock_send.side_effect = Exception("API Error")

            response = client.post("/api/rcs/basic", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["status"] == "failed"

    def test_rcs_basic_variable_substitution(self, client, sample_account, sample_phone_numbers):
        """Teste de substituição de variáveis no conteúdo."""
        payload = {
            "campaign_name": "Teste Variáveis",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {
                        "nome": "João Silva",
                        "produto": "iPhone 15",
                        "preco": "R$ 5.999,00"
                    }
                }
            ],
            "content": {
                "text": {
                    "message": "Olá {{nome}}, seu {{produto}} por {{preco}} está disponível!"
                }
            }
        }

        with patch('rcs_client.RCSAPIClient.send_basic_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/basic", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_rcs_basic_long_message(self, client, sample_account, sample_phone_numbers):
        """Teste com mensagem longa (limite de 5000 caracteres)."""
        long_message = "A" * 4999  # Dentro do limite
        
        payload = {
            "campaign_name": "Mensagem Longa",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {}
                }
            ],
            "content": {
                "text": {
                    "message": long_message
                }
            }
        }

        with patch('rcs_client.RCSAPIClient.send_basic_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/basic", json=payload)
            
            assert response.status_code == 200

    def test_rcs_basic_too_long_message(self, client, sample_account, sample_phone_numbers):
        """Teste com mensagem muito longa (acima do limite)."""
        too_long_message = "A" * 5001  # Acima do limite
        
        payload = {
            "campaign_name": "Mensagem Muito Longa",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {}
                }
            ],
            "content": {
                "text": {
                    "message": too_long_message
                }
            }
        }

        response = client.post("/api/rcs/basic", json=payload)
        
        assert response.status_code == 400
