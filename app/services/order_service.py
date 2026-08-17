import time
import random
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.address import Address
from app.schemas.order import (
    OrderUpdateRequest, RefundRequest, OrderPageRequest, OrderPageData, OrderItem,
    OrderCreateRequest, OrderCreateResponse, OrderCancelRequest, OrderCountData,
    LogisticsData,
)
from app.schemas.address import Pagination
from app.services.user_service import UserService


def _fmt(dt):
    """格式化日期时间为字符串，None返回空串"""
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _fmt_opt(dt):
    """格式化日期时间，None返回None"""
    if not dt:
        return None
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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

    def cancel_order(self, req: OrderCancelRequest, authorization: str) -> bool:
        """取消订单"""
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

        order.status = 4  # 已取消
        order.close_remark = req.remark
        self.db.commit()
        return True

    def page_orders(self, req: OrderPageRequest, authorization: str) -> OrderPageData:
        """分页查询当前用户的订单"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)
        query = self.db.query(Order).filter(Order.user_id == user_id)
        order_map = {
            "updateTime": Order.updated_at,
            "createTime": Order.created_at,
            "id": Order.id,
        }
        sort_col = order_map.get(req.order, Order.updated_at)
        if req.sort == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())
        total = query.count()
        items = query.offset((req.page - 1) * req.size).limit(req.size).all()
        return OrderPageData(
            list=[self._to_item(o) for o in items],
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )

    def _to_item(self, order: Order) -> OrderItem:
        """将Order模型转换为OrderItem响应"""
        return OrderItem(
            id=order.id,
            create_time=_fmt(order.created_at),
            update_time=_fmt(order.updated_at) if order.updated_at else _fmt(order.created_at),
            user_id=order.user_id,
            title=order.title,
            pay_type=order.pay_type,
            pay_time=_fmt_opt(order.pay_time),
            order_num=order.order_no,
            status=order.status,
            price=float(order.price) if order.price is not None else float(order.total_amount),
            discount_price=float(order.discount_price) if order.discount_price is not None else None,
            discount_source=order.discount_source,
            address=order.address_info,
            logistics=order.logistics,
            refund=order.refund_info,
            refund_status=order.refund_status,
            refund_apply_time=_fmt_opt(order.refund_apply_time),
            remark=order.remark,
            close_remark=order.close_remark,
            invoice=order.invoice,
            wx_type=order.wx_type,
            goods_list=order.goods_list,
        )

    def create_order(self, req: OrderCreateRequest, authorization: str) -> OrderCreateResponse:
        """创建订单"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)
        data = req.data

        # 校验收货地址
        address = self.db.query(Address).filter(
            Address.id == data.address_id,
            Address.user_id == user_id,
        ).first()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收货地址不存在",
            )

        # 生成订单号: U + 时间戳 + 随机数
        order_no = f"U{int(time.time())}{random.randint(10000, 99999)}"

        # 计算订单总价 = sum(spec.price * count)
        total = 0.0
        goods_list_json = []
        for item in data.goods_list:
            unit_price = item.spec.price or 0
            total += unit_price * item.count
            goods_list_json.append(item.model_dump(by_alias=True, exclude_none=True))

        # 序列化收货地址快照
        address_json = {
            "id": address.id,
            "userId": address.user_id,
            "contact": address.contact,
            "phone": address.phone,
            "province": address.province,
            "city": address.city,
            "district": address.district,
            "address": address.address,
            "isDefault": address.is_default,
        }

        order = Order(
            user_id=user_id,
            order_no=order_no,
            total_amount=total,
            status=0,
            title=data.title,
            price=total,
            remark=data.remark,
            address_info=address_json,
            goods_list=goods_list_json,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return OrderCreateResponse(id=order.id)

    def user_count(self, authorization: str) -> OrderCountData:
        """用户订单统计"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        pending_payment = self.db.query(Order).filter(
            Order.user_id == user_id, Order.status == 0,
        ).count()
        pending_shipment = self.db.query(Order).filter(
            Order.user_id == user_id, Order.status == 1,
        ).count()
        closed = self.db.query(Order).filter(
            Order.user_id == user_id, Order.status == 4,
        ).count()

        return OrderCountData(
            closed=closed,
            pending_shipment=pending_shipment,
            pending_payment=pending_payment,
        )

    def logistics(self, order_id: int, authorization: str) -> LogisticsData:
        """查询订单物流信息"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        order = self.db.query(Order).filter(Order.id == order_id).first()
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

        # 优先从订单的 logistics JSON 字段读取物流信息
        logistics = order.logistics
        if logistics and isinstance(logistics, dict):
            try:
                return LogisticsData(**logistics)
            except Exception:
                pass

        # 没有物流数据，返回默认占位数据（模拟揽收状态）
        now_str = _fmt(datetime.now())
        return LogisticsData(
            number=logistics.get("number", "") if isinstance(logistics, dict) else "",
            type="YUNDA",
            list=[
                LogisticsTraceItem(
                    time=now_str,
                    status="【商家】订单已下单，等待快递员揽收",
                )
            ],
            deliverystatus="1",
            issign="0",
            expName="韵达快递",
            expSite="www.yundaex.com",
            expPhone="95546",
            logo="https://img3.fegine.com/express/yd.jpg",
            courier="",
            courierPhone="",
            updateTime=now_str,
            takeTime="0小时0分",
        )

    def get_order(self, order_id: int, authorization: str) -> OrderItem:
        """根据ID查询单个订单"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在",
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看该订单",
            )
        return self._to_item(order)

    def confirm_order(self, order_id: int, authorization: str) -> bool:
        """确认收货"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        order = self.db.query(Order).filter(Order.id == order_id).first()
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

        order.status = 3  # 已完成（已收货）
        self.db.commit()
        return True
