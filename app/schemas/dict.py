from typing import Optional, List
from pydantic import BaseModel, Field


class DictDataRequest(BaseModel):
    types: List[str] = Field(..., description="字典类型名数组")


class DictDataItem(BaseModel):
    type_id: int = Field(..., alias="typeId")
    parent_id: Optional[int] = Field(default=None, alias="parentId")
    name: str
    id: int
    value: Optional[int] = None
