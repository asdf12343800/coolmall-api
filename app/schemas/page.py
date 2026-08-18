from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.goods import GoodsItem
from app.schemas.coupon import CouponInfoItem, CouponCondition
from app.schemas.goods import CommentItem
from app.schemas.banner import BannerItem
from app.schemas.category import CategoryItem


class GoodsDetailPageData(BaseModel):
    goods_info: GoodsItem = Field(..., alias="goodsInfo")
    coupon: List[CouponInfoItem] = Field(default_factory=list)
    comment: List[CommentItem] = Field(default_factory=list)


class UserCouponItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    title: str
    description: Optional[str] = None
    type: int
    amount: float
    num: int
    received_num: int = Field(..., alias="receivedNum")
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    status: int
    condition: CouponCondition
    use_status: int = Field(..., alias="useStatus")


class DefaultAddress(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    user_id: int = Field(..., alias="userId")
    contact: str
    phone: str
    province: str
    city: str
    district: str
    address: str
    is_default: bool = Field(..., alias="isDefault")


class ConfirmOrderPageData(BaseModel):
    user_coupon: List[UserCouponItem] = Field(default_factory=list, alias="userCoupon")
    coupon: List[CouponInfoItem] = Field(default_factory=list)
    default_address: Optional[DefaultAddress] = Field(default=None, alias="defaultAddress")


class HomePageData(BaseModel):
    coupon: List[CouponInfoItem] = Field(default_factory=list)
    banner: List[BannerItem] = Field(default_factory=list)
    goods: List[GoodsItem] = Field(default_factory=list)
    flash_sale: List[GoodsItem] = Field(default_factory=list, alias="flashSale")
    recommend: List[GoodsItem] = Field(default_factory=list)
    category_all: List[CategoryItem] = Field(default_factory=list, alias="categoryAll")
    category: List[CategoryItem] = Field(default_factory=list)
