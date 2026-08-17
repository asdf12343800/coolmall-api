from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.schemas.order import OrderUpdateRequest, RefundRequest
from app.services.user_service import UserService


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    """将ISO 8601字符串解析为datetime，失败返回None"""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt
    except Exception:
        return None


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def update_order(self, req: OrderUpdateRequest, authorization: str) -> dict:
        """根据ID修改订单"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        if req.id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单ID不能为空",
            )
        order = self.db.query(Order).filter(Order.id == req.id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在",
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作该订单",
            )

        if req.title is not None:
            order.title = req.title
        if req.pay_type is not None:
            order.pay_type = req.pay_type
        if req.pay_time is not None:
            order.pay_time = _parse_dt(req.pay_time)
        if req.order_num is not None:
            order.order_no = req.order_num
        if req.status is not None:
            order.status = req.status
        if req.price is not None:
            order.price = req.price
        if req.discount_price is not None:
            order.discount_price = req.discount_price
        if req.discount_source is not None:
            order.discount_source = req.discount_source.model_dump(by_alias=True, exclude_none=True)
        if req.address is not None:
            order.address_info = req.address.model_dump(by_alias=True, exclude_none=True)
        if req.logistics is not None:
            order.logistics = req.logistics.model_dump(by_alias=True, exclude_none=True)
        if req.refund is not None:
            order.refund_info = req.refund.model_dump(by_alias=True, exclude_none=True)
        if req.refund_status is not None:
            order.refund_status = req.refund_status
        if req.refund_apply_time is not None:
            order.refund_apply_time = _parse_dt(req.refund_apply_time)
        if req.remark is not None:
            order.remark = req.remark
        if req.close_remark is not None:
            order.close_remark = req.close_remark
        if req.invoice is not None:
            order.invoice = req.invoice
        if req.wx_type is not None:
            order.wx_type = req.wx_type
        if req.goods_list is not None:
            order.goods_list = [g.model_dump(by_alias=True, exclude_none=True) for g in req.goods_list]

        self.db.commit()
        return {}

    def refund(self, req: RefundRequest, authorization: str) -> bool:
        """申请退款"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        order = self.db.query(Order).filter(Order.id == req.order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在",
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作该订单",
            )

        now = datetime.now()
        order.refund_status = 1  # 退款申请中
        order.refund_apply_time = now
        order.refund_info = {
            "orderNum": order.order_no,
            "reason": req.reason,
            "applyTime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "status": 1,
        }
        self.db.commit()
        return True
