import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.schemas.chat import ChatSessionResponse, ChatMessageItem, ChatMessageContent, MsgReadRequest
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


class ChatService:
    def __init__(self, db: Session):
        self.db = db

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
            last_msg = ChatMessageItem(
                id=last_msg_row.id,
                create_time=_fmt_std(last_msg_row.created_at),
                update_time=_fmt_std(last_msg_row.updated_at) if last_msg_row.updated_at else _fmt_std(last_msg_row.created_at),
                user_id=last_msg_row.user_id,
                session_id=last_msg_row.session_id,
                content=_parse_content(last_msg_row.content),
                type=last_msg_row.type,
                status=last_msg_row.status,
                nick_name=nick_name or "",
                avatar_url=avatar_url or "",
                admin_user_name="",
                admin_user_head_img="",
            )

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
