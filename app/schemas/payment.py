from pydantic import BaseModel, Field
from app.schemas.user import ApiResponse


class AlipayAppPayRequest(BaseModel):
    order_id: int = Field(..., alias="orderId", description="订单ID")


class AlipayAppPayData(BaseModel):
    # 支付宝客户端调起支付所需的订单字符串
    order_str: str = Field(..., alias="orderStr", description="支付宝app支付订单字符串")


class AlipayAppPayResponse(BaseModel):
    code: int = Field(default=1000, description="响应码，1000表示成功")
    data: str = Field(..., description="支付宝app支付订单字符串")
    message: str = Field(default="success", description="响应消息")
