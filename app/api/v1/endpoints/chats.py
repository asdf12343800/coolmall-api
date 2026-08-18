from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatSessionResponse
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
