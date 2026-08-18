from typing import List, Optional
from pydantic import BaseModel, Field


class ComplainSubmitRequest(BaseModel):
    target_type: Optional[int] = Field(default=None, alias="targetType", description="举报目标类型: 1=商品 2=订单 3=用户")
    target_id: Optional[int] = Field(default=None, alias="targetId", description="举报目标ID")
    images: Optional[List[str]] = Field(default=None, description="图片URL数组")
    contact: Optional[str] = Field(default=None, description="联系方式")
    type: Optional[int] = Field(default=None, description="投诉类型")
    content: Optional[str] = Field(default=None, description="投诉内容")
