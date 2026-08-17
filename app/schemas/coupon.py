from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import ApiResponse


class CouponReceiveResponse(BaseModel):
    empty: bool = Field(default=True, description="是否为空")
