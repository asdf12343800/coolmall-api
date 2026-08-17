from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order import (
    OrderUpdateRequest, RefundRequest, OrderPageRequest, OrderPageData,
    OrderCreateRequest, OrderCreateResponse, OrderCancelRequest, OrderCountData,
    LogisticsData, OrderItem,
)
from app.schemas.user import ApiResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/update", response_model=ApiResponse[dict])
def update_order(
    req: OrderUpdateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """根据ID修改订单"""
    service = OrderService(db)
    result = service.update_order(req, authorization)
    return ApiResponse[dict](data=result)


@router.post("/refund", response_model=ApiResponse[bool])
def refund_order(
    req: RefundRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """申请退款"""
    service = OrderService(db)
    result = service.refund(req, authorization)
    return ApiResponse[bool](data=result)


@router.post("/cancel", response_model=ApiResponse[bool])
def cancel_order(
    req: OrderCancelRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """取消订单"""
    service = OrderService(db)
    result = service.cancel_order(req, authorization)
    return ApiResponse[bool](data=result)


@router.post("/page", response_model=ApiResponse[OrderPageData])
def page_orders(
    req: OrderPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """分页查询当前用户的订单"""
    service = OrderService(db)
    data = service.page_orders(req, authorization)
    return ApiResponse[OrderPageData](data=data)


@router.post("/create", response_model=ApiResponse[OrderCreateResponse])
def create_order(
    req: OrderCreateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """创建订单"""
    service = OrderService(db)
    data = service.create_order(req, authorization)
    return ApiResponse[OrderCreateResponse](data=data)


@router.get("/userCount", response_model=ApiResponse[OrderCountData])
def user_count(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """用户订单统计"""
    service = OrderService(db)
    data = service.user_count(authorization)
    return ApiResponse[OrderCountData](data=data)


@router.get("/logistics", response_model=ApiResponse[LogisticsData])
def get_logistics(
    orderId: str = Query(..., description="订单ID"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """物流信息查询"""
    service = OrderService(db)
    data = service.logistics(int(orderId), authorization)
    return ApiResponse[LogisticsData](data=data)


@router.get("/info", response_model=ApiResponse[OrderItem])
def get_order_info(
    id: int = Query(..., description="订单ID"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """根据ID查询单个订单"""
    service = OrderService(db)
    data = service.get_order(id, authorization)
    return ApiResponse[OrderItem](data=data)


@router.get("/confirm", response_model=ApiResponse[bool])
def confirm_order(
    orderId: str = Query(..., description="订单ID"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """确认收货"""
    service = OrderService(db)
    result = service.confirm_order(int(orderId), authorization)
    return ApiResponse[bool](data=result)
