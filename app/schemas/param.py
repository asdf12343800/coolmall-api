from pydantic import BaseModel, Field


class ParamItem(BaseModel):
    key: str
    content: str = Field(..., description="参数内容")
