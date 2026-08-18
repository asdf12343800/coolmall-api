import json
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.address import Pagination


class ComplainSubmitRequest(BaseModel):
    target_type: Optional[int] = Field(default=None, alias="targetType", description="举报目标类型: 1=商品 2=订单 3=用户")
    target_id: Optional[int] = Field(default=None, alias="targetId", description="举报目标ID")
    images: Optional[List[str]] = Field(default=None, description="图片URL数组")
    contact: Optional[str] = Field(default=None, description="联系方式")
    type: Optional[int] = Field(default=None, description="投诉类型")
    content: Optional[str] = Field(default=None, description="投诉内容")


class ComplainItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    user_id: int = Field(..., alias="userId")
    target_type: Optional[int] = Field(default=None, alias="targetType")
    target_id: Optional[int] = Field(default=None, alias="targetId")
    contact: Optional[str] = None
    type: Optional[int] = None
    content: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    status: int
    handler_id: Optional[int] = Field(default=None, alias="handlerId")
    remark: Optional[str] = None


class ComplainPageRequest(BaseModel):
    page: int = Field(default=1, description="页码", ge=1)
    size: int = Field(default=20, description="每页条数", ge=1)


class ComplainPageData(BaseModel):
    list: List[ComplainItem]
    pagination: Pagination


def parse_images(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []
