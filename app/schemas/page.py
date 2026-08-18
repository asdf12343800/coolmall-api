from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.goods import GoodsItem
from app.schemas.coupon import CouponInfoItem
from app.schemas.goods import CommentItem


class GoodsDetailPageData(BaseModel):
    goods_info: GoodsItem = Field(..., alias="goodsInfo")
    coupon: List[CouponInfoItem] = Field(default_factory=list)
    comment: List[CommentItem] = Field(default_factory=list)
