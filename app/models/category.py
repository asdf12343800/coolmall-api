from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, nullable=True, index=True)
    sort_num = Column(Integer, default=0, nullable=False)
    pic = Column(String, nullable=True)
    status = Column(Integer, default=1, nullable=False)  # 1=启用 0=禁用
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
