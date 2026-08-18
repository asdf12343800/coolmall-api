from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Goods(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, nullable=True, index=True)
    title = Column(String, nullable=False)
    sub_title = Column(String, nullable=True)
    main_pic = Column(String, nullable=True)
    pics = Column(String, nullable=True)  # JSON 数组字符串
    price = Column(Numeric(10, 2), nullable=False, default=0)
    sold = Column(Integer, nullable=False, default=0)
    content = Column(String, nullable=True)  # 富文本/HTML
    content_pics = Column(String, nullable=True)  # JSON 数组字符串
    recommend = Column(Boolean, default=False, nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    status = Column(Integer, default=1, nullable=False)  # 1=上架 0=下架
    sort_num = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
