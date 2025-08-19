#!/usr/bin/env python3
"""
Debug do client service
"""
import asyncio
from sqlalchemy.orm import sessionmaker
from database import engine
from client_service import ClientRCSService
from auth_schemas import ClientSendMessageRequest

async def test_debug():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        client_service = ClientRCSService(db)
        
        request = ClientSendMessageRequest(
            client_code="CLI_7FB141C8",
            message_type="basic",
            phone_numbers=["5511999999999"],
            content={
                "text": {
                    "message": "Teste debug"
                }
            }
        )
        
        print("Enviando mensagem...")
        result = await client_service.send_message(request)
        print(f"Resultado: {result}")
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_debug())
