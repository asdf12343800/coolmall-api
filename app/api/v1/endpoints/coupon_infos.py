from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.coupon import CouponPageRequest, CouponInfoPageData
from app.schemas.user import ApiResponse
from app.services.coupon_service import CouponService

router = APIRouter()


@router.post("/page", response_model=ApiResponse[CouponInfoPageData])
def page_coupon_infos(
    req: CouponPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """分页查询优惠券主表"""
    service = CouponService(db)
    data = service.page_coupon_infos(req, authorization)
    return ApiResponse[CouponInfoPageData](data=data)
