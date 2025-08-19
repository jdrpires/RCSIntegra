#!/usr/bin/env python3
"""
Script para inicializar banco de dados com autenticação
"""
import logging
from sqlalchemy import create_engine
from database import DATABASE_URL, Base

# Importar modelos na ordem correta (primeiro os que não têm FK)
from models import RCSMessage, RCSTemplate, RCSCallback
from auth_models import Client, User, APIKey, ClientTemplate, MessageLog

from auth_service import AuthService
from sqlalchemy.orm import sessionmaker
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa o banco de dados com todas as tabelas"""
    
    logger.info("🔧 Inicializando banco de dados com autenticação...")
    
    try:
        # Criar engine
        engine = create_engine(DATABASE_URL)
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso!")
        
        # Listar tabelas criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"📋 Tabelas disponíveis: {tables}")
        
        # Criar dados de exemplo
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Verificar se já existem clientes
            existing_clients = db.query(Client).count()
            if existing_clients == 0:
                logger.info("🎯 Criando dados de exemplo...")
                
                auth_service = AuthService(db)
                
                # Criar cliente de exemplo
                sample_client = auth_service.create_client(
                    name="Empresa Exemplo Ltda",
                    email="contato@exemplo.com",
                    rcs_account="15886",  # Account da Eugen
                    api_token="Mjk5MjpvaFdTOU9OaDBZOURTZUJ0TnJuRVp5UDFtTzlGb3c=",
                    allowed_message_types=["basic", "single"],
                    max_messages_per_day="1000",
                    callback_url="https://exemplo.com/callback"
                )
                
                logger.info(f"✅ Cliente criado: {sample_client.name} (Código: {sample_client.client_code})")
                
                # Criar usuário administrador
                admin_user = auth_service.create_user(
                    username="admin",
                    email="admin@exemplo.com",
                    name="Administrador",
                    password="admin123",
                    client_id=sample_client.id,
                    permissions={
                        "can_send_basic": True,
                        "can_send_single": True,
                        "can_use_templates": True,
                        "can_view_reports": True
                    }
                )
                
                logger.info(f"✅ Usuário criado: {admin_user.username}")
                
                # Criar API Key para o cliente
                api_key = auth_service.create_api_key(
                    client_id=sample_client.id,
                    key_name="Chave Principal",
                    scopes=["send_messages", "view_messages"],
                    requests_per_minute="60",
                    requests_per_day="1000"
                )
                
                logger.info(f"✅ API Key criada: {api_key.api_key}")
                
                # Criar segundo cliente para testes
                test_client = auth_service.create_client(
                    name="Cliente Teste",
                    email="teste@exemplo.com",
                    rcs_account="15886",
                    allowed_message_types=["basic"],
                    max_messages_per_day="500"
                )
                
                # Criar usuário para o cliente teste
                test_user = auth_service.create_user(
                    username="teste",
                    email="teste@teste.com",
                    name="Usuário Teste",
                    password="teste123",
                    client_id=test_client.id,
                    permissions={
                        "can_send_basic": True,
                        "can_send_single": False,
                        "can_use_templates": True,
                        "can_view_reports": True
                    }
                )
                
                # Criar API Key para cliente teste
                test_api_key = auth_service.create_api_key(
                    client_id=test_client.id,
                    key_name="Chave Teste",
                    scopes=["send_messages"],
                    requests_per_minute="30",
                    requests_per_day="500"
                )
                
                logger.info("🎉 Dados de exemplo criados com sucesso!")
                logger.info("=" * 60)
                logger.info("📋 INFORMAÇÕES DE ACESSO:")
                logger.info("=" * 60)
                logger.info(f"🏢 Cliente 1: {sample_client.name}")
                logger.info(f"   📧 Email: {sample_client.email}")
                logger.info(f"   🔑 Código: {sample_client.client_code}")
                logger.info(f"   🔐 API Key: {api_key.api_key}")
                logger.info(f"   👤 Usuário: {admin_user.username} / admin123")
                logger.info("")
                logger.info(f"🏢 Cliente 2: {test_client.name}")
                logger.info(f"   📧 Email: {test_client.email}")
                logger.info(f"   🔑 Código: {test_client.client_code}")
                logger.info(f"   🔐 API Key: {test_api_key.api_key}")
                logger.info(f"   👤 Usuário: {test_user.username} / teste123")
                logger.info("=" * 60)
                
            else:
                logger.info("ℹ️  Dados já existem, pulando criação de exemplos")
                
                # Mostrar clientes existentes
                clients = db.query(Client).all()
                logger.info("📋 Clientes existentes:")
                for client in clients:
                    logger.info(f"   - {client.name} (Código: {client.client_code})")
                    
                    # Mostrar API Keys do cliente
                    api_keys = db.query(APIKey).filter(APIKey.client_id == client.id).all()
                    for key in api_keys:
                        if key.is_active:
                            logger.info(f"     🔐 API Key: {key.api_key}")
                
        finally:
            db.close()
        
        logger.info("🎉 Inicialização concluída com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n✅ Banco de dados inicializado com sucesso!")
        print("🚀 Agora você pode executar a aplicação com: python main_with_auth.py")
    else:
        print("\n❌ Falha na inicialização do banco de dados!")
        exit(1)
