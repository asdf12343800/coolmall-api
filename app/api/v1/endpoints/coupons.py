from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import ApiResponse
from app.services.coupon_service import CouponService

router = APIRouter()


@router.post("/receive", response_model=ApiResponse[bool])
def receive_coupon(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """领取优惠券"""
    service = CouponService(db)
    result = service.receive(authorization)
    return ApiResponse[bool](data=result)
