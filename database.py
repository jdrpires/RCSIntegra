from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/rcs_gateway")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from models import Base
    # Importar modelos de autenticação para criar as tabelas
    try:
        import auth_models
        print("✅ Tabelas de autenticação importadas")
    except ImportError as e:
        print(f"⚠️  Tabelas de autenticação não encontradas: {e}")
    
    # Importar modelos de mapeamento DE/PARA
    try:
        import client_mapping_models
        print("✅ Tabelas de mapeamento DE/PARA importadas")
    except ImportError as e:
        print(f"⚠️  Tabelas de mapeamento não encontradas: {e}")
    
    Base.metadata.create_all(bind=engine)
