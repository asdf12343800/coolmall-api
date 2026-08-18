from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    admin_unread_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 会话所属用户
    content = Column(Text, nullable=True)  # JSON: {"type": "text", "data": "..."}
    type = Column(Integer, default=0, nullable=False)  # 0=用户消息 1=客服消息
    status = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
