from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from app.schemas.address import Pagination


class ChatMessageContent(BaseModel):
    type: str = Field(..., description="消息内容类型，如 text")
    data: str = Field(..., description="消息内容")


class ChatMessageItem(BaseModel):
    id: int
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    user_id: int = Field(..., alias="userId")
    session_id: int = Field(..., alias="sessionId")
    content: Optional[ChatMessageContent] = None
    type: int
    status: Optional[int] = None
    nick_name: Optional[str] = Field(default=None, alias="nickName")
    avatar_url: Optional[str] = Field(default=None, alias="avatarUrl")
    admin_user_name: Optional[str] = Field(default=None, alias="adminUserName")
    admin_user_head_img: Optional[str] = Field(default=None, alias="adminUserHeadImg")


class ChatSessionResponse(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    user_id: int = Field(..., alias="userId")
    last_msg: Optional[ChatMessageItem] = Field(default=None, alias="lastMsg")
    admin_unread_count: int = Field(..., alias="adminUnreadCount")
    nick_name: Optional[str] = Field(default=None, alias="nickName")
    avatar_url: Optional[str] = Field(default=None, alias="avatarUrl")


class MsgReadRequest(BaseModel):
    msg_ids: List[int] = Field(..., alias="msgIds", description="消息ID数组")


class MsgPageRequest(BaseModel):
    session_id: int = Field(..., alias="sessionId", description="会话ID")
    order: str = Field(default="createTime", description="排序字段: createTime/updateTime")
    sort: Literal["asc", "desc"] = Field(default="desc", description="排序方向")
    page: int = Field(default=1, description="页码", ge=1)
    size: int = Field(default=20, description="每页条数", ge=1)


class MsgPageData(BaseModel):
    list: List[ChatMessageItem]
    pagination: Pagination
