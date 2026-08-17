from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order import OrderUpdateRequest
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
