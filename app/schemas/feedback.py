from typing import List
from pydantic import BaseModel, Field


class FeedbackSubmitRequest(BaseModel):
    images: List[str] = Field(..., description="图片URL数组")
    contact: str = Field(..., description="联系方式")
    type: int = Field(..., description="反馈类型")
    content: str = Field(..., description="反馈内容")
