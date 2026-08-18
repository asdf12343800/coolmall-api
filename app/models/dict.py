from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class DictType(Base):
    __tablename__ = "dict_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, unique=True, nullable=False, index=True)  # 如 orderCancelReason
    name = Column(String, nullable=True)  # 显示名
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DictData(Base):
    __tablename__ = "dict_data"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, nullable=False, index=True)
    parent_id = Column(Integer, nullable=True)
    name = Column(String, nullable=False)
    value = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
