"""
Serviço de autenticação JWT e gerenciamento de clientes
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from auth_models import Client, User, APIKey, ClientTemplate, MessageLog
from auth_schemas import TokenData
import uuid


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas
    
    # Métodos de hash de senha
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Gera hash da senha"""
        return self.pwd_context.hash(password)
    
    # Métodos JWT
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            client_id: str = payload.get("client_id")
            client_code: str = payload.get("client_code")
            scopes: List[str] = payload.get("scopes", [])
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            token_data = TokenData(
                user_id=user_id,
                client_id=client_id,
                client_code=client_code,
                scopes=scopes
            )
            return token_data
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    # Métodos de autenticação
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autentica usuário"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def authenticate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Autentica via API Key"""
        key = self.db.query(APIKey).filter(APIKey.api_key == api_key).first()
        if not key:
            return None
        if not key.is_active:
            return None
        if key.expires_at and key.expires_at < datetime.utcnow():
            return None
        
        # Atualizar último uso
        key.last_used = datetime.utcnow()
        self.db.commit()
        
        return key
    
    # Métodos de gerenciamento de clientes
    def create_client(self, name: str, email: str, rcs_account: str, **kwargs) -> Client:
        """Cria novo cliente"""
        # Verificar se email já existe
        existing = self.db.query(Client).filter(Client.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Gerar código único do cliente
        client_code = self.generate_client_code()
        
        client = Client(
            name=name,
            email=email,
            client_code=client_code,
            rcs_account=rcs_account,
            **kwargs
        )
        
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        
        return client
    
    def generate_client_code(self) -> str:
        """Gera código único para cliente"""
        while True:
            code = f"CLI_{secrets.token_hex(4).upper()}"
            existing = self.db.query(Client).filter(Client.client_code == code).first()
            if not existing:
                return code
    
    def create_user(self, username: str, email: str, name: str, password: str, client_id: str, **kwargs) -> User:
        """Cria novo usuário"""
        # Verificar se username já existe
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já existe"
            )
        
        # Verificar se cliente existe
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        hashed_password = self.get_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            name=name,
            hashed_password=hashed_password,
            client_id=client_id,
            **kwargs
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_api_key(self, client_id: str, key_name: str, **kwargs) -> APIKey:
        """Cria nova API Key"""
        # Verificar se cliente existe
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Gerar API Key única
        api_key = self.generate_api_key()
        
        key = APIKey(
            client_id=client_id,
            key_name=key_name,
            api_key=api_key,
            **kwargs
        )
        
        self.db.add(key)
        self.db.commit()
        self.db.refresh(key)
        
        return key
    
    def generate_api_key(self) -> str:
        """Gera API Key única"""
        while True:
            # Gerar chave de 32 bytes (256 bits)
            key = secrets.token_urlsafe(32)
            existing = self.db.query(APIKey).filter(APIKey.api_key == key).first()
            if not existing:
                return key
    
    # Métodos de consulta
    def get_client_by_code(self, client_code: str) -> Optional[Client]:
        """Busca cliente por código"""
        return self.db.query(Client).filter(
            Client.client_code == client_code,
            Client.is_active == True
        ).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID"""
        return self.db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
    
    def get_client_templates(self, client_id: str) -> List[ClientTemplate]:
        """Busca templates do cliente"""
        return self.db.query(ClientTemplate).filter(
            ClientTemplate.client_id == client_id,
            ClientTemplate.is_active == True
        ).all()
    
    def log_message_request(self, client_id: str, user_id: Optional[str], rcs_message_id: str, 
                           endpoint_used: str, request_data: dict, success: bool, 
                           error_message: Optional[str] = None) -> MessageLog:
        """Registra log de mensagem enviada"""
        log = MessageLog(
            client_id=client_id,
            user_id=user_id,
            rcs_message_id=rcs_message_id,
            endpoint_used=endpoint_used,
            request_data=request_data,
            success=success,
            error_message=error_message
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
