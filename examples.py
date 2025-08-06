#!/usr/bin/env python3
"""
Exemplos de uso da API RCS Gateway
"""

import httpx
import asyncio
import json

# URL base do gateway (ajuste conforme necessário)
BASE_URL = "http://localhost:8000"

async def example_text_message():
    """Exemplo de mensagem de texto simples"""
    data = {
        "campaign_name": "Campanha Teste",
        "account": "15885",
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Jean",
                    "produto": "Smartphone"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}, seu {{produto}} está disponível para retirada!"
            }
        },
        "callback": "https://seu-dominio.com/callback",
        "fallback": [
            {
                "channel": "SMS",
                "content": "Ola {{nome}}, seu {{produto}} esta disponivel para retirada!"
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/rcs/basic", json=data)
        print("Resposta mensagem de texto:", response.json())

async def example_rich_card():
    """Exemplo de Rich Card com botões"""
    data = {
        "campaign_name": "Promoção Especial",
        "account": "15885",
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Pires",
                    "desconto": "20%"
                }
            }
        ],
        "content": {
            "richCard": {
                "title": "Oferta Especial para {{nome}}!",
                "description": "Aproveite {{desconto}} de desconto em todos os produtos. Oferta válida até o final do mês!",
                "fileUrl": "https://exemplo.com/imagem-promocao.jpg",
                "suggestions": [
                    {
                        "type": "openUrl",
                        "title": "Ver Produtos",
                        "value": "https://loja.exemplo.com/promocao"
                    },
                    {
                        "type": "call",
                        "title": "Ligar",
                        "value": "1140001234"
                    },
                    {
                        "type": "reply",
                        "title": "Mais Info",
                        "value": "Quero mais informações"
                    }
                ]
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/rcs/single", json=data)
        print("Resposta Rich Card:", response.json())

async def example_carousel():
    """Exemplo de Carousel com múltiplos cards"""
    data = {
        "campaign_name": "Catálogo de Produtos",
        "account": "15885",
        "messages": [
            {
                "number": "5516982089942"
            }
        ],
        "content": {
            "carousel": [
                {
                    "title": "Smartphone Premium",
                    "description": "O melhor smartphone do mercado com câmera de 108MP e 5G.",
                    "fileUrl": "https://exemplo.com/smartphone.jpg",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Comprar",
                            "value": "https://loja.exemplo.com/smartphone"
                        },
                        {
                            "type": "reply",
                            "title": "Detalhes",
                            "value": "Quero detalhes do smartphone"
                        }
                    ]
                },
                {
                    "title": "Tablet Ultra",
                    "description": "Tablet com tela de 12 polegadas e processador octa-core.",
                    "fileUrl": "https://exemplo.com/tablet.jpg",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Comprar",
                            "value": "https://loja.exemplo.com/tablet"
                        },
                        {
                            "type": "reply",
                            "title": "Detalhes",
                            "value": "Quero detalhes do tablet"
                        }
                    ]
                },
                {
                    "title": "Fone Bluetooth",
                    "description": "Fone sem fio com cancelamento de ruído ativo.",
                    "fileUrl": "https://exemplo.com/fone.jpg",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Comprar",
                            "value": "https://loja.exemplo.com/fone"
                        },
                        {
                            "type": "reply",
                            "title": "Detalhes",
                            "value": "Quero detalhes do fone"
                        }
                    ]
                }
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/rcs/single", json=data)
        print("Resposta Carousel:", response.json())

async def example_webhook_message():
    """Exemplo de mensagem conversacional com webhook"""
    data = {
        "campaign_name": "Atendimento ao Cliente",
        "account": "15885",
        "webhook": "https://seu-dominio.com/webhook-rcs",
        "messages": [
            {
                "number": "5516982089942",
                "vars": {
                    "nome": "Carlos"
                }
            }
        ],
        "content": {
            "text": {
                "message": "Olá {{nome}}! Como posso ajudá-lo hoje?"
            }
        },
        "callback": "https://seu-dominio.com/callback"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/rcs/webhook", json=data)
        print("Resposta Webhook:", response.json())

async def example_create_template():
    """Exemplo de criação de template"""
    data = {
        "name": "Template Boas Vindas",
        "account": "15885",
        "content_type": "richCard",
        "template_data": {
            "title": "Bem-vindo {{nome}}!",
            "description": "Obrigado por se cadastrar em nossa plataforma. Explore nossos produtos e aproveite as ofertas especiais!",
            "fileUrl": "https://exemplo.com/boas-vindas.jpg",
            "suggestions": [
                {
                    "type": "openUrl",
                    "title": "Explorar",
                    "value": "https://loja.exemplo.com"
                },
                {
                    "type": "reply",
                    "title": "Ajuda",
                    "value": "Preciso de ajuda"
                }
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/rcs/templates", json=data)
        print("Resposta Criar Template:", response.json())

async def example_check_message_status():
    """Exemplo de consulta de status de mensagem"""
    message_id = 1  # ID da mensagem a consultar
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/messages/{message_id}")
        print("Status da mensagem:", response.json())

async def example_list_messages():
    """Exemplo de listagem de mensagens"""
    async with httpx.AsyncClient() as client:
        # Lista todas as mensagens
        response = await client.get(f"{BASE_URL}/api/messages")
        print("Todas as mensagens:", response.json())
        
        # Lista apenas mensagens enviadas
        response = await client.get(f"{BASE_URL}/api/messages?status=sent")
        print("Mensagens enviadas:", response.json())

async def main():
    """Executa todos os exemplos"""
    print("=== Exemplos de uso da API RCS Gateway ===\n")
    
    try:
        print("1. Mensagem de texto simples:")
        await example_text_message()
        print()
        
        print("2. Rich Card com botões:")
        await example_rich_card()
        print()
        
        print("3. Carousel de produtos:")
        await example_carousel()
        print()
        
        print("4. Mensagem conversacional com webhook:")
        await example_webhook_message()
        print()
        
        print("5. Criação de template:")
        await example_create_template()
        print()
        
        print("6. Consulta status de mensagem:")
        await example_check_message_status()
        print()
        
        print("7. Listagem de mensagens:")
        await example_list_messages()
        print()
        
    except Exception as e:
        print(f"Erro ao executar exemplos: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
