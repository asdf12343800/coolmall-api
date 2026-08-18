import json
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.address import Pagination


class FeedbackSubmitRequest(BaseModel):
    images: List[str] = Field(..., description="图片URL数组")
    contact: str = Field(..., description="联系方式")
    type: int = Field(..., description="反馈类型")
    content: str = Field(..., description="反馈内容")


class FeedbackItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    user_id: int = Field(..., alias="userId")
    contact: Optional[str] = None
    type: int
    content: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    status: int
    handler_id: Optional[int] = Field(default=None, alias="handlerId")
    remark: Optional[str] = None


class FeedbackPageRequest(BaseModel):
    page: int = Field(default=1, description="页码", ge=1)
    size: int = Field(default=20, description="每页条数", ge=1)


class FeedbackPageData(BaseModel):
    list: List[FeedbackItem]
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
