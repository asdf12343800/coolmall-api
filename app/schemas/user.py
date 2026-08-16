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

class RegisterRequest(BaseModel):
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    sms_code: str = Field(..., alias="smsCode", description="短信验证码", min_length=4, max_length=6)
    password: str = Field(..., description="密码", min_length=6)
    confirm_password: str = Field(..., alias="confirmPassword", description="确认密码", min_length=6)

class RegisterTokenData(BaseModel):
    token: str = Field(..., description="访问令牌")
    expire: int = Field(..., description="访问令牌过期时间(秒)")
    refresh_token: str = Field(..., alias="refreshToken", description="刷新令牌")
    refresh_expire: int = Field(..., alias="refreshExpire", description="刷新令牌过期时间(秒)")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., alias="refreshToken", description="刷新令牌")

class PhoneLoginRequest(BaseModel):
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    sms_code: str = Field(..., alias="smsCode", description="短信验证码", min_length=4, max_length=6)

class PasswordLoginRequest(BaseModel):
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    password: str = Field(..., description="密码", min_length=6)

class CaptchaData(BaseModel):
    data: str = Field(..., description="图片base64编码(data:image/png;base64,...)")
    captcha_id: str = Field(..., alias="captchaId", description="验证码ID")

class UpdatePersonRequest(BaseModel):
    username: Optional[str] = Field(default=None, description="用户名/昵称")
    avatar: Optional[str] = Field(default=None, description="头像URL")
    email: Optional[EmailStr] = Field(default=None, description="邮箱")
    full_name: Optional[str] = Field(default=None, description="真实姓名")

class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="原密码", min_length=6)
    new_password: str = Field(..., alias="newPassword", description="新密码", min_length=6)
    confirm_password: str = Field(..., alias="confirmPassword", description="确认新密码", min_length=6)

class BindPhoneRequest(BaseModel):
    phone: str = Field(..., description="待绑定的手机号", min_length=11, max_length=11)
    sms_code: str = Field(..., alias="smsCode", description="短信验证码", min_length=4, max_length=6)