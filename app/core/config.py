from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 注册/登录 token 过期时间（秒）
    ACCESS_TOKEN_EXPIRE: int = 2592000  # 30天
    REFRESH_TOKEN_EXPIRE: int = 7776000  # 90天
    USER_TYPE: str = "APP"

    # 支付宝配置
    ALIPAY_APP_ID: str = os.getenv("ALIPAY_APP_ID", "")
    # 应用私钥（PKCS8格式，不含-----BEGIN/END-----标记及换行）
    ALIPAY_APP_PRIVATE_KEY: str = os.getenv("ALIPAY_APP_PRIVATE_KEY", "")
    # 支付宝公钥（用于验签，不含-----BEGIN/END-----标记及换行）
    ALIPAY_PUBLIC_KEY: str = os.getenv("ALIPAY_PUBLIC_KEY", "")
    ALIPAY_SIGN_TYPE: str = os.getenv("ALIPAY_SIGN_TYPE", "RSA2")
    ALIPAY_CHARSET: str = "UTF-8"
    # 支付宝网关：正式环境 https://openapi.alipay.com/gateway.do
    ALIPAY_GATEWAY: str = os.getenv("ALIPAY_GATEWAY", "https://openapi.alipay.com/gateway.do")
    # 支付成功异步通知地址
    ALIPAY_NOTIFY_URL: str = os.getenv("ALIPAY_NOTIFY_URL", "")
    # 商品描述/标题
    ALIPAY_SUBJECT: str = os.getenv("ALIPAY_SUBJECT", "商品采购")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()