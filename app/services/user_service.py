import random
import time
import uuid
import io
import base64
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, SmsCodeRequest, RegisterRequest, RegisterTokenData, RefreshTokenRequest, PhoneLoginRequest, PasswordLoginRequest, CaptchaData, UpdatePersonRequest, UpdatePasswordRequest, BindPhoneRequest
from app.core.config import settings
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, user_data: UserCreate) -> User:
        hashed_password = self.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_phone(self, phone: str) -> User | None:
        return self.db.query(User).filter(User.phone == phone).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = self.get_user(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = self.get_password_hash(
                update_data.pop("password")
            )
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def send_sms_code(self, req: SmsCodeRequest) -> str:
        """发送短信验证码，返回生成的4位验证码"""
        # TODO: 校验图片验证码 captcha_id + code（需要结合 Redis 或缓存实现）
        # TODO: 调用实际短信服务商SDK发送短信到 req.phone
        # 生成4位随机数字验证码
        sms_code = f"{random.randint(0, 9999):04d}"
        # TODO: 将手机号+验证码存入缓存（如Redis），设置有效期，用于后续登录校验
        return sms_code
    
    def _create_token(self, user_id: int, is_refresh: bool = False) -> tuple[str, int]:
        """生成JWT token，返回(token, 过期秒数)"""
        now = int(time.time())
        expire_seconds = settings.REFRESH_TOKEN_EXPIRE if is_refresh else settings.ACCESS_TOKEN_EXPIRE
        payload = {
            "exp": now + expire_seconds,
            "created": now,
            "userType": settings.USER_TYPE,
            "userId": user_id,
            "isRefresh": is_refresh,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token, expire_seconds
    
    def register(self, req: RegisterRequest) -> RegisterTokenData:
        """用户注册，返回token信息"""
        # TODO: 校验短信验证码（从缓存中取手机号对应的验证码进行比对）
        # 校验两次密码一致
        if req.password != req.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码与确认密码不一致"
            )
        # 校验手机号是否已注册
        if self.get_user_by_phone(req.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已注册"
            )
        # 创建用户
        hashed_password = self.get_password_hash(req.password)
        user = User(
            phone=req.phone,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        # 生成 token
        access_token, expire = self._create_token(user.id, is_refresh=False)
        refresh_token, refresh_expire = self._create_token(user.id, is_refresh=True)
        return RegisterTokenData(
            token=access_token,
            expire=expire,
            refresh_token=refresh_token,
            refresh_expire=refresh_expire,
        )
    
    def _decode_token(self, token: str) -> dict:
        """解码JWT token并校验，返回payload"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token无效或已过期"
            )
        return payload
    
    def refresh_token(self, req: RefreshTokenRequest) -> RegisterTokenData:
        """刷新访问令牌，返回新的token信息（refresh token保持不变）"""
        payload = self._decode_token(req.refresh_token)
        # 校验必须是 refresh token
        if not payload.get("isRefresh"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="传入的token不是refresh token"
            )
        user_id = payload.get("userId")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token缺少userId信息"
            )
        # 校验用户存在
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        # 生成新的 access token；refresh token 保持原值继续使用
        access_token, expire = self._create_token(user_id, is_refresh=False)
        refresh_expire = settings.REFRESH_TOKEN_EXPIRE
        return RegisterTokenData(
            token=access_token,
            expire=expire,
            refresh_token=req.refresh_token,
            refresh_expire=refresh_expire,
        )
    
    def login_by_phone(self, req: PhoneLoginRequest) -> RegisterTokenData:
        """手机号 + 短信验证码登录，返回token信息"""
        # TODO: 校验短信验证码（从缓存中取手机号对应的验证码进行比对）
        # 校验手机号是否已注册
        user = self.get_user_by_phone(req.phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号尚未注册"
            )
        # 校验用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
        # 生成 token
        access_token, expire = self._create_token(user.id, is_refresh=False)
        refresh_token, refresh_expire = self._create_token(user.id, is_refresh=True)
        return RegisterTokenData(
            token=access_token,
            expire=expire,
            refresh_token=refresh_token,
            refresh_expire=refresh_expire,
        )
    
    def login_by_password(self, req: PasswordLoginRequest) -> RegisterTokenData:
        """手机号 + 密码登录，返回token信息"""
        # 校验手机号是否已注册
        user = self.get_user_by_phone(req.phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号或密码错误"
            )
        # 校验密码
        if not self.verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号或密码错误"
            )
        # 校验用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
        # 生成 token
        access_token, expire = self._create_token(user.id, is_refresh=False)
        refresh_token, refresh_expire = self._create_token(user.id, is_refresh=True)
        return RegisterTokenData(
            token=access_token,
            expire=expire,
            refresh_token=refresh_token,
            refresh_expire=refresh_expire,
        )
    
    def generate_captcha(self, captcha_type: str, width: int, height: int) -> CaptchaData:
        """生成图片验证码，返回图片base64 + captchaId"""
        captcha_id = str(uuid.uuid4())
        try:
            from captcha.image import ImageCaptcha
            chars = "0123456789"
            code = "".join(random.choices(chars, k=4))
            image_captcha = ImageCaptcha(width=width, height=height)
            data_bytes = image_captcha.generate(code)
            image_bytes = data_bytes.getvalue()
        except Exception:
            # fallback: 使用 Pillow 生成一张简单的占位图
            try:
                from PIL import Image, ImageDraw, ImageFont
                chars = "0123456789"
                code = "".join(random.choices(chars, k=4))
                img = Image.new("RGB", (width, height), color=(240, 240, 240))
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", int(height * 0.7))
                except Exception:
                    font = ImageFont.load_default()
                draw.text((width * 0.15, height * 0.15), code, fill=(50, 50, 50), font=font)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                image_bytes = buf.getvalue()
            except Exception:
                # 二次 fallback: 返回一个最小的 1x1 PNG
                image_bytes = base64.b64decode(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFrwJhFpD1PgAAAABJRU5ErkJggg=="
                )
        base64_data = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = "data:image/png;base64," + base64_data
        # TODO: 将 captcha_id -> code 存入缓存，用于后续 smsCode 接口校验
        return CaptchaData(data=data_uri, captcha_id=captcha_id)
    
    def _get_user_id_from_token(self, authorization: str) -> int:
        """从 Authorization header 解析 access token，返回 userId"""
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少Authorization头"
            )
        token = authorization.replace("Bearer ", "").strip()
        payload = self._decode_token(token)
        # 不能用 refresh token 来操作个人资料
        if payload.get("isRefresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请使用access token"
            )
        user_id = payload.get("userId")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token缺少userId信息"
            )
        return user_id
    
    def update_person(self, req: UpdatePersonRequest, authorization: str) -> dict:
        """更新当前登录用户的个人资料"""
        user_id = self._get_user_id_from_token(authorization)
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        update_data = req.model_dump(exclude_unset=True)
        # 校验用户名唯一性
        if "username" in update_data and update_data["username"]:
            existing = self.get_user_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该用户名已被使用"
                )
        # 校验邮箱唯一性
        if "email" in update_data and update_data["email"]:
            existing = self.get_user_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该邮箱已被使用"
                )
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return {}
    
    def update_password(self, req: UpdatePasswordRequest, authorization: str) -> dict:
        """更新当前登录用户的密码"""
        user_id = self._get_user_id_from_token(authorization)
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        # 校验原密码
        if not self.verify_password(req.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )
        # 校验新密码与确认密码一致
        if req.new_password != req.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码与确认密码不一致"
            )
        # 新密码不能与原密码相同
        if self.verify_password(req.new_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能与原密码相同"
            )
        user.hashed_password = self.get_password_hash(req.new_password)
        self.db.commit()
        return {}
    
    def logoff(self, authorization: str) -> dict:
        """注销当前登录用户账号（停用）"""
        user_id = self._get_user_id_from_token(authorization)
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号已注销"
            )
        user.is_active = False
        self.db.commit()
        # TODO: 可选：将当前 access token 加入黑名单（需 Redis），使其立即失效
        return {}
    
    def bind_phone(self, req: BindPhoneRequest, authorization: str) -> dict:
        """绑定手机号"""
        user_id = self._get_user_id_from_token(authorization)
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        # TODO: 校验短信验证码（从缓存中取手机号对应的验证码进行比对）
        # 校验新手机号是否已被其他用户绑定
        existing = self.get_user_by_phone(req.phone)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被绑定"
            )
        user.phone = req.phone
        self.db.commit()
        return {}