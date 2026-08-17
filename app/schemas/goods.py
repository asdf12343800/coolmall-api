from typing import Optional, List
from pydantic import BaseModel, Field


class GoodsSpecListRequest(BaseModel):
    goods_id: int = Field(..., alias="goodsId", description="商品ID")


class GoodsSpecItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    goods_id: int = Field(..., alias="goodsId")
    name: str
    price: float
    stock: int
    sort_num: int = Field(..., alias="sortNum")
    images: Optional[List[str]] = None
