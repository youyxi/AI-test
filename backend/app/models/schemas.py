"""
Pydantic models - API request/response
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, EmailStr


# ========== User Models ==========
class UserRegister(BaseModel):
    """User registration"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """User login"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """Update user profile"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserSettingsUpdate(BaseModel):
    """Update user settings"""
    theme: Optional[str] = None          # light, dark, auto
    language: Optional[str] = None       # zh, en
    default_model: Optional[str] = None
    default_provider: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = None
    send_with_enter: Optional[bool] = None


class UserResponse(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    nickname: str
    avatar: str
    is_active: bool
    settings: Dict[str, Any] = {}
    created_at: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ========== Chat Models ==========
class ChatMessage(BaseModel):
    """Chat message"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Chat request"""
    messages: List[ChatMessage]
    model: str = "gpt-3.5-turbo"
    provider: str = "openai"
    stream: bool = False
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = None
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat response"""
    id: str
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ========== Conversation Models ==========
class ConversationCreate(BaseModel):
    """Create conversation"""
    title: str = "New Chat"
    model: str
    provider: str


class ConversationUpdate(BaseModel):
    """Update conversation"""
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: int
    title: str
    model: str
    provider: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []


# ========== Model Info ==========
class ModelInfo(BaseModel):
    """Model info"""
    id: str
    name: str
    provider: str
    provider_name: str
    type: str
    max_tokens: int
    supports_stream: bool = True
    supports_vision: bool = False


class ProviderInfo(BaseModel):
    """Provider info"""
    id: str
    name: str
    models: List[ModelInfo]
    configured: bool = False


# ========== Common ==========
class SuccessResponse(BaseModel):
    """Success response"""
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
