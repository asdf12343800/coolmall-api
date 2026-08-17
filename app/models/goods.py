from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class GoodsSpec(Base):
    __tablename__ = "goods_specs"

    id = Column(Integer, primary_key=True, index=True)
    goods_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    sort_num = Column(Integer, default=0, nullable=False)
    images = Column(String, nullable=True)  # JSON 数组字符串，存图片URL列表
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
