from typing import Optional
from pydantic import BaseModel, Field


class CategoryItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    name: str
    parent_id: Optional[int] = Field(default=None, alias="parentId")
    sort_num: int = Field(..., alias="sortNum")
    pic: Optional[str] = None
    status: int
