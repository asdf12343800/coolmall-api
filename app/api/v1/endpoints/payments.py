from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.payment import AlipayAppPayRequest
from app.schemas.user import ApiResponse
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/alipayAppPay", response_model=ApiResponse[str])
def alipay_app_pay(
    req: AlipayAppPayRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """支付宝APP支付"""
    service = PaymentService(db)
    order_str = service.alipay_app_pay(req, authorization)
    return ApiResponse[str](data=order_str)
