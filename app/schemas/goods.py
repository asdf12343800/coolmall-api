from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.address import Pagination


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


class SearchKeywordItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    name: str
    sort_num: int = Field(..., alias="sortNum")


class GoodsPageRequest(BaseModel):
    page: int = Field(..., description="页码", ge=1)
    size: int = Field(..., description="每页条数", ge=1)


class GoodsItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    type_id: int = Field(..., alias="typeId")
    title: str
    sub_title: Optional[str] = Field(default=None, alias="subTitle")
    main_pic: Optional[str] = Field(default=None, alias="mainPic")
    pics: Optional[List[str]] = None
    price: float
    sold: int
    content: Optional[str] = None
    content_pics: Optional[List[str]] = Field(default=None, alias="contentPics")
    recommend: bool
    featured: bool
    status: int
    sort_num: int = Field(..., alias="sortNum")
    specs: Optional[List] = None


class GoodsPageData(BaseModel):
    list: list[GoodsItem]
    pagination: Pagination
