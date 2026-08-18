from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Comment(Base):
    __tablename__ = "goods_comments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, nullable=False, index=True)  # 订单号
    goods_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    content = Column(String, nullable=False)
    star_count = Column(Integer, nullable=False, default=5)
    pics = Column(String, nullable=True)  # JSON 数组字符串
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
