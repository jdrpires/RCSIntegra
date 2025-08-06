import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db, Base
from models import RCSMessage, RCSTemplate, RCSCallback

# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_phone_numbers():
    """Sample phone numbers for testing."""
    return [
        "5511999999999",
        "5521888888888",
        "5531777777777"
    ]

@pytest.fixture
def sample_account():
    """Sample account ID for testing."""
    return "test_account_123"

@pytest.fixture
def sample_text_content():
    """Sample text content for testing."""
    return {
        "text": {
            "message": "Olá {{nome}}, esta é uma mensagem de teste!"
        }
    }

@pytest.fixture
def sample_rich_card_content():
    """Sample rich card content for testing."""
    return {
        "richCard": {
            "title": "Oferta Especial!",
            "description": "Aproveite 20% de desconto em todos os produtos.",
            "fileUrl": "https://exemplo.com/promocao.jpg",
            "suggestions": [
                {
                    "type": "openUrl",
                    "title": "Ver Produtos",
                    "value": "https://loja.exemplo.com"
                },
                {
                    "type": "call",
                    "title": "Ligar",
                    "value": "1140001234"
                }
            ]
        }
    }

@pytest.fixture
def sample_carousel_content():
    """Sample carousel content for testing."""
    return {
        "carousel": {
            "cards": [
                {
                    "title": "Produto 1",
                    "description": "Descrição do produto 1",
                    "fileUrl": "https://exemplo.com/produto1.jpg",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Comprar",
                            "value": "https://loja.exemplo.com/produto1"
                        }
                    ]
                },
                {
                    "title": "Produto 2",
                    "description": "Descrição do produto 2",
                    "fileUrl": "https://exemplo.com/produto2.jpg",
                    "suggestions": [
                        {
                            "type": "openUrl",
                            "title": "Comprar",
                            "value": "https://loja.exemplo.com/produto2"
                        }
                    ]
                }
            ]
        }
    }

@pytest.fixture
def mock_rcs_success_response():
    """Mock successful RCS API response."""
    return {
        "success": True,
        "message_id": "msg_123456789",
        "status": "sent",
        "timestamp": "2024-01-01T12:00:00Z"
    }

@pytest.fixture
def mock_rcs_error_response():
    """Mock error RCS API response."""
    return {
        "success": False,
        "error": "Invalid phone number",
        "code": "INVALID_PHONE"
    }
