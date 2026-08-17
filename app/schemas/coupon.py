from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.address import Pagination


class CouponCondition(BaseModel):
    full_amount: Optional[float] = Field(default=None, alias="fullAmount")


class CouponItem(BaseModel):
    id: int
    title: str
    type: int = Field(..., description="优惠券类型: 0=满减券")
    amount: float = Field(..., description="优惠金额")
    num: int = Field(..., description="发行总量")
    received_num: int = Field(..., alias="receivedNum", description="已领取数量")
    description: Optional[str] = None
    condition: CouponCondition
    use_status: int = Field(..., alias="useStatus", description="使用状态: 0=未使用 1=已使用 2=已过期")
    status: int = Field(..., description="优惠券状态: 1=有效 0=失效")
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")


class CouponPageRequest(BaseModel):
    page: int = Field(default=1, description="页码", ge=1)
    size: int = Field(default=20, description="每页条数", ge=1)
    sort: str = Field(default="desc", description="排序方向: asc/desc")
    order: str = Field(default="updateTime", description="排序字段")


class CouponPageData(BaseModel):
    list: list[CouponItem]
    pagination: Pagination


class CouponReceiveResponse(BaseModel):
    empty: bool = Field(default=True, description="是否为空")


class CouponUserItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    user_id: int = Field(..., alias="userId")
    coupon_id: int = Field(..., alias="couponId")
    status: int
    use_time: Optional[str] = Field(default=None, alias="useTime")


class CouponInfoItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: int = Field(..., description="优惠券类型: 0=满减券")
    amount: float = Field(..., description="优惠金额")
    num: int = Field(..., description="发行总量")
    received_num: int = Field(..., alias="receivedNum", description="已领取数量")
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    status: int = Field(..., description="优惠券状态: 1=有效 0=失效")
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    condition: CouponCondition


class CouponInfoPageData(BaseModel):
    list: list[CouponInfoItem]
    pagination: Pagination
