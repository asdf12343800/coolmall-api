from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatSessionResponse, MsgReadRequest, MsgPageRequest, MsgPageData
from app.schemas.user import ApiResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/session/create", response_model=ApiResponse[ChatSessionResponse])
def create_session(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """创建客服会话"""
    service = ChatService(db)
    data = service.create_session(authorization)
    return ApiResponse[ChatSessionResponse](data=data)


@router.get("/session/detail", response_model=ApiResponse[ChatSessionResponse])
def get_session_detail(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """会话详情"""
    service = ChatService(db)
    data = service.get_session_detail(authorization)
    return ApiResponse[ChatSessionResponse](data=data)


@router.post("/msg/read", response_model=ApiResponse[bool])
def read_messages(
    req: MsgReadRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """标记消息为已读"""
    service = ChatService(db)
    data = service.read_messages(req, authorization)
    return ApiResponse[bool](data=data)


@router.post("/msg/page", response_model=ApiResponse[MsgPageData])
def page_messages(
    req: MsgPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """分页查询消息"""
    service = ChatService(db)
    data = service.page_messages(req, authorization)
    return ApiResponse[MsgPageData](data=data)
