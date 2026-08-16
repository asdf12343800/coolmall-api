from typing import Optional
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
