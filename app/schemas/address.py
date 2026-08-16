from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.user import ApiResponse


class AddressUpdateRequest(BaseModel):
    id: int = Field(..., description="地址ID")
    contact: str = Field(..., description="联系人")
    phone: str = Field(..., description="联系电话")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    district: str = Field(..., description="区/县")
    address: str = Field(..., description="详细地址")
    is_default: bool = Field(..., alias="isDefault", description="是否默认地址")


class AddressResponse(BaseModel):
    id: int
    contact: str
    phone: str
    province: str
    city: str
    district: str
    address: str
    is_default: bool = Field(..., alias="isDefault")

    model_config = {"from_attributes": True}


class AddressPageRequest(BaseModel):
    page: int = Field(..., description="页码", ge=1)
    size: int = Field(..., description="每页条数", ge=1)
    sort: str = Field(default="desc", description="排序方向: asc/desc")
    order: str = Field(default="updateTime", description="排序字段")


class AddressItem(BaseModel):
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


class Pagination(BaseModel):
    total: int
    size: int
    page: int


class AddressPageData(BaseModel):
    list: List[AddressItem]
    pagination: Pagination
