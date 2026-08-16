from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, TypeVar, Generic

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=1000, description="响应码，1000表示成功")
    data: Optional[T] = Field(default=None, description="响应数据")
    message: str = Field(default="success", description="响应消息")

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class SmsCodeRequest(BaseModel):
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    captcha_id: str = Field(..., alias="captchaId", description="图片验证码ID")
    code: str = Field(..., description="图片验证码", min_length=4, max_length=6)