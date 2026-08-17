from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    order_no = Column(String, unique=True, index=True, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Integer, default=0, nullable=False)
    pay_type = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 订单更新相关字段
    title = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    discount_price = Column(Numeric(10, 2), nullable=True)
    pay_time = Column(DateTime(timezone=True), nullable=True)
    remark = Column(String, nullable=True)
    close_remark = Column(String, nullable=True)
    invoice = Column(Integer, nullable=True)
    wx_type = Column(Integer, nullable=True)
    refund_status = Column(Integer, nullable=True)
    refund_apply_time = Column(DateTime(timezone=True), nullable=True)

    # 嵌套对象以JSON存储
    discount_source = Column(JSON, nullable=True)
    address_info = Column(JSON, nullable=True)
    logistics = Column(JSON, nullable=True)
    refund_info = Column(JSON, nullable=True)
    goods_list = Column(JSON, nullable=True)
