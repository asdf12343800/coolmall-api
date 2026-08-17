from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    path = Column(String, nullable=True)
    pic = Column(String, nullable=True)
    sort_num = Column(Integer, default=0, nullable=False)
    status = Column(Integer, default=1, nullable=False)  # 1=启用 0=禁用
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
