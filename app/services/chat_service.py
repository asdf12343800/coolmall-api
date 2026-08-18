import json
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.schemas.chat import (
    ChatSessionResponse,
    ChatMessageItem,
    ChatMessageContent,
    MsgReadRequest,
    MsgPageRequest,
    MsgPageData,
)
from app.schemas.address import Pagination
from app.services.user_service import UserService


def _fmt_std(dt):
    """格式化日期时间为标准字符串，None 返回空串"""
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _parse_content(content_raw):
    """解析 content 字段为 ChatMessageContent 或 None"""
    if not content_raw:
        return None
    try:
        data = json.loads(content_raw)
        if isinstance(data, dict):
            return ChatMessageContent(**data)
    except Exception:
        return None
    return None


_ORDER_FIELD_MAP = {
    "createTime": ChatMessage.created_at,
    "updateTime": ChatMessage.updated_at,
    "id": ChatMessage.id,
}


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def _build_message_item(self, row: ChatMessage, nick_name: str | None, avatar_url: str | None) -> ChatMessageItem:
        """将 ChatMessage ORM 行转为 ChatMessageItem；按消息类型区分用户/客服字段"""
        is_user = row.type == 0
        return ChatMessageItem(
            id=row.id,
            create_time=_fmt_std(row.created_at),
            update_time=_fmt_std(row.updated_at) if row.updated_at else _fmt_std(row.created_at),
            user_id=row.user_id,
            session_id=row.session_id,
            content=_parse_content(row.content),
            type=row.type,
            status=row.status,
            nick_name=nick_name if is_user else None,
            avatar_url=avatar_url if is_user else None,
            admin_user_name=None if is_user else None,
            admin_user_head_img=None if is_user else None,
        )

    def _build_session_response(self, session: ChatSession, user: User | None) -> ChatSessionResponse:
        """根据会话和用户构建会话响应（含最后一条消息）"""
        last_msg_row = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.id.desc())
            .first()
        )

        nick_name = user.username if user else None
        avatar_url = user.avatar if user else None

        last_msg = None
        if last_msg_row:
            last_msg = self._build_message_item(last_msg_row, nick_name, avatar_url)

        return ChatSessionResponse(
            id=session.id,
            create_time=_fmt_std(session.created_at),
            update_time=_fmt_std(session.updated_at) if session.updated_at else _fmt_std(session.created_at),
            user_id=session.user_id,
            last_msg=last_msg,
            admin_unread_count=session.admin_unread_count,
            nick_name=nick_name,
            avatar_url=avatar_url,
        )

    def _get_active_session(self, user_id: int) -> ChatSession | None:
        """查找该用户的已有会话（取最新一条）"""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.id.desc())
            .first()
        )

    def _get_owned_session(self, session_id: int, user_id: int) -> ChatSession:
        """获取会话并校验归属，不存在或越权抛 404/403"""
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在",
            )
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问该会话",
            )
        return session

    def create_session(self, authorization: str) -> ChatSessionResponse:
        """创建（或获取已有的）客服会话"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        session = self._get_active_session(user_id)
        if not session:
            session = ChatSession(user_id=user_id, admin_unread_count=0)
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

        user = self.db.query(User).filter(User.id == user_id).first()
        return self._build_session_response(session, user)

    def get_session_detail(self, authorization: str) -> Optional[ChatSessionResponse]:
        """获取当前用户的会话详情，无会话返回 None"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        session = self._get_active_session(user_id)
        if not session:
            return None

        user = self.db.query(User).filter(User.id == user_id).first()
        return self._build_session_response(session, user)

    def read_messages(self, req: MsgReadRequest, authorization: str) -> bool:
        """标记消息为已读（仅限当前用户的消息）"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        if not req.msg_ids:
            return True

        rows = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.id.in_(req.msg_ids), ChatMessage.user_id == user_id)
            .all()
        )
        for m in rows:
            m.status = 1
        self.db.commit()
        return True

    def page_messages(self, req: MsgPageRequest, authorization: str) -> MsgPageData:
        """分页查询指定会话的消息列表，越权校验"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        # 归属校验
        self._get_owned_session(req.session_id, user_id)

        # 安全排序字段映射
        order_col = _ORDER_FIELD_MAP.get(req.order, ChatMessage.created_at)
        order_expr = order_col.desc() if req.sort == "desc" else order_col.asc()

        total = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == req.session_id)
            .count()
        )

        offset = (req.page - 1) * req.size
        rows = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == req.session_id)
            .order_by(order_expr)
            .offset(offset)
            .limit(req.size)
            .all()
        )

        # 用户展示信息（type=0 消息用）
        user = self.db.query(User).filter(User.id == user_id).first()
        nick_name = user.username if user else None
        avatar_url = user.avatar if user else None

        items = [self._build_message_item(r, nick_name, avatar_url) for r in rows]
        return MsgPageData(
            list=items,
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )

    def get_unread_count(self, authorization: str) -> int:
        """获取当前用户未读的客服消息数（type=1 且 status 非 1）"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        return (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.type == 1,
                or_(ChatMessage.status == 0, ChatMessage.status.is_(None)),
            )
            .count()
        )
