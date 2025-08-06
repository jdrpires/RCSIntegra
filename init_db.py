#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
"""

from database import engine, create_tables
from models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        logger.info("Criando tabelas do banco de dados...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
        
        # Lista as tabelas criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tabelas disponíveis: {tables}")
        
        # Verifica se as novas colunas foram adicionadas
        if 'rcs_messages' in tables:
            columns = [col['name'] for col in inspector.get_columns('rcs_messages')]
            logger.info(f"Colunas da tabela rcs_messages: {columns}")
            
            # Verifica se as novas colunas de tracking existem
            tracking_columns = ['delivered_at', 'read_at', 'opened_at', 'click_count', 'reply_count']
            missing_columns = [col for col in tracking_columns if col not in columns]
            
            if missing_columns:
                logger.warning(f"⚠️  Colunas de tracking não encontradas: {missing_columns}")
                logger.info("💡 Execute: DROP TABLE rcs_messages, rcs_callbacks; e rode este script novamente")
            else:
                logger.info("✅ Todas as colunas de tracking estão presentes!")
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise e

def reset_database():
    """Reseta o banco de dados (CUIDADO: apaga todos os dados!)"""
    try:
        logger.warning("⚠️  RESETANDO BANCO DE DADOS - TODOS OS DADOS SERÃO PERDIDOS!")
        
        # Drop todas as tabelas
        Base.metadata.drop_all(bind=engine)
        logger.info("Tabelas removidas")
        
        # Recria todas as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas recriadas com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao resetar banco: {str(e)}")
        raise e

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        confirm = input("⚠️  Tem certeza que deseja RESETAR o banco? (digite 'RESET' para confirmar): ")
        if confirm == "RESET":
            reset_database()
        else:
            print("❌ Reset cancelado")
    else:
        init_database()
