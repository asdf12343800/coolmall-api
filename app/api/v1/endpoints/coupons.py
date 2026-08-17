from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.coupon import CouponPageRequest, CouponPageData, CouponUserItem
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


@router.post("/page", response_model=ApiResponse[CouponPageData])
def page_coupons(
    req: CouponPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """分页查询当前用户已领取的优惠券"""
    service = CouponService(db)
    data = service.page_coupons(req, authorization)
    return ApiResponse[CouponPageData](data=data)


@router.post("/list", response_model=ApiResponse[List[CouponUserItem]])
def list_coupons(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """查询当前用户的所有优惠券领取记录"""
    service = CouponService(db)
    data = service.list_coupons(authorization)
    return ApiResponse[List[CouponUserItem]](data=data)
