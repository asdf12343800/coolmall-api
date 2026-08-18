from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Complain(Base):
    __tablename__ = "complains"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    target_type = Column(Integer, nullable=True)  # 1=商品 2=订单 3=用户 等
    target_id = Column(Integer, nullable=True)
    images = Column(Text, nullable=True)  # JSON: list of image URLs
    contact = Column(String, nullable=True)
    type = Column(Integer, nullable=True)
    content = Column(Text, nullable=True)
    status = Column(Integer, default=0, nullable=False)  # 0=待处理 1=已处理
    handler_id = Column(Integer, nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
