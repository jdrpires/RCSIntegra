"""
Rotas de autenticação e gerenciamento de clientes
"""
from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from auth_service import AuthService
from auth_models import Client, User, APIKey, ClientTemplate
from auth_schemas import (
    ClientCreate, ClientUpdate, Client as ClientSchema,
    UserCreate, UserUpdate, User as UserSchema,
    APIKeyCreate, APIKey as APIKeySchema,
    ClientTemplateCreate, ClientTemplateUpdate, ClientTemplate as ClientTemplateSchema,
    LoginRequest, Token, TokenData
)

router = APIRouter()
security = HTTPBearer()


# Dependency para obter o serviço de autenticação
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


# Dependency para autenticação JWT
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Obtém usuário atual via JWT"""
    token_data = auth_service.verify_token(credentials.credentials)
    user = auth_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    return user


# Dependency para autenticação via API Key
def get_current_client_by_api_key(
    x_api_key: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> Client:
    """Obtém cliente atual via API Key"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key obrigatória"
        )
    
    api_key = auth_service.authenticate_api_key(x_api_key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
    
    client = auth_service.db.query(Client).filter(Client.id == api_key.client_id).first()
    if not client or not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente inativo"
        )
    
    return client


# Rotas de autenticação
@router.post("/auth/login", response_model=Token)
def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login de usuário"""
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Buscar cliente
    client = auth_service.db.query(Client).filter(Client.id == user.client_id).first()
    if not client or not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente inativo"
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={
            "sub": user.id,
            "client_id": client.id,
            "client_code": client.client_code,
            "scopes": list(user.permissions.keys()) if user.permissions else []
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": auth_service.access_token_expire_minutes * 60,
        "client_code": client.client_code
    }


@router.get("/auth/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Informações do usuário atual"""
    return current_user


# Rotas de gerenciamento de clientes (admin)
@router.post("/admin/clients", response_model=ClientSchema)
def create_client(
    client_data: ClientCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Criar novo cliente"""
    return auth_service.create_client(**client_data.dict())


@router.get("/admin/clients", response_model=List[ClientSchema])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Listar clientes"""
    return auth_service.db.query(Client).offset(skip).limit(limit).all()


@router.get("/admin/clients/{client_id}", response_model=ClientSchema)
def get_client(
    client_id: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obter cliente por ID"""
    client = auth_service.db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.put("/admin/clients/{client_id}", response_model=ClientSchema)
def update_client(
    client_id: str,
    client_data: ClientUpdate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Atualizar cliente"""
    client = auth_service.db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    for field, value in client_data.dict(exclude_unset=True).items():
        setattr(client, field, value)
    
    auth_service.db.commit()
    auth_service.db.refresh(client)
    return client


# Rotas de gerenciamento de usuários
@router.post("/admin/users", response_model=UserSchema)
def create_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Criar novo usuário"""
    return auth_service.create_user(**user_data.dict())


@router.get("/admin/users", response_model=List[UserSchema])
def list_users(
    client_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Listar usuários"""
    query = auth_service.db.query(User)
    if client_id:
        query = query.filter(User.client_id == client_id)
    return query.offset(skip).limit(limit).all()


@router.get("/admin/users/{user_id}", response_model=UserSchema)
def get_user(
    user_id: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obter usuário por ID"""
    user = auth_service.db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.put("/admin/users/{user_id}", response_model=UserSchema)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Atualizar usuário"""
    user = auth_service.db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password":
            user.hashed_password = AuthService(auth_service.db).get_password_hash(value)
        else:
            setattr(user, field, value)
    
    auth_service.db.commit()
    auth_service.db.refresh(user)
    return user


# Rotas de gerenciamento de API Keys
@router.post("/admin/api-keys", response_model=APIKeySchema)
def create_api_key(
    api_key_data: APIKeyCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Criar nova API Key"""
    return auth_service.create_api_key(**api_key_data.dict())


@router.get("/admin/api-keys", response_model=List[APIKeySchema])
def list_api_keys(
    client_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Listar API Keys"""
    query = auth_service.db.query(APIKey)
    if client_id:
        query = query.filter(APIKey.client_id == client_id)
    return query.offset(skip).limit(limit).all()


@router.delete("/admin/api-keys/{api_key_id}")
def delete_api_key(
    api_key_id: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Desativar API Key"""
    api_key = auth_service.db.query(APIKey).filter(APIKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key não encontrada")
    
    api_key.is_active = False
    auth_service.db.commit()
    
    return {"message": "API Key desativada com sucesso"}


# Rotas de templates do cliente
@router.post("/client/templates", response_model=ClientTemplateSchema)
def create_client_template(
    template_data: ClientTemplateCreate,
    current_user: User = Depends(get_current_user)
):
    """Criar template do cliente"""
    # Verificar se o usuário pode criar templates
    if not current_user.permissions.get("can_use_templates", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não tem permissão para criar templates"
        )
    
    template = ClientTemplate(**template_data.dict())
    current_user.client.db.add(template)
    current_user.client.db.commit()
    current_user.client.db.refresh(template)
    
    return template


@router.get("/client/templates", response_model=List[ClientTemplateSchema])
def list_client_templates(
    current_user: User = Depends(get_current_user)
):
    """Listar templates do cliente"""
    auth_service = AuthService(current_user.client.db)
    return auth_service.get_client_templates(current_user.client_id)
