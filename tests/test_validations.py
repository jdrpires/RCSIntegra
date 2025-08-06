import pytest
from unittest.mock import patch, MagicMock
import json

class TestPhoneValidation:
    """Testes para validação de números de telefone."""

    def test_valid_brazilian_phone_numbers(self, client, sample_account, sample_text_content):
        """Teste com números brasileiros válidos."""
        valid_numbers = [
            "5511999999999",  # SP com 9
            "5521888888888",  # RJ com 8
            "5531777777777",  # MG
            "5541666666666",  # PR
            "5551555555555",  # RS
            "5561444444444",  # DF
            "5571333333333",  # BA
            "5581222222222",  # PE
            "5591111111111",  # PA
            "5511912345678"   # SP formato completo
        ]

        for number in valid_numbers:
            payload = {
                "campaign_name": f"Teste {number}",
                "account": sample_account,
                "messages": [
                    {
                        "number": number,
                        "vars": {"nome": "Teste"}
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

                response = client.post("/api/rcs/basic", json=payload)
                
                assert response.status_code == 200, f"Falhou para número: {number}"

    def test_invalid_phone_numbers(self, client, sample_account, sample_text_content):
        """Teste com números inválidos."""
        invalid_numbers = [
            "123456",          # Muito curto
            "55119999999999",  # Muito longo
            "1199999999",      # Sem código do país
            "5511999999",      # Muito curto
            "abc123456789",    # Com letras
            "",                # Vazio
            "55119999999a",    # Com letra no final
            "55 11 99999-9999" # Com formatação
        ]

        for number in invalid_numbers:
            payload = {
                "campaign_name": f"Teste {number}",
                "account": sample_account,
                "messages": [
                    {
                        "number": number,
                        "vars": {"nome": "Teste"}
                    }
                ],
                "content": sample_text_content
            }

            response = client.post("/api/rcs/basic", json=payload)
            
            assert response.status_code == 400, f"Deveria falhar para número: {number}"

    def test_phone_number_formatting(self, client, sample_account, sample_text_content):
        """Teste de formatação automática de números."""
        # Números que devem ser formatados automaticamente
        test_cases = [
            ("11999999999", "5511999999999"),    # Adicionar código do país
            ("011999999999", "5511999999999"),   # Remover 0 do DDD
            ("+5511999999999", "5511999999999"), # Remover +
            ("55 11 99999-9999", "5511999999999") # Remover formatação
        ]

        for input_number, expected_number in test_cases:
            payload = {
                "campaign_name": f"Teste formatação {input_number}",
                "account": sample_account,
                "messages": [
                    {
                        "number": input_number,
                        "vars": {"nome": "Teste"}
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

                response = client.post("/api/rcs/basic", json=payload)
                
                if response.status_code == 200:
                    # Verificar se o número foi formatado corretamente na chamada da API
                    call_args = mock_send.call_args[1]
                    assert call_args["phone_number"] == expected_number

class TestContentValidation:
    """Testes para validação de conteúdo."""

    def test_text_message_length_limits(self, client, sample_account, sample_phone_numbers):
        """Teste de limites de caracteres para mensagens de texto."""
        # Mensagem no limite (5000 caracteres)
        valid_message = "A" * 5000
        payload = {
            "campaign_name": "Teste Limite",
            "account": sample_account,
            "messages": [{"number": sample_phone_numbers[0], "vars": {}}],
            "content": {"text": {"message": valid_message}}
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            response = client.post("/api/rcs/basic", json=payload)
            assert response.status_code == 200

        # Mensagem acima do limite (5001 caracteres)
        invalid_message = "A" * 5001
        payload["content"]["text"]["message"] = invalid_message

        response = client.post("/api/rcs/basic", json=payload)
        assert response.status_code == 400

    def test_url_validation(self, client, sample_account, sample_phone_numbers):
        """Teste de validação de URLs."""
        # URLs válidas (HTTPS)
        valid_urls = [
            "https://exemplo.com/imagem.jpg",
            "https://cdn.exemplo.com/video.mp4",
            "https://storage.exemplo.com/documento.pdf"
        ]

        for url in valid_urls:
            payload = {
                "account": sample_account,
                "messages": [{"number": sample_phone_numbers[0]}],
                "content": {
                    "image": {
                        "fileUrl": url,
                        "message": "Teste URL válida"
                    }
                }
            }

            with patch('rcs_client.RCSClient.send_message') as mock_send:
                mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
                response = client.post("/api/rcs/single", json=payload)
                assert response.status_code == 200, f"Falhou para URL: {url}"

        # URLs inválidas (HTTP ou malformadas)
        invalid_urls = [
            "http://exemplo.com/imagem.jpg",  # HTTP
            "ftp://exemplo.com/arquivo.pdf",  # FTP
            "exemplo.com/imagem.jpg",         # Sem protocolo
            "https://",                       # Incompleta
            "not-a-url"                       # Não é URL
        ]

        for url in invalid_urls:
            payload = {
                "account": sample_account,
                "messages": [{"number": sample_phone_numbers[0]}],
                "content": {
                    "image": {
                        "fileUrl": url,
                        "message": "Teste URL inválida"
                    }
                }
            }

            response = client.post("/api/rcs/single", json=payload)
            assert response.status_code == 400, f"Deveria falhar para URL: {url}"

    def test_suggestions_limit(self, client, sample_account, sample_phone_numbers):
        """Teste de limite de sugestões (máximo 4)."""
        # 4 sugestões (válido)
        valid_suggestions = [
            {"type": "reply", "title": "Opção 1", "value": "1"},
            {"type": "reply", "title": "Opção 2", "value": "2"},
            {"type": "reply", "title": "Opção 3", "value": "3"},
            {"type": "reply", "title": "Opção 4", "value": "4"}
        ]

        payload = {
            "account": sample_account,
            "messages": [{"number": sample_phone_numbers[0]}],
            "content": {
                "suggestion": {
                    "message": "Escolha uma opção:",
                    "suggestions": valid_suggestions
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            response = client.post("/api/rcs/single", json=payload)
            assert response.status_code == 200

        # 5 sugestões (inválido)
        invalid_suggestions = valid_suggestions + [
            {"type": "reply", "title": "Opção 5", "value": "5"}
        ]

        payload["content"]["suggestion"]["suggestions"] = invalid_suggestions
        response = client.post("/api/rcs/single", json=payload)
        assert response.status_code == 400

    def test_suggestion_types_validation(self, client, sample_account, sample_phone_numbers):
        """Teste de validação de tipos de sugestão."""
        # Tipos válidos
        valid_types = ["reply", "openUrl", "call"]
        
        for suggestion_type in valid_types:
            suggestions = [
                {
                    "type": suggestion_type,
                    "title": f"Teste {suggestion_type}",
                    "value": "test_value" if suggestion_type == "reply" else 
                            "https://exemplo.com" if suggestion_type == "openUrl" else
                            "1140001234"
                }
            ]

            payload = {
                "account": sample_account,
                "messages": [{"number": sample_phone_numbers[0]}],
                "content": {
                    "suggestion": {
                        "message": "Teste tipos de sugestão",
                        "suggestions": suggestions
                    }
                }
            }

            with patch('rcs_client.RCSClient.send_message') as mock_send:
                mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
                response = client.post("/api/rcs/single", json=payload)
                assert response.status_code == 200, f"Falhou para tipo: {suggestion_type}"

        # Tipo inválido
        invalid_suggestions = [
            {
                "type": "invalid_type",
                "title": "Tipo Inválido",
                "value": "test"
            }
        ]

        payload["content"]["suggestion"]["suggestions"] = invalid_suggestions
        response = client.post("/api/rcs/single", json=payload)
        assert response.status_code == 400

class TestFallbackValidation:
    """Testes para validação de fallback SMS."""

    def test_fallback_content_sanitization(self, client, sample_account, sample_phone_numbers):
        """Teste de sanitização do conteúdo de fallback."""
        payload = {
            "campaign_name": "Teste Fallback",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {"nome": "João"}
                }
            ],
            "content": {
                "text": {
                    "message": "Olá {{nome}}, você tem uma mensagem!"
                }
            },
            "fallback": [
                {
                    "channel": "SMS",
                    "content": "Olá {{nome}}, você têm ümä mënsägëm com açéntos!"
                }
            ]
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            
            response = client.post("/api/rcs/basic", json=payload)
            assert response.status_code == 200
            
            # Verificar se os acentos foram removidos no fallback
            call_args = mock_send.call_args[1]
            fallback_content = call_args["fallback"][0]["content"]
            assert "têm" not in fallback_content
            assert "ümä" not in fallback_content
            assert "mënsägëm" not in fallback_content
            assert "açéntos" not in fallback_content

    def test_fallback_length_limit(self, client, sample_account, sample_phone_numbers):
        """Teste de limite de caracteres no fallback (160 caracteres)."""
        # Fallback no limite (160 caracteres)
        valid_fallback = "A" * 160
        
        payload = {
            "campaign_name": "Teste Fallback Limite",
            "account": sample_account,
            "messages": [{"number": sample_phone_numbers[0], "vars": {}}],
            "content": {"text": {"message": "Mensagem principal"}},
            "fallback": [{"channel": "SMS", "content": valid_fallback}]
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            response = client.post("/api/rcs/basic", json=payload)
            assert response.status_code == 200

        # Fallback acima do limite (161 caracteres) - deve ser truncado
        long_fallback = "A" * 161
        payload["fallback"][0]["content"] = long_fallback

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            response = client.post("/api/rcs/basic", json=payload)
            assert response.status_code == 200
            
            # Verificar se foi truncado
            call_args = mock_send.call_args[1]
            fallback_content = call_args["fallback"][0]["content"]
            assert len(fallback_content) <= 160

class TestVariableSubstitution:
    """Testes para substituição de variáveis."""

    def test_simple_variable_substitution(self, client, sample_account, sample_phone_numbers):
        """Teste de substituição simples de variáveis."""
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
                    "message": "Olá {{nome}}, seu {{produto}} por {{preco}} chegou!"
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            
            response = client.post("/api/rcs/basic", json=payload)
            assert response.status_code == 200
            
            # Verificar substituição
            call_args = mock_send.call_args[1]
            expected = "Olá João Silva, seu iPhone 15 por R$ 5.999,00 chegou!"
            assert call_args["content"]["text"]["message"] == expected

    def test_missing_variables(self, client, sample_account, sample_phone_numbers):
        """Teste com variáveis ausentes."""
        payload = {
            "campaign_name": "Teste Variáveis Ausentes",
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {
                        "nome": "João"
                        # "produto" ausente
                    }
                }
            ],
            "content": {
                "text": {
                    "message": "Olá {{nome}}, seu {{produto}} está pronto!"
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            
            response = client.post("/api/rcs/basic", json=payload)
            assert response.status_code == 200
            
            # Verificar que variável ausente permanece como placeholder
            call_args = mock_send.call_args[1]
            message = call_args["content"]["text"]["message"]
            assert "João" in message
            assert "{{produto}}" in message  # Deve permanecer não substituída

    def test_variable_substitution_in_rich_card(self, client, sample_account, sample_phone_numbers):
        """Teste de substituição de variáveis em Rich Card."""
        payload = {
            "account": sample_account,
            "messages": [
                {
                    "number": sample_phone_numbers[0],
                    "vars": {
                        "nome": "Maria",
                        "desconto": "25",
                        "produto_url": "smartphone-xyz"
                    }
                }
            ],
            "content": {
                "richCard": {
                    "title": "Oferta especial para {{nome}}!",
                    "description": "{{desconto}}% de desconto hoje!",
                    "fileUrl": "https://exemplo.com/promo.jpg",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Ver Oferta",
                            "value": "https://loja.exemplo.com/{{produto_url}}"
                        }
                    ]
                }
            }
        }

        with patch('rcs_client.RCSClient.send_message') as mock_send:
            mock_send.return_value = {"success": True, "message_id": "msg_123", "status": "sent"}
            
            response = client.post("/api/rcs/single", json=payload)
            assert response.status_code == 200
            
            # Verificar substituições no Rich Card
            call_args = mock_send.call_args[1]
            rich_card = call_args["content"]["richCard"]
            assert rich_card["title"] == "Oferta especial para Maria!"
            assert rich_card["description"] == "25% de desconto hoje!"
            assert rich_card["suggestions"][0]["value"] == "https://loja.exemplo.com/smartphone-xyz"
