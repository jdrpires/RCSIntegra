#!/usr/bin/env python3
"""
Script para simular callbacks de eventos RCS
"""

import httpx
import asyncio
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"

async def simulate_message_lifecycle(message_id: int, phone_number: str):
    """Simula o ciclo completo de vida de uma mensagem RCS"""
    
    print(f"🎭 Simulando ciclo de vida da mensagem {message_id}")
    print(f"📱 Número: {phone_number}")
    
    # 1. Mensagem entregue (após 2-5 segundos)
    await asyncio.sleep(random.uniform(2, 5))
    await send_callback({
        "event": "delivered",
        "message_id": message_id,
        "phone_number": phone_number,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, "📦 Entregue")
    
    # 2. Mensagem lida (após 10-30 segundos)
    await asyncio.sleep(random.uniform(10, 30))
    await send_callback({
        "event": "read",
        "message_id": message_id,
        "phone_number": phone_number,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, "👁️ Lida")
    
    # 3. Mensagem aberta (após 5-15 segundos)
    await asyncio.sleep(random.uniform(5, 15))
    await send_callback({
        "event": "opened",
        "message_id": message_id,
        "phone_number": phone_number,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_agent": "Mozilla/5.0 (Android 12; Mobile; RCS)",
        "device_info": {
            "platform": "Android",
            "version": "12",
            "device": "Samsung Galaxy S21"
        }
    }, "📱 Aberta")
    
    # 4. Simula interações (50% chance)
    if random.random() < 0.5:
        interaction_type = random.choice(["click", "reply"])
        
        if interaction_type == "click":
            await asyncio.sleep(random.uniform(5, 20))
            await send_callback({
                "event": "clicked",
                "message_id": message_id,
                "phone_number": phone_number,
                "button_value": "Ver Produtos",
                "interaction_type": "button_click",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }, "🖱️ Botão clicado")
        
        elif interaction_type == "reply":
            await asyncio.sleep(random.uniform(10, 60))
            replies = [
                "Interessado!",
                "Quero mais informações",
                "Obrigado!",
                "Como faço para comprar?",
                "Perfeito!"
            ]
            await send_callback({
                "event": "replied",
                "message_id": message_id,
                "phone_number": phone_number,
                "reply_text": random.choice(replies),
                "interaction_type": "reply",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }, "💬 Respondeu")

async def send_callback(callback_data: dict, description: str):
    """Envia um callback para o endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/api/rcs/callback", json=callback_data)
            
            if response.status_code == 200:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} - Erro {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {description} - Erro: {str(e)}")

async def get_latest_message():
    """Busca a mensagem mais recente para simular eventos"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/messages?limit=1")
            
            if response.status_code == 200:
                messages = response.json()
                if messages:
                    return messages[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar mensagem: {str(e)}")
            return None

async def simulate_multiple_events():
    """Simula eventos para múltiplas mensagens"""
    print("🎭 Simulador de Eventos RCS")
    print("=" * 50)
    
    # Busca mensagem mais recente
    message = await get_latest_message()
    
    if not message:
        print("❌ Nenhuma mensagem encontrada para simular eventos")
        print("💡 Envie uma mensagem primeiro usando os scripts de teste")
        return
    
    message_id = message['id']
    phone_number = message['phone_number']
    
    print(f"📨 Usando mensagem ID: {message_id}")
    print(f"📱 Número: {phone_number}")
    print()
    
    # Simula ciclo de vida
    await simulate_message_lifecycle(message_id, phone_number)
    
    print("\n🎉 Simulação concluída!")
    print("\n📊 Verifique os resultados:")
    print(f"   curl {BASE_URL}/api/messages/{message_id}/stats")
    print(f"   curl {BASE_URL}/api/messages/{message_id}/events")

async def simulate_custom_event():
    """Permite simular um evento customizado"""
    print("🎛️ Simulador de Evento Customizado")
    print("=" * 40)
    
    message_id = input("ID da mensagem: ").strip()
    if not message_id.isdigit():
        print("❌ ID da mensagem deve ser um número")
        return
    
    phone_number = input("Número de telefone: ").strip()
    if not phone_number:
        print("❌ Número de telefone é obrigatório")
        return
    
    print("\nTipos de evento disponíveis:")
    print("1. delivered - Mensagem entregue")
    print("2. read - Mensagem lida")
    print("3. opened - Mensagem aberta")
    print("4. clicked - Botão clicado")
    print("5. replied - Usuário respondeu")
    print("6. failed - Falha na entrega")
    
    event_choice = input("\nEscolha o tipo de evento (1-6): ").strip()
    
    event_types = {
        "1": "delivered",
        "2": "read", 
        "3": "opened",
        "4": "clicked",
        "5": "replied",
        "6": "failed"
    }
    
    event_type = event_types.get(event_choice)
    if not event_type:
        print("❌ Opção inválida")
        return
    
    # Dados base do callback
    callback_data = {
        "event": event_type,
        "message_id": int(message_id),
        "phone_number": phone_number,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Dados específicos por tipo
    if event_type == "clicked":
        button_value = input("Valor do botão clicado: ").strip() or "Botão Teste"
        callback_data.update({
            "button_value": button_value,
            "interaction_type": "button_click"
        })
    
    elif event_type == "replied":
        reply_text = input("Texto da resposta: ").strip() or "Resposta teste"
        callback_data.update({
            "reply_text": reply_text,
            "interaction_type": "reply"
        })
    
    elif event_type == "failed":
        error_msg = input("Mensagem de erro: ").strip() or "Falha na entrega"
        callback_data.update({
            "status": "failed",
            "error_message": error_msg
        })
    
    # Envia o callback
    await send_callback(callback_data, f"Evento {event_type}")
    
    print(f"\n✅ Evento {event_type} simulado!")
    print(f"🔍 Verifique: curl {BASE_URL}/api/messages/{message_id}")

async def main():
    print("🎭 Simulador de Callbacks RCS")
    print("=" * 40)
    
    print("Escolha uma opção:")
    print("1. 🤖 Simular ciclo completo (automático)")
    print("2. 🎛️ Simular evento específico (manual)")
    print("3. 📊 Ver estatísticas de mensagem")
    
    choice = input("\nOpção (1-3): ").strip()
    
    if choice == "1":
        await simulate_multiple_events()
    elif choice == "2":
        await simulate_custom_event()
    elif choice == "3":
        message_id = input("ID da mensagem: ").strip()
        if message_id.isdigit():
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/api/messages/{message_id}/stats")
                if response.status_code == 200:
                    stats = response.json()
                    print(f"\n📊 Estatísticas da mensagem {message_id}:")
                    print(json.dumps(stats, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ Erro ao buscar estatísticas: {response.status_code}")
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    asyncio.run(main())
