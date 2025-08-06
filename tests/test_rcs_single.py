import pytest
from unittest.mock import patch, MagicMock
import json

class TestRCSSingle:
    """Testes para o endpoint RCS Single."""

    def test_rcs_single_text_message(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste de mensagem de texto simples."""
        payload = {
            "account": sample_account,
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

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 1

    def test_rcs_single_rich_card(self, client, sample_account, sample_phone_numbers, sample_rich_card_content):
        """Teste de Rich Card."""
        payload = {
            "account": sample_account,
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

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_single_carousel(self, client, sample_account, sample_phone_numbers, sample_carousel_content):
        """Teste de Carousel."""
        payload = {
            "account": sample_account,
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

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_single_image_message(self, client, sample_account, sample_phone_numbers):
        """Teste de mensagem com imagem."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {
                "image": {
                    "fileUrl": "https://exemplo.com/imagem.jpg",
                    "message": "Confira esta imagem!"
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_single_video_message(self, client, sample_account, sample_phone_numbers):
        """Teste de mensagem com vídeo."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {
                "video": {
                    "fileUrl": "https://exemplo.com/video.mp4",
                    "message": "Assista a este vídeo!"
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_single_pdf_message(self, client, sample_account, sample_phone_numbers):
        """Teste de mensagem com PDF."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {
                "pdf": {
                    "fileUrl": "https://exemplo.com/documento.pdf",
                    "message": "Documento importante anexado."
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_single_suggestions_only(self, client, sample_account, sample_phone_numbers):
        """Teste de mensagem apenas com sugestões (botões)."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {
                "suggestion": {
                    "message": "Escolha uma opção:",
                    "suggestions": [
                        {
                            "type": "reply",
                            "title": "Sim",
                            "value": "sim"
                        },
                        {
                            "type": "reply",
                            "title": "Não",
                            "value": "nao"
                        },
                        {
                            "type": "openUrl",
                            "title": "Mais Info",
                            "value": "https://exemplo.com/info"
                        },
                        {
                            "type": "call",
                            "title": "Ligar",
                            "value": "1140001234"
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

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_rcs_single_invalid_url(self, client, sample_account, sample_phone_numbers):
        """Teste com URL inválida (não HTTPS)."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {
                "image": {
                    "fileUrl": "http://exemplo.com/imagem.jpg",  # HTTP em vez de HTTPS
                    "message": "Imagem com URL inválida"
                }
            }
        }

        response = client.post("/api/rcs/single", json=payload)
        
        assert response.status_code == 400

    def test_rcs_single_too_many_suggestions(self, client, sample_account, sample_phone_numbers):
        """Teste com mais de 4 sugestões (limite)."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {
                "suggestion": {
                    "message": "Muitas opções:",
                    "suggestions": [
                        {"type": "reply", "title": "Opção 1", "value": "1"},
                        {"type": "reply", "title": "Opção 2", "value": "2"},
                        {"type": "reply", "title": "Opção 3", "value": "3"},
                        {"type": "reply", "title": "Opção 4", "value": "4"},
                        {"type": "reply", "title": "Opção 5", "value": "5"}  # 5ª opção - inválida
                    ]
                }
            }
        }

        response = client.post("/api/rcs/single", json=payload)
        
        assert response.status_code == 400

    def test_rcs_single_multiple_recipients(self, client, sample_account, sample_phone_numbers, sample_rich_card_content):
        """Teste de envio para múltiplos destinatários."""
        payload = {
            "account": sample_account,
            "messages": [
                {"number": sample_phone_numbers[0]},
                {"number": sample_phone_numbers[1]},
                {"number": sample_phone_numbers[2]}
            ],
            "content": sample_rich_card_content
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message_id": "msg_123456789",
                "status": "sent"
            }

            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 3
            assert mock_send.call_count == 3

    def test_rcs_single_empty_content(self, client, sample_account, sample_phone_numbers):
        """Teste com conteúdo vazio."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0]
                }
            ],
            "content": {}
        }

        response = client.post("/api/rcs/single", json=payload)
        
        assert response.status_code == 400

    def test_rcs_single_mixed_success_error(self, client, sample_account, sample_phone_numbers, sample_text_content):
        """Teste com alguns sucessos e alguns erros."""
        payload = {
            "account": sample_account,
            "messages": [
                {"number": sample_phone_numbers[0]},
                {"number": sample_phone_numbers[1]},
                {"number": sample_phone_numbers[2]}
            ],
            "content": sample_text_content
        }

        def mock_send_side_effect(*args, **kwargs):
            # Simular sucesso para o primeiro, erro para o segundo, sucesso para o terceiro
            call_count = mock_send_side_effect.call_count
            mock_send_side_effect.call_count += 1
            
            if call_count == 0:  # Primeira chamada - sucesso
                return {"success": True, "message_id": "msg_1", "status": "sent"}
            elif call_count == 1:  # Segunda chamada - erro
                return {"success": False, "error": "Invalid number", "code": "INVALID_PHONE"}
            else:  # Terceira chamada - sucesso
                return {"success": True, "message_id": "msg_3", "status": "sent"}

        mock_send_side_effect.call_count = 0

        with patch('rcs_client.RCSClient.send_message', side_effect=mock_send_side_effect):
            response = client.post("/api/rcs/single", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 3
            assert data["results"][0]["status"] == "sent"
            assert data["results"][1]["status"] == "error"
            assert data["results"][2]["status"] == "sent"
