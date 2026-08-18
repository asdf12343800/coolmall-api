from pydantic import BaseModel, Field


class CosCredentials(BaseModel):
    tmp_secret_id: str = Field(..., alias="tmpSecretId", description="临时 SecretId")
    tmp_secret_key: str = Field(..., alias="tmpSecretKey", description="临时 SecretKey")
    session_token: str = Field(..., alias="sessionToken", description="会话 Token")


class UploadData(BaseModel):
    credentials: CosCredentials
    request_id: str = Field(..., alias="requestId", description="请求ID")
    expiration: str = Field(..., description="过期时间(ISO格式)")
    start_time: int = Field(..., alias="startTime", description="开始时间(秒级时间戳)")
    expired_time: int = Field(..., alias="expiredTime", description="过期时间(秒级时间戳)")
    url: str = Field(..., description="COS 桶访问地址")
