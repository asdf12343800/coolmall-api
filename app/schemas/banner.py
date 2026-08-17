from typing import Optional
from pydantic import BaseModel, Field


class BannerItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    description: Optional[str] = None
    path: Optional[str] = None
    pic: Optional[str] = None
    sort_num: int = Field(..., alias="sortNum")
    status: int
