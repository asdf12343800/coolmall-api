from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order import (
    OrderUpdateRequest, RefundRequest, OrderPageRequest, OrderPageData,
    OrderCreateRequest, OrderCreateResponse,
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
