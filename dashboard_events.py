#!/usr/bin/env python3
"""
Dashboard simples para visualizar eventos RCS em tempo real
"""

import httpx
import asyncio
import json
from datetime import datetime
import os

BASE_URL = "http://localhost:8000"

async def show_real_time_events():
    """Mostra eventos em tempo real"""
    print("📊 Dashboard de Eventos RCS - Tempo Real")
    print("=" * 60)
    print("Pressione Ctrl+C para sair\n")
    
    last_event_id = 0
    
    while True:
        try:
            async with httpx.AsyncClient() as client:
                # Busca eventos mais recentes
                response = await client.get(f"{BASE_URL}/api/events?limit=10")
                
                if response.status_code == 200:
                    events = response.json()
                    
                    # Filtra apenas eventos novos
                    new_events = [e for e in events if e['id'] > last_event_id]
                    
                    if new_events:
                        for event in reversed(new_events):  # Mostra do mais antigo para o mais novo
                            timestamp = datetime.fromisoformat(event['received_at'].replace('Z', '+00:00'))
                            
                            # Emoji por tipo de evento
                            emoji_map = {
                                'delivered': '📦',
                                'read': '👁️',
                                'opened': '📱',
                                'clicked': '🖱️',
                                'replied': '💬',
                                'failed': '❌'
                            }
                            
                            emoji = emoji_map.get(event['event_type'], '📨')
                            
                            print(f"{timestamp.strftime('%H:%M:%S')} {emoji} {event['event_type'].upper()}")
                            print(f"   📱 {event['phone_number']}")
                            
                            if event['interaction_value']:
                                print(f"   💬 {event['interaction_value']}")
                            
                            print()
                        
                        last_event_id = max(e['id'] for e in new_events)
            
            await asyncio.sleep(2)  # Verifica a cada 2 segundos
            
        except KeyboardInterrupt:
            print("\n👋 Dashboard encerrado!")
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            await asyncio.sleep(5)

async def show_message_stats():
    """Mostra estatísticas de mensagens"""
    print("📊 Estatísticas de Mensagens")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        try:
            # Busca mensagens recentes
            response = await client.get(f"{BASE_URL}/api/messages?limit=10")
            
            if response.status_code == 200:
                messages = response.json()
                
                if not messages:
                    print("ℹ️  Nenhuma mensagem encontrada")
                    return
                
                print(f"📨 {len(messages)} mensagens mais recentes:\n")
                
                for msg in messages:
                    print(f"🆔 ID: {msg['id']}")
                    print(f"📱 Para: {msg['phone_number']}")
                    print(f"📊 Status: {msg['status']}")
                    print(f"📅 Criada: {msg['created_at']}")
                    
                    # Busca estatísticas detalhadas
                    stats_response = await client.get(f"{BASE_URL}/api/messages/{msg['id']}/stats")
                    if stats_response.status_code == 200:
                        stats = stats_response.json()
                        
                        if stats['delivered_at']:
                            print(f"   📦 Entregue: {stats['delivered_at']}")
                        if stats['read_at']:
                            print(f"   👁️ Lida: {stats['read_at']}")
                        if stats['opened_at']:
                            print(f"   📱 Aberta: {stats['opened_at']}")
                        if stats['click_count'] > 0:
                            print(f"   🖱️ Clicks: {stats['click_count']}")
                        if stats['reply_count'] > 0:
                            print(f"   💬 Respostas: {stats['reply_count']}")
                    
                    print("   " + "-" * 30)
                    
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

async def show_campaign_summary():
    """Mostra resumo por campanha"""
    print("📈 Resumo por Campanha")
    print("=" * 30)
    
    # Lista campanhas disponíveis
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/messages")
            
            if response.status_code == 200:
                messages = response.json()
                campaigns = list(set(msg['campaign_name'] for msg in messages if msg['campaign_name']))
                
                if not campaigns:
                    print("ℹ️  Nenhuma campanha encontrada")
                    return
                
                print(f"📋 {len(campaigns)} campanha(s) encontrada(s):\n")
                
                for campaign in campaigns:
                    print(f"🎯 Campanha: {campaign}")
                    
                    # Busca resumo da campanha
                    summary_response = await client.get(f"{BASE_URL}/api/campaigns/{campaign}/summary")
                    if summary_response.status_code == 200:
                        summary = summary_response.json()
                        
                        print(f"   📨 Enviadas: {summary['total_sent']}")
                        print(f"   📦 Entregues: {summary['total_delivered']} ({summary['delivery_rate']}%)")
                        print(f"   👁️ Lidas: {summary['total_read']} ({summary['read_rate']}%)")
                        print(f"   🖱️ Clicks: {summary['total_clicked']}")
                        print(f"   💬 Respostas: {summary['total_replied']}")
                        print(f"   📊 Engajamento: {summary['engagement_rate']}%")
                    
                    print("   " + "-" * 30)
                    
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

async def main():
    print("📊 Dashboard de Eventos RCS")
    print("=" * 40)
    
    while True:
        print("\nEscolha uma opção:")
        print("1. 📊 Eventos em tempo real")
        print("2. 📨 Estatísticas de mensagens")
        print("3. 📈 Resumo por campanha")
        print("4. 🔄 Atualizar tela")
        print("5. 🚪 Sair")
        
        choice = input("\nOpção (1-5): ").strip()
        
        # Limpa a tela
        os.system('clear' if os.name == 'posix' else 'cls')
        
        if choice == "1":
            await show_real_time_events()
        elif choice == "2":
            await show_message_stats()
        elif choice == "3":
            await show_campaign_summary()
        elif choice == "4":
            continue
        elif choice == "5":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")
        
        if choice != "1":  # Não pausa se for tempo real
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    asyncio.run(main())
